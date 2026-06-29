import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import random
import json
import plotly.graph_objects as go
from datetime import datetime

# ১. পেজ সেটিংস ও উচ্চ-কন্ট্রাস্ট মার্জিত থিম (High-Contrast Theme)
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
            try:
                # পাইথন সিনট্যাক্স এরর এড়াতে প্রম্পট স্ট্রিংটি একদম সেফ রাখা হলো 
                quiz_prompt = "Generate exactly 5 university-level Discrete Mathematics exam questions in English. Mix both conceptual MCQs and numerical mathematical problems that require direct numeric answers. Provide the output strictly as a valid raw JSON list of dictionaries containing fields: id, type (MCQ or MATH), topic, question, options (list of strings, empty for MATH), and correct (string representing the correct option or numeric value). Do not include markdown wraps or backticks."
                response = ai_model.generate_content(quiz_prompt)
                clean_json = response.text.replace("```json", "").replace("```", "").strip()
                st.session_state.ai_questions = json.loads(clean_json)
                st.session_state.user_answers = {}
                st.session_state.exam_submitted = False
            except Exception:
                # ফেইলসেফ ব্যাকআপ কোয়েশ্চেন প্যাক
                st.session_state.ai_questions = [
                    {"id": 1, "type": "MCQ", "topic": "Graph Theory", "question": "What is the maximum number of edges in a simple graph with 6 vertices?", "options": ["6", "12", "15", "30"], "correct": "15"},
                    {"id": 2, "type": "MATH", "topic": "Combinatorics", "question": "Find the number of distinct permutations of the letters in the word 'PUCSE'.", "options": [], "correct": "120"},
                    {"id": 3, "type": "MCQ", "topic": "Set Theory", "question": "If set A has 3 elements, how many elements are in the power set P(A)?", "options": ["3", "6", "8", "9"], "correct": "8"},
                    {"id": 4, "type": "MATH", "topic": "Logic", "question": "How many rows will a truth table have for a proposition containing 4 distinct variables?", "options": [], "correct": "16"},
                    {"id": 5, "type": "MCQ", "topic": "Relations", "question": "A relation R on set A is reflexive if for all a in A, which condition holds?", "options": ["(a,a) belongs to R", "(a,b) implies (b,a)", "(a,b) and (b,c) implies (a,c)"], "correct": "(a,a) belongs to R"}
                ]
    else:
        # রানটাইম যেন ক্রাশ না করে সেজন্য ব্যাকআপ লোড লজিক
        st.session_state.ai_questions = [
            {"id": 1, "type": "MCQ", "topic": "Graph Theory", "question": "What is the maximum number of edges in a simple graph with 6 vertices?", "options": ["6", "12", "15", "30"], "correct": "15"},
            {"id": 2, "type": "MATH", "topic": "Combinatorics", "question": "Find the number of distinct permutations of the letters in the word 'PUCSE'.", "options": [], "correct": "120"},
            {"id": 3, "type": "MCQ", "topic": "Set Theory", "question": "If set A has 3 elements, how many elements are in the power set P(A)?", "options": ["3", "6", "8", "9"], "correct": "8"},
            {"id": 4, "type": "MATH", "topic": "Logic", "question": "How many rows will a truth table have for a proposition containing 4 distinct variables?", "options": [], "correct": "16"},
            {"id": 5, "type": "MCQ", "topic": "Relations", "question": "A relation R on set A is reflexive if for all a in A, which condition holds?", "options": ["(a,a) belongs to R", "(a,b) implies (b,a)", "(a,b) and (b,c) implies (a,c)"], "correct": "(a,a) belongs to R"}
        ]

# মক টেস্ট ফর্ম ইন্টারফেস
if st.session_state.ai_questions and not st.session_state.exam_submitted:
    with st.form("dynamic_exam_form"):
        st.info("⏱️ Exam Regulations: Answer all 5 university-standard questions below. No negative marking.")
        
        for q in st.session_state.ai_questions:
            st.markdown(f"#### **Question {q['id']}: {q['question']}**")
            st.markdown(f"<span style='background-color:#334155; padding:2px 6px; border-radius:4px; color:#38bdf8; font-size:13px;'>🏷️ {q['topic']} | Type: {q['type']}</span>", unsafe_allow_html=True)
            
            if q['type'] == "MCQ":
                st.session_state.user_answers[q['id']] = st.radio(
                    "Select your answer:", q['options'], key=f"ai_q_{q['id']}"
                )
            else:
                st.session_state.user_answers[q['id']] = st.text_input(
                    "Type your numerical/final answer here:", key=f"ai_q_{q['id']}"
                ).strip()
            st.write("---")
            
        if st.form_submit_button("📤 Submit Mock Test"):
            st.session_state.exam_submitted = True
            st.rerun()

elif st.session_state.exam_submitted:
    st.success("🎯 Evaluation Completed! Check your interactive report below:")
    
    score = 0
    total_q = len(st.session_state.ai_questions)
    detailed_report = []
    
    for q in st.session_state.ai_questions:
        u_ans = st.session_state.user_answers.get(q['id'], "")
        is_correct = str(u_ans).lower() == str(q['correct']).lower()
        if is_correct:
            score += 1
        detailed_report.append({
            "Question": q['question'],
            "Your Answer": u_ans,
            "Correct Answer": q['correct'],
            "Result": "✅ Correct" if is_correct else "❌ Incorrect"
        })
            
    wrong = total_q - score
    
    # ডাইনামিক প্লটলি চার্ট
    fig = go.Figure(data=[go.Pie(
        labels=['Correct', 'Incorrect'], 
        values=[score, wrong], 
        hole=.4,
        marker_colors=['#4ade80', '#f43f5e']
    )])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    st.metric(label="Final Score", value=f"{score} / {total_q}")
    
    with st.expander("🔍 Detailed Answer Sheet Review"):
        st.dataframe(pd.DataFrame(detailed_report), use_container_width=True)
    
    if st.button("🔄 Take Another AI Test"):
        st.session_state.ai_questions = None
        st.session_state.exam_submitted = False
        st.rerun()

st.write("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Developed by MD FAZLE RABBI SOHAN | PU CSE Innovation Lab</p>", unsafe_allow_html=True)
