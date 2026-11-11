# Equity Research News Tool

Streamlit app that fetches news from NewsAPI and summarises it with Google Gemini via LangChain.

## Files
| File | Purpose |
|---|---|
| app.py | Streamlit interface (run this one) |
| langchain_config.py | NewsAPI + LangChain/Gemini logic (imported by app.py) |
| requirements.txt | Dependencies |
| gitignore.txt | Rename to `.gitignore` (keeps secrets out of GitHub) |
| secrets.toml.example | Template for your API keys |

## Setup (VS Code)
1. Rename `gitignore.txt` -> `.gitignore`
2. Create a folder named `.streamlit` in this folder.
3. Copy `secrets.toml.example` into `.streamlit/` and rename it `secrets.toml`, then paste your real keys.
4. Terminal:
   ```
   python -m venv .venv
   .venv\Scripts\activate       
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Deploy
1. Run `git status` and confirm `secrets.toml` is NOT listed.
2. Push to GitHub.
3. share.streamlit.io -> Create app -> main file `app.py`.
4. Advanced settings -> Secrets: paste
   ```
   NEWSAPI_KEY = "..."
   GEMINI_API_KEY = "..."
   ```
