import json
from tavily import TavilyClient
from utils.config import TAVILY_API_KEY, TAVILY_SEARCH_DEPTH, TAVILY_MAX_RESULTS

client = TavilyClient(api_key=TAVILY_API_KEY)


def _build_queries(topic: str) -> list[str]:
    """Build 3 targeted queries from a topic — specific beats generic."""
    return [
        topic,
        f"{topic} India 2026",
        f"{topic} impact analysis data",
    ]


def research_topic(topic: str) -> dict:
    """
    Run 3 Tavily searches, deduplicate, return structured research context.
    Returns: {sources, key_facts, summary, raw_results}
    """
    queries = _build_queries(topic)
    seen_urls = set()
    all_results = []
    best_answer = ""

    for query in queries:
        resp = client.search(
            query=query,
            search_depth=TAVILY_SEARCH_DEPTH,
            max_results=TAVILY_MAX_RESULTS,
            include_answer=True,
        )
        # Keep the longest/best answer across all queries
        answer = resp.get("answer", "") or ""
        if len(answer) > len(best_answer):
            best_answer = answer
        for r in resp.get("results", []):
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)

    sources = [
        {"title": r["title"], "url": r["url"], "snippet": r.get("content", "")[:300]}
        for r in all_results
    ]

    # Key facts: first sentence of each result snippet
    key_facts = [
        r.get("content", "").split(".")[0].strip() + "."
        for r in all_results
        if r.get("content", "").strip()
    ][:8]  # cap at 8 facts

    summary = best_answer or f"Research on: {topic}"

    return {
        "topic": topic,
        "queries_run": queries,
        "sources": sources,
        "key_facts": key_facts,
        "summary": summary,
        "source_count": len(sources),
    }


def get_trending_topics() -> dict:
    """Fetch trending India finance news for topic suggestion."""
    resp = client.search(
        query="trending India finance news this week",
        search_depth="basic",
        max_results=8,
        include_answer=True,
    )
    return {
        "results": resp.get("results", []),
        "answer": resp.get("answer", ""),
    }


# ponytail: CLI test
if __name__ == "__main__":
    topic = input("Enter topic to research: ")
    result = research_topic(topic)
    print(f"\nSearched {len(result['queries_run'])} queries → {result['source_count']} sources")
    print("\nKey facts:")
    for f in result["key_facts"]:
        print(f"  • {f}")
    print(f"\nSummary: {result['summary'][:200]}")
