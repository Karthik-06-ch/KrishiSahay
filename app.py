"""
KrishiSahay — Kisan Call Centre Query Assistant.
Login, Registration, Language selection, and multilingual Q&A for farmers.
"""
import html
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
# Helper imports
from streamlit_mic_recorder import mic_recorder

from config import FAISS_INDEX, META_PKL, TOP_K, OLLAMA_MODEL
from retrieval import get_offline_answer, get_online_answer, get_available_models
from firebase_helper import save_to_firebase, get_firebase_config
from auth_helper import register_user, login_user
from data_feeds import get_weather, get_market_prices, analyze_plant_image
from report_gen import generate_prescription

DEFAULT_FIREBASE_URL = "https://kishanagent-d81dc-default-rtdb.asia-southeast1.firebasedatabase.app"

# Language options: code -> (display name, native name)
LANG_OPTIONS = {
    "en": ("English", "English"),
    "hi": ("Hindi", "हिंदी"),
    "ta": ("Tamil", "தமிழ்"),
    "te": ("Telugu", "తెలుగు"),
    "kn": ("Kannada", "ಕನ್ನಡ"),
}

# UI strings per language
LANG_STRINGS = {
    "en": {
        "app_title": "Kisan Call Centre Assistant",
        "app_caption": "Your expert agricultural companion.",
        "query_label": "Ask your question",
        "query_placeholder": "e.g. How to control aphids? What fertilizer for wheat?",
        "get_answer": "Get Answer",
        "offline_answer": "Knowledge Base (KCC)",
        "online_answer": "AI Expert Answer",
        "use_online": "Enable AI Expert (Online)",
        "saved_firebase": "Saved to history",
        "login_title": "Login",
        "login_email": "Email",
        "login_password": "Password",
        "login_btn": "Login",
        "no_account": "Don't have an account?",
        "register_here": "Register here",
        "register_title": "Create Account",
        "register_name": "Full name",
        "register_email": "Email",
        "register_password": "Password (min 6 chars)",
        "register_btn": "Register",
        "have_account": "Already have an account?",
        "login_here": "Login here",
        "select_language": "Language / भाषा",
        "logout": "Logout",
        "welcome": "Welcome",
        "about": "About",
        "about_text": "Powered by FAISS & Ollama AI.",
        "sample_queries": "Try These",
        "settings": "AI Settings",
        "model_select": "Select AI Model",
        "weather_title": "Weather",
        "market_title": "Market Prices",
        "voice_input": "🎤 Voice Input",
        "download_pdf": "📥 Download Prescription",
        "plant_doctor": "📸 Plant Doctor",
        "upload_leaf": "Upload Leaf Image",
    },
    "hi": {
        "app_title": "किसान कॉल सेंटर सहायक",
        "app_caption": "आपका विशेषज्ञ कृषि साथी।",
        "query_label": "अपना सवाल पूछें",
        "query_placeholder": "जैसे: सरसों में एफिड कैसे नियंत्रित करें?",
        "get_answer": "जवाब पाएं",
        "offline_answer": "ज्ञान का आधार (KCC)",
        "online_answer": "AI विशेषज्ञ जवाब",
        "use_online": "AI विशेषज्ञ सक्षम करें",
        "saved_firebase": "इतिहास में सहेजा गया",
        "login_title": "लॉगिन",
        "login_email": "ईमेल",
        "login_password": "पासवर्ड",
        "login_btn": "लॉगिन",
        "no_account": "खाता नहीं है?",
        "register_here": "यहां रजिस्टर करें",
        "register_title": "खाता बनाएं",
        "register_name": "पूरा नाम",
        "register_email": "ईमेल",
        "register_password": "पासवर्ड",
        "register_btn": "रजिस्टर",
        "have_account": "पहले से खाता है?",
        "login_here": "यहां लॉगिन करें",
        "select_language": "भाषा / Language",
        "logout": "लॉगआउट",
        "welcome": "स्वागत है",
        "about": "जानीए",
        "about_text": "FAISS और Ollama AI द्वारा संचालित।",
        "sample_queries": "कोशिश करें",
        "settings": "AI सेटिंग्स",
        "model_select": "AI मॉडल चुनें",
        "weather_title": "मौसम",
        "market_title": "बाजार भाव",
        "voice_input": "🎤 बोलकर पूछें",
        "download_pdf": "📥 नुस्खा डाउनलोड करें",
        "plant_doctor": "📸 प्लांट डॉक्टर",
        "upload_leaf": "पत्ती की फोटो अपलोड करें",
    },
    # Simple fallbacks for others
    "ta": { "app_title": "கிசான் கால் சென்டர்", "select_language": "மொழி", "login_title": "உள்நுழை", "register_title": "பதிவு", "get_answer": "பதில்", "query_label": "கேள்வி", "welcome": "வணக்கம்" },
    "te": { "app_title": "కిసాన్ కాల్ సెంటర్", "select_language": "భాష", "login_title": "లాగిన్", "register_title": "నమోదు", "get_answer": "జవాబు", "query_label": "ప్రశ్న", "welcome": "స్వాగతం" },
    "kn": { "app_title": "ಕಿಸಾನ್ ಕಾಲ್ ಸೆಂಟರ್", "select_language": "ಭಾಷೆ", "login_title": "ಲಾಗಿನ್", "register_title": "ನೋಂದಣಿ", "get_answer": "ಉತ್ತರ", "query_label": "ಪ್ರಶ್ನೆ", "welcome": "ಸ್ವಾಗತ" },
}

def _t(lang: str, key: str) -> str:
    d = LANG_STRINGS.get(lang, LANG_STRINGS["en"])
    return d.get(key, LANG_STRINGS["en"].get(key, key))


st.set_page_config(
    page_title="KrishiSahay AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- PREMIUM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(to bottom right, #f8fcf8, #eef7ee);
    }
    
    h1, h2, h3 {
        color: #1b4332;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Widget Cards */
    .widget-card {
       background: white; border-radius: 8px; padding: 10px; margin-bottom: 10px; border: 1px solid #eee;
       box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box_shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        margin-bottom: 1.5rem;
        border: 1px solid #f0f0f0;
    }
    
    .offline-header { color: #2d6a4f; font-weight: 600; display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem; }
    .online-header { color: #1a73e8; font-weight: 600; display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem; }
    .answer-text { color: #333; line-height: 1.6; white-space: pre-wrap; }
    
    .stButton button {
        background-color: #2d6a4f; color: white; border-radius: 8px; font-weight: 600; border: none; padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #1b4332;
        box-shadow: 0 4px 12px rgba(45, 106, 79, 0.2);
    }
    
    .auth-container {
        max-width: 400px;
        margin: 4rem auto;
        background: white;
        padding: 2.5rem;
        border-radius: 16px;
        box_shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)


def _init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "selected_language" not in st.session_state:
        st.session_state.selected_language = "en"
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = OLLAMA_MODEL
    # Voice input buffer
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""


def render_login(lang: str):
    # (Same as before, abbreviated for brevity, logic remains identical)
    # Copied from previous view for completeness
    cols = st.columns([1, 1, 1])
    with cols[1]:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #2d6a4f;'>🌾 {_t(lang, 'app_title')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #555;'>{_t(lang, 'login_title')}</h4>", unsafe_allow_html=True)
        
        l_opts = list(LANG_OPTIONS.keys())
        idx = l_opts.index(lang) if lang in l_opts else 0
        new_lang = st.selectbox("Language / भाषा", options=l_opts, format_func=lambda c: LANG_OPTIONS[c][1], key="login_lang", index=idx)
        if new_lang != st.session_state.get("selected_language"):
            st.session_state.selected_language = new_lang
            st.rerun()

        with st.form("login_form"):
            email = st.text_input(_t(lang, "login_email"), key="login_email")
            password = st.text_input(_t(lang, "login_password"), type="password", key="login_pass")
            submitted = st.form_submit_button(_t(lang, "login_btn"), use_container_width=True)
            if submitted and email and password:
                ok, msg, user = login_user(email, password)
                if ok and user:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user["name"]
                    st.session_state.user_email = user["email"]
                    st.session_state.page = "main"
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
        
        st.markdown("---")
        st.caption(_t(lang, "no_account"))
        if st.button(_t(lang, "register_here"), key="goto_reg", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def render_register(lang: str):
    cols = st.columns([1, 1, 1])
    with cols[1]:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: #2d6a4f;'>🌾 {_t(lang, 'app_title')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: #555;'>{_t(lang, 'register_title')}</h4>", unsafe_allow_html=True)

        with st.form("reg_form"):
            name = st.text_input(_t(lang, "register_name"), key="reg_name")
            email = st.text_input(_t(lang, "register_email"), key="reg_email")
            password = st.text_input(_t(lang, "register_password"), type="password", key="reg_pass")
            submitted = st.form_submit_button(_t(lang, "register_btn"), use_container_width=True)
            if submitted:
                ok, msg = register_user(name, email, password)
                if ok:
                    st.success(msg)
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error(msg)
        
        st.markdown("---")
        st.caption(_t(lang, "have_account"))
        if st.button(_t(lang, "login_here"), key="goto_login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def render_sidebar(lang: str):
    t = lambda k: _t(lang, k)
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3233/3233499.png", width=60)
        st.title("KrishiSahay")
        st.caption(f"{t('welcome')}, {st.session_state.user_name.split()[0] if st.session_state.user_name else 'Farmer'}")
        
        # --- WEATHER WIDGET ---
        weather = get_weather()
        st.markdown(f"""
        <div class="widget-card">
            <div style="font-weight:bold; color:#555;">🌦️ {t("weather_title")} ({weather['city']})</div>
            <div style="font-size: 1.2rem;">{weather['condition']} {weather['temp']}°C</div>
            <div style="font-size: 0.8rem; color:#888;">Hum: {weather['humidity']}%</div>
        </div>
        """, unsafe_allow_html=True)

        # --- MARKET WIDGET ---
        st.markdown(f"""<div class="widget-card"><div style="font-weight:bold; color:#555;">💰 {t("market_title")}</div>""", unsafe_allow_html=True)
        prices = get_market_prices()
        for p in prices:
             st.markdown(f"<div style='display:flex; justify-content:space_between; font-size:0.9rem;'><span>{p['crop']}</span><span><b>{p['price']}</b></span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


        st.markdown("---")
        # Language
        l_opts = list(LANG_OPTIONS.keys())
        idx = l_opts.index(lang) if lang in l_opts else 0
        new_lang = st.selectbox("Language", options=l_opts, format_func=lambda c: f"{LANG_OPTIONS[c][0]} ({LANG_OPTIONS[c][1]})", label_visibility="collapsed", index=idx, key="sb_lang")
        if new_lang != st.session_state.selected_language:
            st.session_state.selected_language = new_lang
            st.rerun()

        st.markdown("### 🤖 " + t("settings"))
        # Models
        available_models = get_available_models()
        if not available_models:
             available_models = [OLLAMA_MODEL, "granite3-dense:8b", "llama3"]
        current_model = st.session_state.get("selected_model", OLLAMA_MODEL)
        if current_model not in available_models:
             if available_models: available_models.insert(0, current_model)
        chosen_model = st.selectbox(t("model_select"), available_models, index=available_models.index(current_model) if current_model in available_models else 0)
        st.session_state.selected_model = chosen_model

        st.markdown("---")
        if st.button(t("logout"), key="logout_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()


def render_main(lang: str):
    t = lambda k: _t(lang, k)
    render_sidebar(lang)
    
    st.title(f"🌾 {t('app_title')}")
    st.markdown(f"*{t('app_caption')}*")
    st.markdown("---")

    if not FAISS_INDEX.exists() or not META_PKL.exists():
        st.error("⚠️ Data not initialized. Please run scripts.")
        return

    # Tabs for Text vs Image
    tab1, tab2 = st.tabs(["💬 Chat", t("plant_doctor")])

    with tab2: # Plant Doctor
        st.subheader(t("plant_doctor"))
        uploaded_file = st.file_uploader(t("upload_leaf"), type=["jpg", "png", "jpeg"])
        if uploaded_file is not None:
             st.image(uploaded_file, width=300)
             if st.button("🩺 Analyze Disease", type="primary"):
                 with st.spinner("Analyzing leaf image with AI..."):
                      bytes_data = uploaded_file.getvalue()
                      diagnosis = analyze_plant_image(bytes_data, model=st.session_state.selected_model)
                      st.markdown(f"""
                        <div class="result-card" style="border-left: 5px solid #e63946;">
                            <div class="online-header" style="color:#e63946;">🚑 Diagnosis</div>
                            <div class="answer-text">{html.escape(diagnosis).replace(chr(10), '<br>')}</div>
                        </div>
                        """, unsafe_allow_html=True)


    with tab1: # Chat
        # Voice Input Helper
        st.markdown(f"**{t('voice_input')}**")
        
        # Mapping for Web Speech API locales
        LOCALE_MAP = {
            "en": "en-IN", 
            "hi": "hi-IN", 
            "ta": "ta-IN", 
            "te": "te-IN", 
            "kn": "kn-IN"
        }
        current_locale = LOCALE_MAP.get(lang, "en-IN")

        # Browser-based STT (High Accuracy, No Server Processing needed)
        from streamlit_mic_recorder import speech_to_text
        
        # speech_to_text returns the transcribed text directly
        voice_text_output = speech_to_text(
            language=current_locale,
            start_prompt="🎤 Start Recording",
            stop_prompt="⏹️ Stop",
            just_once=False,
            key="STT"
        )
        
        if voice_text_output and voice_text_output != st.session_state.get("last_voice_text", ""):
            st.session_state.voice_query = voice_text_output
            st.session_state.last_voice_text = voice_text_output # Prevent infinite loop
            st.session_state.voice_auto_submit = True
            st.rerun()

        # Determine query source
        default_query = st.session_state.get("voice_query", "")
        
        col_q, col_tog = st.columns([4, 1])
        with col_q:
            query = st.text_input(t("query_label"), value=default_query, placeholder=t("query_placeholder"), key="query_input")
        with col_tog:
            st.write("") # Spacer
            use_online = st.toggle(t("use_online"), value=True)
        
        # Check for auto-submit flag
        auto_submit = st.session_state.get("voice_auto_submit", False)
        
        if st.button(t("get_answer"), type="primary", key="btn_ans") or auto_submit:
            # Clear the flag immediately so it doesn't loop
            if auto_submit:
                st.session_state.voice_auto_submit = False
                
            # If triggered by voice (audio exists) and we have text, we proceed.
            final_query = query if query else default_query
            
            if not final_query.strip():
                st.warning("Please enter a question.")
                return

            response_lang_name = LANG_OPTIONS[lang][0]
            
            with st.spinner("Searching knowledge base..."):
                results, offline_answer = get_offline_answer(final_query.strip(), top_k=TOP_K)

            # Offline Result Card
            if not use_online:
                st.markdown(f"""
                <div class="result-card">
                    <div class="offline-header">📊 {t('offline_answer')}</div>
                    <div class="answer-text">{html.escape(offline_answer).replace(chr(10), '<br>')}</div>
                </div>
                """, unsafe_allow_html=True)

            online_answer = ""
            final_answer_for_pdf = offline_answer
            
            if use_online:
                with st.spinner(f"AI ({st.session_state.selected_model}) is thinking..."):
                    online_answer = get_online_answer(
                        final_query.strip(), 
                        offline_answer, 
                        response_language=response_lang_name,
                        model_name=st.session_state.selected_model
                    )
                    final_answer_for_pdf = online_answer
                
                if "Error" in online_answer:
                     st.error(online_answer)
                else:
                    st.markdown(f"""
                    <div class="result-card" style="border-left: 5px solid #1a73e8;">
                        <div class="online-header">🤖 {t('online_answer')}</div>
                        <div class="answer-text">{html.escape(online_answer).replace(chr(10), '<br>')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # --- PDF DOWNLOAD ---
            pdf_file = generate_prescription(final_query, offline_answer, online_answer if use_online else None)
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label=t("download_pdf"),
                    data=f,
                    file_name="KrishiSahay_Prescription.pdf",
                    mime="application/pdf"
                )

            # Save to Firebase
            firebase_url, _ = get_firebase_config()
            if firebase_url:
                if save_to_firebase(final_query.strip(), offline_answer, online_answer or None):
                     st.toast(f"✅ {t('saved_firebase')}")

            # --- TEXT TO SPEECH (TTS) ---
            # Speak the answer (Online if available, else Offline)
            text_to_speak = online_answer if use_online and online_answer else offline_answer
            # Remove any raw HTML/markdown for speech if possible, but gTTS handles text decently.
            # Simple cleanup:
            import re
            clean_text = re.sub(r'<[^>]+>', '', text_to_speak).replace('*', '').replace('#', '')
            
            if clean_text:
                from gtts import gTTS
                import io
                
                try:
                    # Detect language from response if possible, else default to selected language or 'en'
                    # gTTS supports 'hi', 'en', 'ta', 'te', 'kn', 'ml' etc.
                    tts_lang = lang if lang in ['en', 'hi', 'ta', 'te', 'kn'] else 'en'
                    
                    tts = gTTS(text=clean_text[:500], lang=tts_lang, slow=False) # Limit to first 500 chars for speed
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    st.audio(audio_fp, format='audio/mp3', start_time=0)
                except Exception as e:
                    # Fallback or silent fail if Tts issue
                    print(f"TTS Error: {e}")


def main():
    _init_session()
    
    # Check query param for page routing
    q = st.query_params.get("page", "")
    if q == "register":
        st.session_state.page = "register"
    elif q == "login":
        st.session_state.page = "login"

    lang = st.session_state.get("selected_language", "en")

    if not st.session_state.logged_in:
        if st.session_state.page == "register":
            render_register(lang)
        else:
            render_login(lang)
        return

    render_main(lang)


if __name__ == "__main__":
    main()
