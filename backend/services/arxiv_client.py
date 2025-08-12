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