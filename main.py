import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import random
import json
import plotly.graph_objects as go
from datetime import datetime

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
    
    /* উত্তর বা এআই আউটপুট বক্সের ব্যাকগ্রাউন্ড সাদা এবং লেখা কালো করার জন্য */
    .answer-box {
        background-color: #ffffff !important;
        color: #000000 !important;
        padding: 25px !important;
        border-radius: 8px !important;
        border: 2px solid #cbd5e1 !important;
        margin-top: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* সাদা বক্সের ভেতরের টেক্সট, হেডিং ও সূত্রের কালার ব্ল্যাক ফোর্স করা */
    .answer-box * {
        color: #000000 !important;
    }
    .answer-box .katex, .answer-box .katex * {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Universal Course Solver")
st.subheader("Discrete Mathematics Engine & Interactive Exam Lab")
st.write("Presidency University | CSE Dept | Academic Edition")
st.write("---")

# Session State ইনিশিয়েলাইজেশন
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'ai_questions' not in st.session_state:
    st.session_state.ai_questions = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'exam_submitted' not in st.session_state:
    st.session_state.exam_submitted = False

# ২. সাইডবার প্রোফাইল
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🎓 Student Profile</h3>", unsafe_allow_html=True)
with st.sidebar.container(border=True):
    st.write("**Developer:** MD FAZLE RABBI SOHAN")
    st.write("**Institution:** Presidency University")
    st.write("**Department:** CSE")
    st.markdown("<span style='color: #4ade80; font-weight: bold;'>🔥 Core AI Engine: Connected</span>", unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.page_link("https://presidency.edu.bd/", label="Presidency University Portal", icon="🏫")

# ৩. এপিআই কি কনফিগারেশন
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    ai_model = genai.GenerativeModel(model_name='gemini-2.5-flash')
else:
    ai_model = None

# ৪. ইউনিভার্সাল সিঙ্গেল ইনপুট ইন্টারফেস
st.markdown("<h3 style='color: #38bdf8;'>🚀 Universal Math Input Box</h3>", unsafe_allow_html=True)
st.caption("💡 Enter any Discrete Mathematics problem below (Truth Tables, Graphs, Sets, Counting, Recurrence):")

user_query = st.text_area(
    "📝 Type or paste your question here:",
    placeholder="e.g., Find the explicit formula for a_n = 5a_{n-1} - 6a_{n-2}...",
    height=110
)

if st.button("Generate Answer", use_container_width=True):
    if not user_query.strip():
        st.warning("⚠️ Please enter a question first!")
    else:
        with st.spinner("✨ Generating solution..."):
            try:
                if ai_model:
                    prompt = f"You are an expert university professor in Discrete Mathematics. Provide a rigorous, step-by-step, textbook-style solution with proper LaTeX formatting for: {user_query}"
                    response = ai_model.generate_content(prompt)
                    solution = response.text
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    st.session_state.search_history.insert(0, {"time": timestamp, "query": user_query, "sol": solution})
                else:
                    solution = "⚠️ API Key not configured in Streamlit Secrets."
                
                st.balloons()
                st.success("🎉 Solution generated successfully!")
                
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error: {e}")

# লাইভ সেশন সার্চ হিস্ট্রি লগ
if st.session_state.search_history:
    with st.expander("📜 Live Session Search Log"):
        for idx, item in enumerate(st.session_state.search_history):
            st.markdown(f"**🕒 [{item['time']}] Q:** {item['query']}")
            if st.checkbox("View Solution", key=f"hist_chk_{idx}"):
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(item['sol'])
                st.markdown('</div>', unsafe_allow_html=True)
            st.write("---")

st.write("---")

# 🧠 ৫. মডিউল ২: ইউনিভার্সিটি স্ট্যান্ডার্ড মক টেস্ট ইঞ্জিন (MCQ + Math Problems)
st.markdown("<h3 style='color: #38bdf8;'>📝 Interactive Mid/Final Mock Test</h3>", unsafe_allow_html=True)
st.caption("💡 Click below to generate 5 real exam-standard questions in English, including critical mathematical calculations.")

if st.button("🔄 Generate New AI Exam Paper", use_container_width=True) or st.session_state.ai_questions is None:
    if ai_model:
        with st.spinner("🤖 Fetching high-quality exam problems..."):
            try
