from __future__ import annotations
from typing import List, Dict
import arxiv


def fetch_arxiv_papers(query: str, max_results: int = 5) -> List[Dict]:
    """Fetch papers from arXiv using the official arxiv Python client."""
    client = arxiv.Client(page_size=max_results, num_retries=3)
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    papers = []
    for result in client.results(search):
        papers.append({
            "id": result.entry_id.split("/")[-1],
            "title": result.title.replace("\n", " ").strip(),
            "abstract": result.summary.replace("\n", " ").strip(),
            "authors": ", ".join(a.name for a in result.authors[:3]),
            "published": str(result.published.date()),
            "categories": result.primary_category,
            "url": result.entry_id,
        })
    return papers
