"""
Kisan Call Centre Query Assistant - Streamlit UI.
Step 6: Accept user query, show Offline (FAISS) and Online (LLM) answers.
"""
import html
import streamlit as st
from pathlib import Path

# Project root
sys_path = Path(__file__).resolve().parent
import sys
if str(sys_path) not in sys.path:
    sys.path.insert(0, str(sys_path))

from config import FAISS_INDEX, META_PKL, TOP_K
from retrieval import get_offline_answer, get_online_answer
from firebase_helper import save_to_firebase, get_firebase_config

# Default Firebase URL (user can paste their own in sidebar or .env)
DEFAULT_FIREBASE_URL = "https://kishanagent-d81dc-default-rtdb.asia-southeast1.firebasedatabase.app"


st.set_page_config(
    page_title="Kisan Call Centre Query Assistant",
    page_icon="🌾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom style
st.markdown("""
<style>
    .stApp { max-width: 900px; margin: 0 auto; }
    h1 { color: #2d5a27; font-size: 1.8rem !important; }
    .answer-box { padding: 1rem 1.25rem; border-radius: 8px; margin: 1rem 0; white-space: pre-wrap; }
    .offline-box { background: #f0f7ee; border-left: 4px solid #2d5a27; }
    .online-box { background: #e8f4fd; border-left: 4px solid #1a73e8; }
    .stSpinner > div { border-color: #2d5a27 !important; }
</style>
""", unsafe_allow_html=True)


def _html_box(content: str, css_class: str) -> str:
    """Wrap content in a styled div (content escaped for HTML)."""
    escaped = html.escape(content).replace("\n", "<br>")
    return f'<div class="answer-box {css_class}">{escaped}</div>'


def main():
    st.title("Kisan Call Centre Query Assistant")
    st.caption("AI-powered agricultural helpdesk using FAISS and IBM Watsonx Granite LLM")

    if not FAISS_INDEX.exists() or not META_PKL.exists():
        st.error(
            "FAISS index not found. Run the build pipeline first:\n\n"
            "1. `python scripts/data_preprocessing.py`\n"
            "2. `python scripts/build_embeddings_faiss.py`"
        )
        return

    query = st.text_input(
        "Enter your agricultural query",
        placeholder="e.g. How to control aphids in mustard? What fertilizer for wheat at flowering?",
        key="query",
    )

    use_online = st.checkbox("Use online mode (IBM Watsonx LLM)", value=False, help="Requires WATSONX_APIKEY and WATSONX_PROJECT_ID in .env")

    if st.button("Get answer", type="primary") and query.strip():
        with st.spinner("Searching KCC database..."):
            results, offline_answer = get_offline_answer(query.strip(), top_k=TOP_K)

        st.markdown("### 📋 Offline answer (KCC database)")
        st.markdown(_html_box(offline_answer, "offline-box"), unsafe_allow_html=True)

        online_answer = ""
        if use_online:
            with st.spinner("Generating answer with IBM Watsonx Granite LLM..."):
                online_answer = get_online_answer(query.strip(), offline_answer)
            st.markdown("### 🤖 Online answer (LLM-generated)")
            st.markdown(_html_box(online_answer, "online-box"), unsafe_allow_html=True)
            if "requires WATSONX" in online_answer or ".env" in online_answer:
                with st.expander("How to get Watson API for free & enable Online mode"):
                    st.markdown("""
                    **Get IBM Watson API for free**
                    - **Free trial**: [Try watsonx.ai](https://www.ibm.com/products/watsonx-ai/info/trial) — 30-day trial with IBM/Google/LinkedIn account.
                    - **Free tier**: [watsonx.ai](https://www.ibm.com/watsonx/get-started) includes a **Free Toolbox** with ~300,000 tokens/month for foundation models.
                    - Sign up → Create a project → Get **Project ID** and **API key** from IBM Cloud.

                    **Configure in this project**
                    1. Copy `.env.example` to `.env` in the project folder.
                    2. Set:
                       - `WATSONX_APIKEY` = your API key  
                       - `WATSONX_PROJECT_ID` = your project ID  
                       - `WATSONX_URL` = your region endpoint (e.g. `https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2024-05-31`)
                    3. Restart the app and check **Use online mode** again.
                    """)
        else:
            st.info("Enable **Use online mode** and set Watsonx credentials in `.env` for LLM-generated answers.")

        # Save to Firebase if URL is set (from .env or sidebar paste)
        import os as _os
        if st.session_state.get("firebase_url"):
            _os.environ["FIREBASE_DATABASE_URL"] = st.session_state["firebase_url"]
            _os.environ["FIREBASE_API_KEY"] = st.session_state.get("firebase_api_key") or ""
        firebase_url, _ = get_firebase_config()
        if firebase_url:
            if save_to_firebase(query.strip(), offline_answer, online_answer or None):
                st.caption("✅ Saved to Firebase")
            else:
                st.caption("⚠️ Could not save to Firebase. Check URL and API key in Settings.")

    st.sidebar.title("About")
    st.sidebar.markdown(
        "**Data**: Stored in **Firebase**. **Chatbot**: **IBM Watsonx** LLM. "
        "Offline answers from KCC database (FAISS); online answers from Watson."
    )
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚙️ Firebase & API keys"):
        st.markdown("Paste your Firebase Realtime Database URL and optional API key below (or set in `.env`).")
        fb_url = st.text_input(
            "Firebase Database URL",
            value=st.session_state.get("firebase_url", DEFAULT_FIREBASE_URL),
            placeholder="https://your-project.firebasedatabase.app",
            key="firebase_url_input",
        )
        fb_key = st.text_input(
            "Firebase API Key (optional)",
            value=st.session_state.get("firebase_api_key", ""),
            placeholder="Paste API key if your rules require auth",
            type="password",
            key="firebase_key_input",
        )
        if st.button("Use these credentials"):
            st.session_state["firebase_url"] = (fb_url or "").strip() or None
            st.session_state["firebase_api_key"] = (fb_key or "").strip() or None
            if st.session_state.get("firebase_url"):
                st.success("Firebase URL set for this session.")
            else:
                st.info("Clear URL to use .env only.")
        st.caption("Data is saved under `/conversations`. If your DB rules need auth, use the database secret (Project Settings → Service accounts).")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Sample queries**")
    st.sidebar.markdown("- How to control aphids in mustard?")
    st.sidebar.markdown("- What fertilizer during flowering in wheat?")
    st.sidebar.markdown("- How to apply for PM Kisan Samman Nidhi?")
    st.sidebar.markdown("- How to treat blight in potato crops?")


if __name__ == "__main__":
    main()
