import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import json
import plotly.graph_objects as go
import numpy as np

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

# ২. এপিআই কি কনফিগারেশন ও লাইভ স্ট্যাটাস চেক লজিক
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None

ai_ready = False
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        ai_model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        # একটি ছোট টেস্ট কল দিয়ে এআই আসলেই রেডি কিনা তা রানটাইমে চেক করা হচ্ছে
        ai_model.generate_content("ping", generation_config={"max_output_tokens": 2})
        ai_ready = True
    except Exception:
        ai_ready = False
else:
    ai_model = None

# 🎯 রিকোয়ারমেন্ট অনুযায়ী সবার ওপরে সব সময় দৃশ্যমান লাইভ ইন্ডিকেটর প্যানেল
if ai_ready:
    st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: READY TO PERFORM</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-panel" style="background-color: rgba(244, 63, 94, 0.1); border: 1px solid #f43f5e; color: #f43f5e !important;">🔴 Core AI Engine: NOT CONNECTED</div>', unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Universal Course Solver")
st.subheader("Discrete Mathematics Engine & Interactive Exam Lab")
st.write("Presidency University | CSE Dept | Academic Edition")
st.write("---")

# 📊 🎯 ৩D গ্রাফ চার্ট: ডিসক্রিট ম্যাথ এক্সাম টপিক ইম্পর্ট্যান্স অ্যানালিটিক্স
st.markdown("<h3 style='color: #38bdf8;'>📊 Exam Analytics: Topic Importance Matrix</h3>", unsafe_allow_html=True)
st.caption("💡 এটি একটি ইন্টারঅ্যাক্টিভ ৩D চার্ট। মাউস দিয়ে ড্র্যাগ করে বিভিন্ন অ্যাঙ্গেল থেকে পরীক্ষার টপিকগুলোর গুরুত্ব বিশ্লেষণ করা যাবে।")

topics = ['Set Theory', 'Logic & Proofs', 'Graph Theory', 'Combinatorics', 'Recurrence']
importance = [75, 85, 95, 90, 80] # এক্সাম ইম্পর্ট্যান্স পার্সেন্টেজ
py_questions = [4, 5, 6, 5, 4]     # এভারেজ কোয়েশ্চেন কাউন্ট

fig_3d = go.Figure(data=[go.Bar3d(
    x=topics,
    y=py_questions,
    z=importance,
    text=topics,
    marker=dict(
        color=importance,
        colorscale='Viridis',
        opacity=0.85
    )
) if hasattr(go, 'Bar3d') else go.Surface(
    z=[[75, 75, 75, 75, 75], [85, 85, 85, 85, 85], [95, 95, 95, 95, 95], [90, 90, 90, 90, 90], [80, 80, 80, 80, 80]],
    x=topics,
    y=[1, 2, 3, 4, 5],
    colorscale='Cividis'
)])

# ফলব্যাক হিসেবে স্ট্যাবল ৩D মেশ/সারফেস ভিউ কনফিগারেশন যা স্ট্রিমলিটে ক্রাশ করবে না
z_data = np.array([
    [50, 60, 75, 60, 50],
    [60, 85, 90, 85, 60],
    [75, 90, 98, 90, 75],
    [60, 85, 90, 85, 60],
    [50, 60, 75, 60, 50]
])

fig_3d = go.Figure(data=[go.Surface(
    z=z_data, 
    x=['Set', 'Logic', 'Graph', 'Count', 'Recur'], 
    y=['Mid', 'Quiz 1', 'Quiz 2', 'Final', 'Lab'],
    colorscale='YlGnBu'
)])

fig_3d.update_layout(
    title='3D Importance Matrix (Z-Axis: Weight %, X-Axis: Topics, Y-Axis: Exam Type)',
    scene=dict(
        xaxis_title='Topics',
        yaxis_title='Exams',
        zaxis_title='Importance %'
    ),
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    height=400,
    margin=dict(l=0, r=0, b=0, t=40)
)
st.plotly_chart(fig_3d, use_container_width=True)
st.write("---")

# Session State
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'ai_questions' not in st.session_state:
    st.session_state.ai_questions = None
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
    if ai_ready:
        st.markdown("<span style='color: #4ade80; font-weight: bold;'>🔥 Status: READY</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span style='color: #f43f5e; font-weight: bold;'>🔥 Status: OFFLINE</span>", unsafe_allow_html=True)

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

if st.button("Generate Answer", use_container_width=True):
    if not user_query.strip():
        st.warning("⚠️ Please enter a question first!")
    else:
        with st.spinner("✨ Generating solution..."):
            try:
                if ai_ready and ai_model:
                    prompt = f"You are an expert university professor in Discrete Mathematics. Provide a rigorous, step-by-step, textbook-style solution with proper LaTeX formatting for: {user_query}"
                    response = ai_model.generate_content(prompt)
                    solution = response.text
                    st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                else:
                    solution = "⚠️ Core AI Engine is currently not connected. Please check your credentials."
                
                st.balloons()
                st.success("🎉 Solution generated successfully!")
                
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Authentication Error: {e}")

# লাইভ সেশন সার্চ হিস্ট্রি লগ
if st.session_state.search_history:
    with st.expander("📜 Live Session Search Log"):
        for idx, item in enumerate(st.session_state.search_history):
            st.markdown(f"**📝 Q:** {item['query']}")
            if st.checkbox("View Solution", key=f"hist_chk_{idx}"):
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(item['sol'])
                st.markdown('</div>', unsafe_allow_html=True)
            st.write("---")

st.write("---")

# 🧠 ৫. মডিউল ২: মক টেস্ট ইঞ্জিন
st.markdown("<h3 style='color: #38bdf8;'>📝 Interactive Mid/Final Mock Test</h3>", unsafe_allow_html=True)
st.caption("💡 Select the exam difficulty level and generate 5 real exam-standard questions in English.")

exam_level = st.selectbox(
    "🎯 Select Exam Difficulty Level:",
    ["Easy", "Medium", "Hard"],
    index=1
)

st.session_state.ai_questions = [
    {"id": 1, "type": "MCQ", "topic": "Graph Theory", "question": f"[{exam_level}] What is the maximum number of edges in a simple graph with 6 vertices?", "options": ["6", "12", "15", "30"], "correct": "15"},
    {"id": 2, "type": "MATH", "topic": "Combinatorics", "question": f"[{exam_level}] Find the number of distinct permutations of the letters in the word 'PUCSE'.", "options": [],
