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