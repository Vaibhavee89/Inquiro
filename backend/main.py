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