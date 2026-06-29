import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go

# ১. পেজ সেটিংস ও উচ্চ-কন্ট্রাস্ট মার্জিত থিম
st.set_page_config(page_title="DiscreteMind AI", page_icon="🧠", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; }
    .stApp, p, span, label, li { color: #f8fafc !important; font-size: 16px; }
    h1 { color: #f1f5f9 !important; font-weight: 700 !important; }
    h2, h3, h4 { color: #38bdf8 !important; font-weight: 600 !important; }
    
    /* মক টেস্ট ফর্ম সেটিংস */
    div[data-testid="stForm"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }
    
    /* ইউনিভার্সাল বাটন ডিজাইন */
    .stButton>button {
        background: #0284c7 !important; color: #ffffff !important;
        font-weight: bold !important; border: none !important;
        border-radius: 6px !important; padding: 0.6rem 2rem !important;
        text-transform: none !important;
    }
    .stButton>button:hover { background: #0369a1 !important; }
    
    /* উত্তর বক্সের ব্যাকগ্রাউন্ড সাদা এবং লেখা কালো করার জন্য */
    .answer-box {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px !important;
        border-radius: 8px !important;
        border: 2px solid #cbd5e1 !important;
        margin-top: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    .answer-box * { color: #000000 !important; }
    .answer-box .katex, .answer-box .katex * {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    /* লাইভ স্ট্যাটাস বক্স স্টাইলিং */
    .status-panel {
        padding: 12px !important;
        border-radius: 8px !important;
        text-align: center !important;
        font-weight: bold !important;
        margin-bottom: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ২. এপিআই কি কনফিগারেশন 
ANY_API_KEY = ""
for secret_key in ["ANY_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "CLAUDE_API_KEY"]:
    if secret_key in st.secrets:
        ANY_API_KEY = st.secrets[secret_key]
        break

# সাইডবারে ম্যানুয়াল এপিআই কী ইনপুট বক্স
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🔑 Multi-Provider API Config</h3>", unsafe_allow_html=True)
manual_key = st.sidebar.text_input(
    "Enter OpenAI, Gemini or Claude Key:", 
    type="password", 
    help="Paste your API key here. The engine will auto-detect the provider!"
)

# ফাইনাল কি চুজ করা
final_key = manual_key.strip() if manual_key.strip() else ANY_API_KEY.strip()

# অটো ডিটেকশন লজিক
def detect_provider(api_key):
    if not api_key:
        return None
    if api_key.startswith("sk-") and not api_key.startswith("sk-ant-"):
        return "OpenAI"
    elif api_key.startswith("sk-ant-"):
        return "Claude"
    elif api_key.startswith("AIzaSy") or api_key.startswith("AQ"):
        return "Gemini"
    if len(api_key) >= 35:
        return "Gemini"
    return "Unknown"

provider = detect_provider(final_key)

# ইউনিভার্সাল REST API কল ফাংশন
def call_universal_ai(prompt_text, api_key, provider_name):
    if provider_name == "OpenAI":
        url = "https://api.openai.com/v1/chat/completions"
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt_text}],
            "temperature": 0.3
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], True
            return f"OpenAI Error {res.status_code}: {res.text}", False
        except Exception as e: return str(e), False

    elif provider_name == "Gemini":
        gateways = [
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        ]
        
        last_error = ""
        for url_template in gateways:
            url = f"{url_template}?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
            try:
                res = requests.post(url, headers=headers, json=payload, timeout=12)
                # --- [FIXED] এখানে সিনট্যাক্স এররটি সম্পূর্ণ জোড়া লাগানো হয়েছে ---
                if res.status_code == 200:
                    return res.json()['candidates'][0]['content']['parts'][0]['text'], True
                last_error = f"Gemini Error {res.status_code}: {res.text}"
            except Exception as e: 
                last_error = str(e)
        return last_error, False

    elif provider_name == "Claude":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            'X-API-Key': api_key,
            'Anthropic-Version': '2023-06-01',
            'Content-Type': 'application/json'
        }
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt_text}]
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                return res.json()['content'][0]['text'], True
            return f"Claude Error {res.status_code}: {res.text}", False
        except Exception as e: return str(e), False
        
    return "Unsupported or undetected provider", False

# ৩. মেইন ইউজার ইন্টারফেস (UI) রেন্ডারিং
st.title("🧠 DiscreteMind AI")
st.markdown("Your advanced AI companion for smart reasoning and instant solutions.")

# সাইডবারে লাইভ স্ট্যাটাস ইন্ডিকেটর
if provider:
    st.sidebar.markdown(f'<div class="status-panel" style="background-color: #1e3a1e; color: #4ade80; border: 1px solid #22c55e;">Connected to: {provider}</div>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<div class="status-panel" style="background-color: #3a1e1e; color: #f87171; border: 1px solid #ef4444;">Not Connected</div>', unsafe_allow_html=True)

# ইউজার ইনপুট ফর্ম বক্স
with st.form("ai_form"):
    user_prompt = st.text_area("Ask me anything:", placeholder="Type your question or problem here...")
    submit_button = st.form_submit_button("Generate Response")

# সাবমিট অ্যাকশন হ্যান্ডলার
if submit_button:
    if not final_key:
        st.error("🔑 API Key পাওয়া যায়নি! দয়া করে সাইডবারে একটি সঠিক Key প্রদান করুন।")
    elif not user_prompt.strip():
        st.warning("⚠️ দয়া করে বক্সে আপনার প্রশ্নটি লিখুন।")
    else:
        with st.spinner("Processing your request..."):
            response_text, success = call_universal_ai(user_prompt, final_key, provider)
            
            if success:
                # আপনার CSS থিম অনুযায়ী সুন্দর সাদা বক্সে এআই এর আউটপুট জেনারেট হবে
                st.markdown(f'<div class="answer-box">{response_text}</div>', unsafe_allow_html=True)
            else:
                st.error(f"❌ Error: {response_text}")
