"""Streamlit front-end for the Equity Research News Tool (NewsAPI + LangChain + Gemini)."""

import os
from datetime import date, timedelta

import streamlit as st
from newsapi.newsapi_exception import NewsAPIException

from langchain_config import DEFAULT_MODEL, get_news_articles, get_summary

st.set_page_config(page_title="Equity Research News Tool", page_icon="📈", layout="wide")


def get_secret(name: str):
    """Read a key from Streamlit secrets (cloud) or environment variables (local)."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name)


@st.cache_data(ttl=900, show_spinner=False)
def cached_articles(query, news_key, from_date, page_size):
    """Cache NewsAPI results for 15 minutes to save the daily request quota."""
    return get_news_articles(query, news_key, from_date, page_size)


st.title("📈 Equity Research News Tool")
st.write("Enter a company, ticker or topic to get a sourced summary of recent news.")

news_key = get_secret("NEWSAPI_KEY")
gemini_key = get_secret("GEMINI_API_KEY")

with st.sidebar:
    st.header("Settings")
    model = st.text_input("Gemini model", value=DEFAULT_MODEL)
    days = st.slider("Look back (days)", 1, 30, 7,
                     help="NewsAPI's free plan only goes back about 30 days.")
    n_articles = st.slider("Number of articles", 5, 30, 10)
    if not news_key:
        news_key = st.text_input("NewsAPI key", type="password")
    if not gemini_key:
        gemini_key = st.text_input("Gemini API key", type="password")

query = st.text_input("Query", placeholder='e.g. "Tata Motors" Q2 results')

if st.button("Get News", type="primary"):
    if not query.strip():
        st.warning("Please enter a query.")
    elif not news_key or not gemini_key:
        st.error("Missing API keys. Add them in secrets (see README) or in the sidebar.")
    else:
        from_date = (date.today() - timedelta(days=days)).isoformat()
        try:
            with st.spinner("Fetching news..."):
                articles = cached_articles(query.strip(), news_key, from_date, n_articles)
        except NewsAPIException as e:
            st.error(f"NewsAPI error: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Could not fetch news: {e}")
            st.stop()

        if not articles:
            st.info("No articles found. Try a broader query or a longer look-back period.")
            st.stop()

        try:
            with st.spinner("Summarising with LangChain + Gemini..."):
                summary = get_summary(query.strip(), articles, gemini_key, model)
        except Exception as e:
            st.error(f"Gemini error: {e}")
            st.stop()

        st.markdown("### Summary")
        st.markdown(summary)
        st.download_button("Download summary (.md)", summary,
                           file_name="news_summary.md", mime="text/markdown")

        st.markdown("### Sources")
        for i, a in enumerate(articles, start=1):
            src = (a.get("source") or {}).get("name", "Unknown")
            with st.expander(f"[{i}] {a.get('title', 'Untitled')} - {src}"):
                st.caption(a.get("publishedAt", ""))
                st.write(a.get("description") or "No description available.")
                st.markdown(f"[Read full article]({a.get('url')})")
