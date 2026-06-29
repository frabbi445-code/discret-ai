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
ai_ready = False
connection_error_msg = ""
used_gateway = "Not Connected"

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
                if res.
