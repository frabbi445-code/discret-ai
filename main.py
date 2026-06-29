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
    
    /* কাস্টম প্রিমিয়াম মডিউল BOX */
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

# ২. এপিআই কি কনফিগারেশন ও API NotFound Error Fix
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
        # API 404/NotFound এড়াতে স্টেবল মডেল ব্যবহার করা হয়েছে
        ai_model = genai.GenerativeModel('gemini-1.5-flash')
        ai_ready = True
    except Exception:
        ai_ready = False

# লাইভ ইন্ডিকেটর প্যানেল
if ai_ready:
    st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: CONNECTED WITH GEMINI LIVE</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-panel" style="background-color: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; color: #f59e0b !important;">💡 Core AI Engine: RUNNING IN LOCAL MASTER-SIMULATION MODE</div>', unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Ultimate Interactive Lab")
st.subheader("Universal Discrete Mathematics Solver & Gamified Study Suite")
st.write("Presidency University | CSE Dept | Innovation Edition")
st.write("---")

# Session State ইনিশিয়েলাইজেশন
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'exam_submitted' not in st.session_state:
    st.session_state.exam_submitted = False
if 'user_score_history' not in st.session_state:
    st.session_state.user_score_history = []
if 'calculated_score' not in st.session_state:
    st.session_state.calculated_score = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0

# ৩. সাইডবার প্রোফাইল ও গ্যামিফাইড মেডেল ট্র্যাকার
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🎓 Student Profile</h3>", unsafe_allow_html=True)
with st.sidebar.container(border=True):
    st.write("**Developer:** MD FAZLE RABBI SOHAN")
    st.write("**Institution:** Presidency University")
    st.write("**Department:** CSE")
    
    history_len = len(st.session_state.user_score_history)
    if history_len >= 3:
        rank, badge = "Graph Wizard 🥇", "#f59e0b"
    elif history_len >= 1:
        rank, badge = "Logic Master 🥈", "#cbd5e1"
    else:
        rank, badge = "Discrete Novice 🥉", "#b45309"
        
    st.markdown(f"**Rank:** <span style='color:{badge}; font-weight:bold;'>{rank}</span>", unsafe_allow_html=True)
    if history_len > 0:
        st.metric(label="Tests Taken", value=history_len)

st.sidebar.write("---")
st.sidebar.page_link("https://presidency.edu.bd/", label="Presidency University Portal", icon="🏫")

# 🧮 ৪. Live Interactive Truth Table Generator
st.markdown("<h3 style='color: #38bdf8;'>🧮 Live Interactive Truth Table Generator</h3>", unsafe_allow_html=True)
st.caption("💡 ২-ভেরিয়েবল প্রপোজিশনের জন্য অ্যান্ড (AND), অর (OR) বা কন্ডিশনাল ট্রুথ টেবিল লাইভ জেনারেট করো।")

col_t1, col_t2 = st.columns(2)
with col_t1:
    var_1 = st.selectbox("Select Variable 1:", ["P", "~P"])
with col_t2:
    op_type = st.selectbox("Select Logical Operator:", ["AND (/\\)", "OR (\\/)", "Implication (->)"])

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
    st.dataframe(pd.DataFrame(table_rows).style.format(formatter={col: str for col in [f"{var_1}", f"{var_1} {sign} Q"]}), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 📊 ৫. সিলেবাস অ্যানালিটিক্স (পাই চার্ট + Hardness Index)
st.markdown("<h3 style='color: #38bdf8;'>📊 Dynamic Syllabus Analytics & Weight Distribution</h3>", unsafe_allow_html=True)

topic_data = {
    "Set Theory": {"importance": 15, "hardness": 30},
    "Propositional Logic": {"importance": 20, "hardness": 45},
    "Graph Theory": {"importance": 25, "hardness": 85},
    "Combinatorics & Counting": {"importance": 20, "hardness": 70},
    "Recurrence Relations": {"importance": 20, "hardness": 90}
}

st.markdown("##### 🔍 Select Syllabus Topics to Analyze:")
selected_topics = [t for t in topic_data.keys() if st.checkbox(t, value=True, key=f"sync_{t}")]

if selected_topics:
    col_chart1, col_chart2 = st.columns(2)
    
    # Chart 1: Importance Weight (Pie Chart)
    labels = selected_topics
    importance_values = [topic_data[t]["importance"] for t in selected_topics]
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=importance_values, hole=.3, marker_colors=['#0ea5e9', '#38bdf8', '#0284c7', '#7dd3fc', '#bae6fd'])])
    fig_pie.update_layout(title="Exam Importance (%)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=260, margin=dict(l=10, r=10, b=10, t=40))
    
    # Chart 2: Hardness Level (Bar Chart - ADDED OPTION)
    hardness_values = [topic_data[t]["hardness"] for t in selected_topics]
    fig_bar = go.Figure(data=[go.Bar(x=labels, y=hardness_values, marker_color='#f43f5e')])
    fig_bar.update_layout(title="Topic Hardness Index (1-100)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=260, margin=dict(l=10, r=10, b=10, t=40))
    
    with col_chart1:
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_chart2:
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("Please select at least one topic to view analytics.")

st.write("---")

# 📚 ৬. গ্লোবাল লেকচার ডাটাবেস এবং ইন্টারঅ্যাক্টিভ লেসন জেনারেটর (বাংলা + English + Diagrams)
st.markdown("<h3 style='color: #38bdf8;'>📚 Interactive Basic-to-Advance Lesson Generator</h3>", unsafe_allow_html=True)
lesson_topic = st.selectbox("📖 Choose a topic to learn:", list(topic_data.keys()))

global_lecture_db = {
    "Recurrence Relations": r"""### 📘 Masterclass Lecture: Recurrence Relations (পুনরাবৃত্তি সম্পর্ক)
#### **১. ভূমিকা ও বেসিক লেভেল (Basic Introduction):**
একটি পুনরাবৃত্তি সম্পর্ক (Recurrence Relation) হলো এমন একটি গাণিতিক সমীকরণ যা কোনো সিকোয়েন্সের $n$-তম পদকে তার পূর্ববর্তী পদগুলোর (যেমন: $a_{n-1}, a_{n-2}$) মাধ্যমে প্রকাশ করে।
* **CSE Application:** এটি অ্যালগরিদমের টাইম কমপ্লেক্সিটি (যেমন: Divide and Conquer, Merge Sort) বের করতে ব্যবহৃত হয়।

#### **২. ইন্টারঅ্যাক্টিভ মডেল ও ডায়াগ্রাম (Visual Representation):**
