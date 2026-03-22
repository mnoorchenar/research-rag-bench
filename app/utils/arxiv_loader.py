from __future__ import annotations
from typing import List, Dict
import arxiv

def fetch_arxiv_papers(query: str, max_results: int = 5) -> List[Dict]:
    client = arxiv.Client(page_size=max_results, num_retries=3)
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    papers = []
    for r in client.results(search):
        papers.append({"id":r.entry_id.split("/")[-1],"title":r.title.replace("\n"," ").strip(),"abstract":r.summary.replace("\n"," ").strip(),"authors":", ".join(a.name for a in r.authors[:3]),"published":str(r.published.date()),"categories":r.primary_category,"url":r.entry_id})
    return papers
