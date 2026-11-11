"""
LangChain configuration for the Equity Research News Tool.

Contains:
  - NewsAPI helpers (fetch + format articles)
  - A LangChain (LCEL) chain:  prompt | Gemini chat model | string parser
No Streamlit code here, so it can be tested on its own.
"""

from newsapi import NewsApiClient
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

DEFAULT_MODEL = "gemini-3.8-flash" 

SYSTEM_TEMPLATE = (
    "You are an AI assistant helping an equity research analyst. "
    "Use ONLY the news articles provided. Do not use outside knowledge, and do not "
    "invent numbers, quotes or events. If the articles do not cover something, say so. "
    "Cite sources inline using the article numbers, e.g. [1], [3]."
)

HUMAN_TEMPLATE = """Query: {query}

News articles (numbered):
{articles}

Write the answer in this structure:
1. **Bottom line** - 2-3 sentences answering the query.
2. **Key developments** - bullet points, each with citations like [1].
3. **Sentiment** - Positive / Neutral / Negative, with a one-line reason.
4. **Risks and catalysts** - bullet points.
5. **Gaps / conflicting reports** - what the articles don't cover or disagree on.
"""

prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_TEMPLATE), ("human", HUMAN_TEMPLATE)]
)


def get_news_articles(query: str, news_key: str, from_date: str, page_size: int = 10) -> list:
    """Fetch articles from NewsAPI."""
    client = NewsApiClient(api_key=news_key)
    resp = client.get_everything(
        q=query,
        language="en",
        sort_by="relevancy",
        from_param=from_date,
        page_size=page_size,
    )
    return resp.get("articles", [])


def format_articles(articles: list) -> str:
    """Turn the article list into a numbered text block for the prompt."""
    blocks = []
    for i, a in enumerate(articles, start=1):
        content = (a.get("content") or "").split("[+")[0].strip()  # drop NewsAPI truncation tag
        blocks.append(
            f"[{i}] {a.get('title', '')}\n"
            f"Source: {(a.get('source') or {}).get('name', 'Unknown')} | "
            f"Published: {a.get('publishedAt', '')}\n"
            f"Description: {a.get('description') or ''}\n"
            f"Content: {content}"
        )
    return "\n\n".join(blocks)


def build_chain(gemini_key: str, model: str = DEFAULT_MODEL):
    """Build the LangChain chain: prompt -> Gemini -> plain string."""
    llm = ChatGoogleGenerativeAI(model=model, google_api_key=gemini_key, temperature=0.2)
    return prompt | llm | StrOutputParser()


def get_summary(query: str, articles: list, gemini_key: str, model: str = DEFAULT_MODEL) -> str:
    """Summarise the given articles for the query."""
    chain = build_chain(gemini_key, model)
    return chain.invoke({"query": query, "articles": format_articles(articles)})
