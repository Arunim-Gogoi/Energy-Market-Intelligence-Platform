import os
import glob
import requests
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

_MODEL = SentenceTransformer("all-MiniLM-L6-v2")


def _chunk(text, size=500, overlap=50):
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunks.append(" ".join(words[i:i + size]))
        i += size - overlap
    return chunks


def build_index(docs_dir="docs"):
    texts, meta = [], []
    for path in glob.glob(os.path.join(docs_dir, "*.txt")):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for chunk in _chunk(content):
            texts.append(chunk)
            meta.append(os.path.basename(path))

    if not texts:
        return {"index": None, "texts": [], "meta": []}

    embeddings = _MODEL.encode(texts, normalize_embeddings=True)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(np.array(embeddings, dtype="float32"))
    return {"index": index, "texts": texts, "meta": meta}


def _retrieve(query, store, k=4, min_score=0.25):
    """Return only chunks that actually resemble the query — a low-relevance local doc
    shouldn't get pulled in just because it's the 'least bad' of 3 unrelated files."""
    if store["index"] is None:
        return [], []
    q_emb = _MODEL.encode([query], normalize_embeddings=True)
    scores, idx = store["index"].search(np.array(q_emb, dtype="float32"), k)
    hits, sources = [], []
    for score, i in zip(scores[0], idx[0]):
        if i != -1 and score >= min_score:
            hits.append(store["texts"][i])
            sources.append(store["meta"][i])
    return hits, sources


def fetch_live_context(query, max_results=3):
    """Optional live-web augmentation via Tavily's free tier. Returns ([], []) if no key set
    or the call fails — the app should degrade to static-docs-only RAG in that case."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return [], []
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
            },
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except requests.RequestException:
        return [], []

    snippets = [r.get("content", "")[:600] for r in results if r.get("content")]
    sources = [r.get("url", "unknown") for r in results if r.get("content")]
    return snippets, sources


def answer_question(query, store):
    hits, doc_sources = _retrieve(query, store)
    live_hits, live_sources = fetch_live_context(query)

    all_hits = hits + live_hits
    all_sources = doc_sources + [f"🌐 {s}" for s in live_sources]

    if not all_hits:
        return "No documents indexed yet — add .txt files to /docs.", []

    context = "\n\n".join(all_hits)
    groq_key = os.environ.get("GROQ_API_KEY")

    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            system_msg = (
                "You are an energy market analyst assistant. Answer using only the provided "
                "context. Cite which source each fact comes from. If both static reference "
                "material and live web snippets are present, prefer the live snippets for "
                "anything time-sensitive (prices, current events, recent figures) and say so."
            )
            resp = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
                ],
                temperature=0.2,
            )
            return resp.choices[0].message.content, sorted(set(all_sources))
        except Exception:
            pass  # fall through to extractive fallback below

    # Extractive fallback — used with no key, or if the Groq call above failed
    snippet = all_hits[0][:600]
    return f"(extractive fallback — set GROQ_API_KEY for generated answers)\n\n{snippet}...", sorted(set(all_sources))
