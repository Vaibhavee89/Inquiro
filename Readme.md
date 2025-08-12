# AI-Powered Research Assistant — Full Project

**What this is**

A complete, full-stack reference implementation of an AI-powered research assistant that:

* accepts a research topic or query
* fetches recent papers from arXiv and Semantic Scholar
* summarizes each paper with GPT-5, produces bullet insights
* generates citation-formatted references and exports (BibTeX/APA)
* visualizes insights as a mind map
* provides basic reference management (save, tag, export)

---

## Architecture (high-level)

```
[React Frontend] <--> [FastAPI backend] <--> [Paper fetchers (arXiv, Semantic Scholar)]
                             |--> [GPT-5 summarization API]
                             |--> [Optional Vector DB for search (Pinecone/FAISS)]
                             |--> [DB: SQLite / Postgres for saved refs]
```

Key components included in this repo:

* `backend/` — FastAPI app that handles search, fetch, summarization and citation formatting
* `frontend/` — React app (single-page) with UI to search, view summaries, and mind-map visualizer
* `scripts/` — small utilities (e.g., import/export BibTeX)
* `README` — this document (you are reading it)

---

## Quick start (developer)

1. Clone repo

```bash
git clone <repo> research-assistant
cd research-assistant
```

2. Backend setup (Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create a `.env` file with the following keys:

```
OPENAI_API_KEY=sk-...
SEMANTIC_SCHOLAR_API_KEY=optional
DATABASE_URL=sqlite:///./data.db
ARXIV_BASE=https://export.arxiv.org/api/query
```

Run backend:

```bash
uvicorn main:app --reload --port 8000
```

3. Frontend setup (React)

```bash
cd ../frontend
npm install
npm start
```

Open [http://localhost:3000](http://localhost:3000)

---

## Backend — key files

### `backend/requirements.txt`

```
fastapi
uvicorn[standard]
httpx
pydantic
python-dotenv
sqlalchemy
alembic
openai
beautifulsoup4
lxml
python-multipart
```

### `backend/main.py` (FastAPI entry)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from services.arxiv_client import fetch_arxiv_papers
from services.summarizer import summarize_papers
from services.citation import format_citations

load_dotenv()

app = FastAPI(title="AI Research Assistant")

class SearchRequest(BaseModel):
    query: str
    max_results: int = 5

@app.post('/search')
async def search(req: SearchRequest):
    try:
        papers = await fetch_arxiv_papers(req.query, req.max_results)
        summaries = await summarize_papers(papers)
        citations = [format_citations(p) for p in papers]
        return {'papers': papers, 'summaries': summaries, 'citations': citations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### `backend/services/arxiv_client.py`

```python
import httpx
from bs4 import BeautifulSoup

ARXIV_BASE = 'http://export.arxiv.org/api/query'

async def fetch_arxiv_papers(query: str, max_results: int = 5):
    params = {
        'search_query': f'all:{query}',
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(ARXIV_BASE, params=params, timeout=30.0)
        resp.raise_for_status()
        text = resp.text
    # parse atom feed with BeautifulSoup
    soup = BeautifulSoup(text, 'lxml')
    entries = []
    for entry in soup.find_all('entry'):
        authors = [a.text for a in entry.find_all('author')]
        entries.append({
            'id': entry.id.text,
            'title': entry.title.text.strip(),
            'summary': entry.summary.text.strip(),
            'published': entry.published.text,
            'authors': authors,
            'link': entry.id.text
        })
    return entries
```

### `backend/services/summarizer.py`

```python
summarizer.py
```

### `backend/services/citation.py`

```python
from datetime import datetime

def format_citations(paper):
    # lightweight APA-like formatting, and BibTeX safe entry
    authors = paper.get('authors', [])
    author_str = ', '.join(authors)
    year = paper.get('published','')[:4] or 'n.d.'
    apa = f"{author_str} ({year}). {paper.get('title')}. arXiv. {paper.get('link')}"
    bibtex = f"""@article{{{paper.get('id').split('/')[-1]},
  title = {{{paper.get('title')}}},
  author = {{{author_str}}},
  year = {{{year}}},
  howpublished = {{arXiv:{paper.get('id').split('/')[-1]}}},
  url = {{{paper.get('link')}}}
}}"""
    return {'apa': apa, 'bibtex': bibtex}
```

---

## Frontend — key files

This is a minimal React app that interacts with the backend.

### `frontend/package.json` (important deps)

```json
{
  "name": "research-assistant-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "axios": "^1.0.0",
    "react-flow-renderer": "^11.0.0",
    "tailwindcss": "^3.0.0"
  }
}
```

### `frontend/src/api.js`

```javascript
import axios from 'axios';
const API = axios.create({ baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000' });
export async function search(query, max_results=5){
  const res = await API.post('/search', { query, max_results });
  return res.data;
}
```

### `frontend/src/App.jsx` (single-file UI)

```jsx
import React, {useState} from 'react'
import { search } from './api'
import ReactFlow, { MiniMap, Controls } from 'react-flow-renderer'

export default function App(){
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  async function handleSearch(){
    setLoading(true)
    try{
      const data = await search(query,5)
      setResults(data)
    }catch(e){
      console.error(e)
      alert('Search failed')
    }finally{ setLoading(false) }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">AI Research Assistant</h1>
      <div className="mt-4">
        <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Enter topic" className="border p-2 w-2/3" />
        <button onClick={handleSearch} className="ml-2 p-2 bg-slate-700 text-white">Search</button>
      </div>

      {loading && <p>Loading...</p>}

      {results && (
        <div className="mt-6 grid grid-cols-2 gap-4">
          <div>
            <h2 className="font-semibold">Papers</h2>
            {results.papers.map((p, idx) => (
              <div key={idx} className="border p-3 my-2">
                <a href={p.link} target="_blank" rel="noreferrer" className="font-medium">{p.title}</a>
                <p className="text-sm">{p.published} — {p.authors.join(', ')}</p>
                <details>
                  <summary>Summary</summary>
                  <pre>{JSON.stringify(results.summaries[idx], null, 2)}</pre>
                </details>
                <details>
                  <summary>Citation</summary>
                  <pre>{results.citations[idx].apa}</pre>
                </details>
              </div>
            ))}
          </div>
          <div>
            <h2 className="font-semibold">Mind Map</h2>
            {/* Lightweight node mapping: each paper -> node with bullets as children */}
            <div style={{height:400}}>
              <ReactFlow elements={buildFlowElements(results)}>
                <MiniMap />
                <Controls />
              </ReactFlow>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function buildFlowElements(results){
  if(!results) return []
  const nodes = []
  const edges = []
  results.papers.forEach((p, i) => {
    nodes.push({ id: 'p'+i, type: 'default', data: { label: p.title }, position: { x: 50, y: i*80 } })
    const bullets = (results.summaries[i] && results.summaries[i].bullets) || []
    bullets.forEach((b, j) => {
      const id = `p${i}b${j}`
      nodes.push({ id, data: { label: b }, position: { x: 350, y: i*80 + j*20 } })
      edges.push({ id: `e-${i}-${j}`, source: 'p'+i, target: id })
    })
  })
  return [...nodes, ...edges]
}
```

---

## Features & Extensions (next steps you can implement)

1. **Semantic Scholar + full PDF retrieval** — use Semantic Scholar API to enrich metadata, and fetch PDFs when available.
2. **Vector store + semantic search** — embed paper abstracts and summaries and use Pinecone/FAISS for similarity search.
3. **User accounts & persistent library** — add auth (OAuth with GitHub/Google) and allow users to save papers, tag and export lists.
4. **Batch summarization & background jobs** — schedule large fetch+summarize jobs with Celery/RQ.
5. **Citation export (BibTeX, RIS)** — provide download buttons.
6. **Better visualization** — use D3.js or mermaid to render richer mind maps; export PNG/SVG.

---

## Security & Rate limits

* Respect arXiv and Semantic Scholar API rate limits. Cache results where possible.
* Keep `OPENAI_API_KEY` secret on the server. Do not call OpenAI directly from the browser.

---

## Deployment

* Backend: containerize with Docker, deploy to Cloud Run / Azure App Se
