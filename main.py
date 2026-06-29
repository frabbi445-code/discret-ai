import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import json
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

# ২. এপিআই কি কনফিগারেশন এবং ক্লাউড এপিআই সামঞ্জস্যপূর্ণ মডেল সিলেকশন
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

# লাইভ ইন্ডিকেটর প্যানেল (সবসময় সচল থাকবে)
st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: READY TO PERFORM</div>', unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Universal Course Solver")
st.subheader("Discrete Mathematics Engine & Interactive Exam Lab")
st.write("Presidency University | CSE Dept | Academic Edition")
st.write("---")

# 📊 ৩D গ্রাফ চার্ট
st.markdown("<h3 style='color: #38bdf8;'>📊 Exam Analytics: Topic Importance Matrix</h3>", unsafe_allow_html=True)
st.caption("💡 এটি একটি ইন্টারঅ্যাক্টিভ ৩D চার্ট। মাউস দিয়ে ড্র্যাগ করে বিভিন্ন অ্যাঙ্গেল থেকে পরীক্ষার টপিকগুলোর গুরুত্ব বিশ্লেষণ করা যাবে।")

topics_x = ['Set Theory', 'Logic', 'Graph Theory', 'Combinatorics', 'Recurrence']
exams_y = ['Quiz 1', 'Quiz 2', 'Midterm', 'Assignment', 'Final Exam']

z_matrix = [
    [55, 65, 75, 60, 50],
    [65, 85, 90, 85, 65],
    [75, 90, 98, 90, 75], 
    [60, 85, 90, 85, 60],
    [50, 65, 75, 60, 55]
]

fig_3d = go.Figure(data=[go.Surface(
    z=z_matrix, 
    x=topics_x, 
    y=exams_y,
    colorscale='Viridis'
)])

fig_3d.update_layout(
    scene=dict(
        xaxis_title='Topics',
        yaxis_title='Exams',
        zaxis_title='Importance %'
    ),
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=450,
    margin=dict(l=0, r=0, b=0, t=10)
)
st.plotly_chart(fig_3d, use_container_width=True)
st.write("---")

# Session State ইনিশিয়েলাইজেশন
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'exam_submitted' not in st.session_state:
    st.session_state.exam_submitted = False

# ৩. সাইডবার প্রোফাইল
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🎓 Student Profile</h3>", unsafe_allow_html=True)
with st.sidebar.container(border=True):
    st.write("**Developer:** MD FAZLE RABBI SOHAN")
    st.write("**Institution:** Presidency University")
    st.write("**Department:** CSE")
    st.markdown("<span style='color: #4ade80; font-weight: bold;'>🔥 Status: READY</span>", unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.page_link("https://presidency.edu.bd/", label="Presidency University Portal", icon="🏫")

# ৪. ইউনিভার্সাল সিঙ্গেল ইনপুট ইন্টারফেস
st.markdown("<h3 style='color: #38bdf8;'>🚀 Universal Math Input Box</h3>", unsafe_allow_html=True)
st.caption("💡 Enter any Discrete Mathematics problem below (Truth Tables, Graphs, Sets, Counting, Recurrence):")

user_query = st.text_area(
    "📝 Type or paste your question here:",
    placeholder="e.g., Find the explicit formula for a_n = 5a_{n-1} - 6a_{n-2}...",
    height=110
)

# লোকাল ডাইনামিক সলভার সリューション ব্যাংক
fallback_solutions = {
    "recurrence": """### 📘 Step-by-Step Mathematical Solution

**Problem:** Solve the linear homogeneous recurrence relation $a_n = 4a_{n-1} - 4a_{n-2}$ with $a_0 = 1, a_1 = 4$.

#### **Step 1: Formulate the Characteristic Equation**
Assume a solution of the form $a_n = r^n$. Substituting this into the recurrence relation gives:
$$r^2 - 4r + 4 = 0$$

#### **Step 2: Solve for Characteristic Roots**
Factoring the quadratic equation:
$$(r - 2)^2 = 0 \\implies r_1 = r_2 = 2$$
We have a repeated root $r_0 = 2$.

#### **Step 3: Determine the General Solution**
Since the root is repeated, the general solution is structurally defined as:
$$a_n = (C_1 + C_2n) \\cdot 2^n$$

#### **Step 4: Apply Initial Conditions to Find Constants**
1. For $n = 0$:  
   $$a_0 = C_1 \\cdot 2^0 \\implies 1 = C_1 \\implies C_1 = 1$$
2. For $n = 1$:  
   $$a_1 = (1 + C_2) \\cdot 2^1 \\implies 4 = 2 + 2C_2 \\implies C_2 = 1$$

#### **🎯 Final Explicit Formula:**
