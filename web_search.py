from duckduckgo_search import DDGS

def web_search(query):

    with DDGS() as ddgs:

        results = list(ddgs.text(query, max_results=5))

    context = ""

    for result in results:

        context += (
            f"Title: {result['title']}\n"
            f"Body: {result['body']}\n\n"
        )

    return context