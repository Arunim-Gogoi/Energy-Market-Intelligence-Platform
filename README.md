# ⚡ Energy Market Intelligence Platform

An analyst-style dashboard for global energy markets — oil, gas, coal, renewables and
demand trends — paired with a hybrid RAG assistant that answers market questions using
both a local knowledge base and live web search.

**[Live demo →](https://energy-market-intelligence-platform-hdaawum42sfefwvnqsab6q.streamlit.app/)**


## What it does

- **Interactive dashboard** — oil production, renewables share of electricity, and
  primary energy consumption mix, filterable by country and year range (Our World in
  Data energy dataset)
- **Automated trend insights** — period-over-period change narratives generated
  directly from the underlying data
- **Hybrid RAG Q&A** — ask questions in plain language and get answers grounded in:
  - a local knowledge base (embedded with sentence-transformers, indexed with FAISS)
  - live web search (Tavily) for anything time-sensitive
  - generated with Groq (`openai/gpt-oss-120b`), with a graceful extractive fallback
    if no LLM key is configured

## Tech stack

`Streamlit` · `pandas` · `Plotly` · `sentence-transformers` · `FAISS` · `Groq` ·
`Tavily`

## Run it locally

```bash
git clone <this repo>
cd Energy_Market_Intelligence_Platform
pip install -r requirements.txt
# create a .env file with GROQ_API_KEY and TAVILY_API_KEY (both optional —
# the app degrades gracefully without them)
streamlit run app.py
```

## Why I built this

Built as a demo for a campus recruiting drive focused on energy-market analysis,
to show an end-to-end pipeline an analyst role would actually use: data ingestion,
trend analysis, and a retrieval-grounded assistant — not just a chatbot wrapper.
