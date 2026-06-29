import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import json
import itertools
import plotly.graph_objects as go

# ১. পেজ সেটিংস ও উচ্চ-কন্ট্রাস্ট মার্জিত থিম
st.set_page_config(page_title="DiscreteMind AI", page_icon="🧠", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0f172a; }
    .stApp, p, span, label, li { color: #f8fafc !important; font-size: 16px; }
    h1 { color: #f1f5f9 !important; font-weight: 700 !important; }
    h2, h3, h4 { color: #38bdf8 !important; font-weight: 600 !important; }
    
    /* কাস্টম প্রিমিয়াম মডিউল বক্স */
    .premium-box {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 22px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
    }
    
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
    
    /* উত্তর ও লেকচার বক্সের ব্যাকগ্রাউন্ড সাদা এবং লেখা কালো */
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
    .answer-box .katex, .answer-box .katex * { color: #000000 !important; font-weight: 600 !important; }
    
    /* ফ্ল্যাশ কার্ড স্টাইলিং */
    .flashcard {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        text-align: center !important;
        margin-bottom: 15px !important;
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
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None

ai_ready = False
ai_model = None

if GEMINI_API_KEY:
    clean_key = str(GEMINI_API_KEY).strip().replace('"', '').replace("'", "")
    try:
        genai.configure(api_key=clean_key)
        ai_model = genai.GenerativeModel('gemini-1.5-flash')
        ai_ready = True
    except Exception:
        ai_ready = False

# লাইভ কানেকশন ইন্ডিকেটর প্যানেল
st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: READY TO PERFORM</div>', unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Ultimate Interactive Lab")
st.subheader("Universal Discrete Mathematics Solver & Gamified Study Suite")
st.write("Presidency University | CSE Dept | Innovation Edition")
st.write("---")

# Session State ইনিশিয়েলাইজেশন
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'exam_submitted' not in st.session_state:
    st.session_state.exam_submitted = False
if 'user_score_history' not in st.session_state:
    st.session_state.user_score_history = []

# ৩. সাইডবার প্রোফাইল ও গ্যামিফাইড মেডেল ট্র্যাকার (Progress Tracker & Badge System)
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🎓 Student Profile</h3>", unsafe_allow_html=True)
with st.sidebar.container(border=True):
    st.write("**Developer:** MD FAZLE RABBI SOHAN")
    st.write("**Institution:** Presidency University")
    st.write("**Department:** CSE")
    
    # ডাইনামিক মেডেল ও র্যাঙ্ক লজিক
    history_len = len(st.session_state.user_score_history)
    if history_len >= 3:
        rank, badge = "Graph Wizard 🥇", "#f59e0b"
    elif history_len >= 1:
        rank, badge = "Logic Master 🥈", "#cbd5e1"
    else:
        rank, badge = "Discrete Novice 🥉", "#b45309"
        
    st.markdown(f"**Rank:** <span style='color:{badge}; font-weight:bold;'>{rank}</span>", unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.page_link("https://presidency.edu.bd/", label="Presidency University Portal", icon="🏫")

# 🧮 ৪. নতুন ফিচার ১: Live Interactive Truth Table Generator
st.markdown("<h3 style='color: #38bdf8;'>🧮 Live Interactive Truth Table Generator</h3>", unsafe_allow_html=True)
st.caption("💡 ২-ভেরিয়েবল প্রপোজিশনের জন্য অ্যান্ড (AND), অর (OR) বা কন্ডিশনাল ট্রুথ টেবিল লাইভ জেনারেট করো।")

col_t1, col_t2 = st.columns(2)
with col_t1:
    var_1 = st.selectbox("Select Variable 1:", ["P", "~P"])
with col_t2:
    op_type = st.selectbox("Select Logical Operator:", ["AND (/\)", "OR (\/)", "Implication (->)"])

if st.button("📊 Construct Truth Table", use_container_width=True):
    combinations = list(itertools.product([True, False], repeat=2))
    table_rows = []
    
    for p, q in combinations:
        v1 = p if var_1 == "P" else not p
        if "AND" in op_type:
            res = v1 and q
            sign = "∧"
        elif "OR" in op_type:
            res = v1 or q
            sign = "∨"
        else:
            res = (not v1) or q
            sign = "→"
            
        table_rows.append({
            "P": p,
            "Q": q,
            f"{var_1}": v1,
            f"{var_1} {sign} Q": res
        })
    
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    st.markdown(f"##### 🎯 Generated Truth Table for: `{var_1} {sign} Q`")
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 📊 ৫. সিলেবাস অ্যানালিটিক্স (পাই চার্ট সিস্টেম)
st.markdown("<h3 style='color: #38bdf8;'>📊 Dynamic Syllabus Analytics & Weight Distribution</h3>", unsafe_allow_html=True)

topic_data = {
    "Set Theory": {"importance": 15, "hardness": 30},
    "Propositional Logic": {"importance": 20, "hardness": 45},
    "Graph Theory": {"importance": 25, "hardness": 85},
    "Combinatorics & Counting": {"importance": 20, "hardness": 70},
    "Recurrence Relations": {"importance": 20, "hardness": 90}
}

col_list, col_chart = st.columns([1, 1.2])
with col_list:
    st.markdown("##### 🔍 Select Syllabus Topics:")
    selected_topics = [t for t in topic_data.keys() if st.checkbox(t, value=True)]

if selected_topics:
    labels = selected_topics
    importance_values = [topic_data[t]["importance"] for t in selected_topics]
    
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=importance_values, hole=.3, marker_colors=['#0ea5e9', '#38bdf8', '#0284c7', '#7dd3fc', '#bae6fd'])])
    fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=0, r=0, b=0, t=10))
    with col_chart:
        st.plotly_chart(fig_pie, use_container_width=True)

st.write("---")

# 📚 ৬. ইন্টারঅ্যাক্টিভ লেসন জেনারেটর (বাংলা + ইংরেজি)
st.markdown("<h3 style='color: #38bdf8;'>📚 Interactive Lesson Generator</h3>", unsafe_allow_html=True)
lesson_topic = st.selectbox("📖 Choose a topic to learn:", list(topic_data.keys()))

lecture_database =
