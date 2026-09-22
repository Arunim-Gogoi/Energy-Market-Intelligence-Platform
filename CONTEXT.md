# Energy Market Intelligence Platform — Context Capsule

## Why this exists
Rystad Energy is recruiting on campus but the placement office never forwarded the JD or
even the post name. Rystad's actual India campus role (confirmed via public listings,
Sept 2026) is **"Analyst (Data & Research)"** — Bengaluru, Analysis department. Core duties:
maintain energy databases, analyze oil/gas/renewables/power market data, build forecasting
models, write analyst reports/narratives. Skills called out: Excel, Python, SQL, C.

## Project goal
Build an "Energy Market Intelligence Platform" demo in ~8 hours that mirrors what an
Analyst (Data & Research) does day to day — ingest energy data, generate trend insights,
answer questions via RAG — positioned as a mini Rystad-style analyst tool.

## Constraints
- ~8 hour build budget, single session
- No paid API budget — default to free tiers only (Groq free tier for generation,
  sentence-transformers + FAISS run locally for embeddings/retrieval, no API key needed)
- Must be demo-able: deployed link + short clip, not just local code

## Architecture decisions
- **Data**: Our World in Data energy dataset (`owid-energy-data.csv`) — free, no auth,
  oil/gas/coal/renewables/demand by country & year, back to the 1900s
- **Frontend**: Streamlit — fastest path to a deployed, interactive demo
- **Insight layer**: pandas-computed period deltas + templated narrative; optional LLM
  polish via Groq (`GROQ_API_KEY`) if set, falls back gracefully without it
- **RAG**: local sentence-transformers embeddings (`all-MiniLM-L6-v2`) + FAISS flat index
  over `/docs`; generation via Groq if key present, else extractive fallback (works with
  zero API keys)
- **Deploy target**: Streamlit Community Cloud (free, fast to spin up)

## Files
- `app.py` — Streamlit entrypoint (dashboard + insight + RAG UI)
- `data_loader.py` — cached OWID data fetch
- `rag_utils.py` — chunk / embed / index / answer
- `docs/*.txt` — seed corpus (oil market, renewables growth, demand outlook) — **swap
  these for real IEA/EIA/Rystad-public-commentary excerpts if time allows**, they're
  placeholders written to make the RAG demo work out of the box
- `requirements.txt`

## Status
- [x] Scaffold created (app.py, data_loader.py, rag_utils.py, requirements.txt, seed /docs)
- [ ] Verified `pip install -r requirements.txt && streamlit run app.py` runs locally
- [ ] Dashboard renders with real OWID data for a few countries
- [ ] Insight narrative reads sensibly across different year ranges
- [ ] RAG Q&A tested with 3-4 real questions
- [ ] Rystad-style theming pass (navy/cyan already stubbed in app.py)
- [ ] Deployed to Streamlit Community Cloud
- [ ] Demo clip recorded (30-60s)
- [ ] Resume bullet finalized

## Resume bullet (draft)
"Built an Energy Market Intelligence Platform analyzing global oil, gas and renewables
data (OWID dataset) with automated trend insights and a RAG-based Q&A assistant over
energy market reports (sentence-transformers + FAISS); deployed as an interactive
Streamlit app."

## Next steps for a fresh session
1. Read this file first.
2. Pick up from the first unchecked item in Status above.
3. If `GROQ_API_KEY` isn't set, the app still works (extractive RAG answers, templated
   insights) — don't block the demo on getting an API key.
