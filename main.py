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

# ২. এপিআই কি কনফিগারেশন এবং ক্লাউড রেস্ট ট্রান্সপোর্ট মেথড এনফোর্সমেন্ট
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None

ai_ready = False
ai_model = None

if GEMINI_API_KEY:
    clean_key = str(GEMINI_API_KEY).strip().replace('"', '').replace("'", "")
    try:
        # 🛠️ এপিআই কী সচল করার জন্য REST ক্লাউড ট্রান্সপোর্ট আর্কিটেকচার ফোর্স করা হলো
        genai.configure(api_key=clean_key, transport="rest")
        ai_model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # ১-টোকেন রিয়েল লাইভ সার্ভার রিকোয়েস্ট টেস্ট
        test_ping = ai_model.generate_content("Hi", generation_config={"max_output_tokens": 1})
        if test_ping:
            ai_ready = True
    except Exception:
        ai_ready = False

# 🟢/🔴 লাইভ ইন্ডিকেটর উইজেট প্যানেল (যা এপিআই এর আসল রেসপন্স ট্র্যাকিং এর ওপর ভিত্তি করে কাজ করবে)
if ai_ready:
    st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: CONNECTED & ONLINE</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-panel" style="background-color: rgba(244, 63, 94, 0.1); border: 1px solid #f43f5e; color: #f43f5e !important;">🔴 Core AI Engine: NOT CONNECTED (Smart Fallback Operational)</div>', unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Ultimate Interactive Lab")
st.subheader("Universal Discrete Mathematics Solver & Gamified Study Suite")
st.write("Presidency University | CSE Dept | Innovation Edition")
st.write("---")

# Session State
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'exam_submitted' not in st.session_state:
    st.session_state.exam_submitted = False
if 'user_score_history' not in st.session_state:
    st.session_state.user_score_history = []

# ৩. সাইডবার প্রোফাইল ও মেডেল ট্র্যাকার
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🎓 Student Profile</h3>", unsafe_allow_html=True)
with st.sidebar.container(border=True):
    st.write("**Developer:** MD FAZLE RABBI SOHAN")
    st.write("**Institution:** Presidency University")
    st.write("**Department:** CSE")
    
    history_len = len(st.session_state.user_score_history)
    rank, badge = ("Graph Wizard 🥇", "#f59e0b") if history_len >= 3 else (("Logic Master 🥈", "#cbd5e1") if history_len >= 1 else ("Discrete Novice 🥉", "#b45309"))
    st.markdown(f"**Rank:** <span style='color:{badge}; font-weight:bold;'>{rank}</span>", unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.page_link("https://presidency.edu.bd/", label="Presidency University Portal", icon="🏫")

# 🧮 ৪. Live Interactive Truth Table Generator
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
            
        table_rows.append({"P": p, "Q": q, f"{var_1}": v1, f"{var_1} {sign} Q": res})
    
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    st.markdown(f"##### 🎯 Generated Truth Table for: `{var_1} {sign} Q`")
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 📊 ৫. সিলেবাস অ্যানালিটিক্স (পাই চার্ট সিস্টেম)
st.markdown("<h3 style='color: #38bdf8;'>📊 Exam Analytics: Syllabus Weight Matrix</h3>", unsafe_allow_html=True)

topic_data = {
    "Set Theory": {"importance": 15},
    "Propositional Logic": {"importance": 20},
    "Graph Theory": {"importance": 25},
    "Combinatorics & Counting": {"importance": 20},
    "Recurrence Relations": {"importance": 20}
}

col_list, col_chart = st.columns([1, 1.2])
with col_list:
    st.markdown("##### 🔍 Select Syllabus Topics:")
    selected_topics = [t for t in topic_data.keys() if st.checkbox(t, value=True, key=f"sync_{t}")]

if selected_topics:
    labels = selected_topics
    importance_values = [topic_data[t]["importance"] for t in selected_topics]
    
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=importance_values, hole=.3, marker_colors=['#0ea5e9', '#38bdf8', '#0284c7', '#7dd3fc', '#bae6fd'])])
    fig_pie.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=0, r=0, b=0, t=10))
    with col_chart:
        st.plotly_chart(fig_pie, use_container_width=True)

st.write("---")

# 📚 ৬. সম্পূর্ণ কাস্টমাইজড সুপার ডিটেইলড লেকচার ডাটাবেস
st.markdown("<h3 style='color: #38bdf8;'>📚 Interactive Basic-to-Advance Lesson Generator</h3>", unsafe_allow_html=True)
lesson_topic = st.selectbox("📖 Choose a topic to learn in details:", list(topic_data.keys()))

global_lessons = {
    "Set Theory": r"""### 📘 Advanced Lecture: Set Theory (সেট তত্ত্ব)
#### **১. ভূমিকা (Introduction):**
সেট হলো বাস্তব বা চিন্তাজ জগতের বস্তুর যেকোনো সুনির্ধারিত সংগ্রহ (A set is a well-defined collection of distinct objects)।
#### **২. Core Concepts & Mathematical Proofs:**
* **Power Set (পাওয়ার সেট):** দ্য সেট অফ অল সাবсеটস। উপাদান সংখ্যা $n$ হলে পাওয়ার সেটের উপাদান হবে $2^n$।
$$\text{Cartesian Product: } A \times B = \{(a, b) \mid a \in A \land b \in B\}$$
#### **🎯 Solved Example:**
If $A = \{1, 2\}$, find the Power Set $P(A)$.
$$\text{Answer: } P(A) = \{\emptyset, \{1\}, \{2\}, \{1, 2\}\}$$
#### **📚 Reference Books:**
* 📖 *Discrete Mathematics and Its Applications* by Kenneth H. Rosen — [McGraw-Hill](https://www.mheducation.com)""",

    "Propositional Logic": r"""### 📘 Advanced Lecture: Propositional Logic (প্রপোজিশনাল লজিক)
#### **১. ভূমিকা (Introduction):**
একটি প্রপোজিশন হলো এমন একটি বাক্য যা হয় সত্য অথবা মিথ্যা, কিন্তু একসাথে উভয়ই হতে পারে না।
#### **২. 📚 Core Logic Rules:**
* **Conditional Identity:**
$$P \rightarrow Q \equiv \neg P \lor Q$$
#### **📚 Reference Books:**
* 📖 *Logic and Computer Design Fundamentals* by M. Morris Mano — [Pearson](https://www.pearson.com)""",

    "Graph Theory": r"""### 📘 Advanced Lecture: Graph Theory (গ্রাফ তত্ত্ব)
#### **১. Handshaking Theorem (হ্যান্ডশেকিং থিওরেম):**
$$\sum_{v \in V} \text{deg}(v) = 2|E|$$
#### **🎯 Solved Example:**
If a simple undirected graph has 15 edges, what is the sum of degrees of all vertices?
$$\text{Sum of degrees} = 2 \times 15 = 30$$
#### **📚 Reference Books:**
* 📖 *Introduction to Graph Theory* by Douglas B. West — [Pearson](https://www.pearson.com)""",

    "Combinatorics & Counting": r"""### 📘 Advanced Lecture: Combinatorics & Counting (বিন্যাস ও সমাবেশ)
#### **১. Pigeonhole Principle (পায়রাখোপ নীতি):**
$$\lceil n/k \rceil \text{ elements distribution.}$$
#### **🎯 Solved Example:**
Among 13 people, at least how many must be born in the same month?
$$\text{Answer: } \lceil 13/12 \rceil = 2 \text{ people.}$$
#### **📚 Reference Books:**
* 📖 *Introductory Combinatorics* by Richard A. Brualdi — [Pearson](https://www.pearson.com)""",

    "Recurrence Relations": r"""### 📘 Advanced Lecture: Recurrence Relations (পুনরাবৃত্তি সম্পর্ক)
#### **১. ভূমিকা (Introduction):**
একটি পুনরাবৃত্তি সম্পর্ক হলো এমন একটি সমীকরণ যা কোনো সিকোয়েন্সের $n$-তম পদকে তার পূর্ববর্তী পদগুলোর মাধ্যমে প্রকাশ করে।
$$\text{General Formula: } a_n = C_1r_1^n + C_2r_2^n$$
#### **🎯 Solved Example:**
Solve $a_n = 5a_{n-1} - 6a_{n-2}$ with $a_0=1, a_1=5$.
* Equation: $r^2 - 5r + 6 = 0 \implies (r-2)(r-3) = 0 \implies r=2, 3$
* Final Formula: $a_n = -1 \cdot 2^n + 2 \cdot 3^n$
#### **📚 Reference Books:**
* 📖 *Discrete Mathematics and Its Applications* by Kenneth H. Rosen — [McGraw-Hill](https://www.mheducation.com)"""
}

if st.button("Generate Detailed AI Lecture Note", use_container_width=True):
    with st.spinner(f"✨ Compiling notes for {lesson_topic}..."):
        content = None
        if ai_ready and ai_model:
            try:
                prompt = f"Write a comprehensive university undergraduate lecture note on '{lesson_topic}' in a professional mix of Bengali and English. Include definitions, 2 solved mathematical examples using LaTeX formatting, and textbook references with URLs."
                resp = ai_model.generate_content(prompt)
                content = resp.text
            except Exception:
                content = None
        
        if not content:
            content = global_lessons.get(lesson_topic, "### Lecture database operational.")
            
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown(content)
        st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 🃏 ७. ডাইনামিক ফ্ল্যাশ কার্ড সূত্র রিভিশন
st.markdown("<h3 style='color: #38bdf8;'>🃏 Interactive Formula Flashcards</h3>", unsafe_allow_html=True)
flash_topic = st.selectbox("🎯 Select a topic for formula revision:", list(topic_data.keys()), key="flash_sel")

if st.button("🔄 Load Dynamic AI Flashcards", use_container_width=True):
    f_col1, f_col2 = st.columns(2)
    if "Graph" in flash_topic:
        with f_col1:
            st.markdown('<div class="flashcard"><b>💡 Handshaking Lemma</b></div>', unsafe_allow_html=True)
            st.info(r"$$\sum_{v \in V} \text{deg}(v) = 2|E|$$")
        with f_col2:
            st.markdown('<div class="flashcard"><b>💡 Euler\'s Formula</b></div>', unsafe_allow_html=True)
            st.info(r"$$V - E + F = 2$$")
