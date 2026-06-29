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

# ২. এপিআই কি কনফিগারেশন (বিকল্প মেকানিজম)
# যদি st.secrets এ কী না থাকে, তাহলে এটি ড্যাশবোর্ড থেকে ইনপুট নেওয়া যাবে।
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = ""

# সাইডবারে ম্যানুয়াল এপিআই কী ইনপুট বক্স
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🔑 API Configuration</h3>", unsafe_allow_html=True)
manual_key = st.sidebar.text_input("Enter Valid Gemini API Key:", type="password", help="Enter a valid API key starting with AIzaSy...")

# ফাইনাল কি চুজ করা
final_key = manual_key.strip() if manual_key.strip() else GEMINI_API_KEY.strip()

ai_ready = False
connection_error_msg = ""
used_gateway = "v1beta API Gateway"

# জেমিনি REST API রিকোয়েস্ট ফাংশন 
def call_gemini_rest(prompt_text, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        if response.status_code == 200:
            res_json = response.json()
            if 'candidates' in res_json and len(res_json['candidates']) > 0:
                text_out = res_json['candidates'][0]['content']['parts'][0]['text']
                return text_out, True
            else:
                return "No text candidates returned.", False
        elif response.status_code == 401:
            return "Invalid API Key. Please use a valid Google AI Studio Key (starts with AIzaSy).", False
        else:
            return f"Error {response.status_code}: {response.text}", False
    except Exception as exc:
        return str(exc), False

# লাইভ কানেক্টিভিটি টেস্ট পিং কল
if final_key:
    test_output, is_ok = call_gemini_rest("Ping", final_key)
    if is_ok:
        ai_ready = True
        used_gateway = "v1beta (Gemini 1.5 Flash)"
    else:
        connection_error_msg = test_output
else:
    connection_error_msg = "Please provide a valid Gemini API key in the sidebar or st.secrets."

# স্ট্যাটাস প্যানেল রেন্ডারিং
if ai_ready:
    status_msg = f"🟢 Core AI Engine: READY TO PERFORM ({used_gateway} Gateway Connected)"
    st.markdown(f'<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">{status_msg}</div>', unsafe_allow_html=True)
else:
    status_msg = f"🔴 Core AI Engine: NOT CONNECTED<br><span style=\'font-size:12px; font-weight:normal; color:#fda4af !important;\'>Reason: {connection_error_msg}</span>"
    st.markdown(f'<div class="status-panel" style="background-color: rgba(244, 63, 94, 0.1); border: 1px solid #f43f5e; color: #f43f5e !important;">{status_msg}</div>', unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Universal Course Solver")
st.subheader("Discrete Mathematics Engine & Interactive Exam Lab")
st.write("Presidency University | CSE Dept | Academic Edition")
st.write("---")

# 📊 ৩D গ্রাফ চার্ট
st.markdown("<h3 style='color: #38bdf8;'>📊 Exam Analytics: Topic Importance Matrix</h3>", unsafe_allow_html=True)

topics_x = ['Set Theory', 'Logic', 'Graph Theory', 'Combinatorics', 'Recurrence']
exams_y = ['Quiz 1', 'Quiz 2', 'Midterm', 'Assignment', 'Final Exam']
z_matrix = [
    [55, 65, 75, 60, 50],
    [65, 85, 90, 85, 65],
    [75, 90, 98, 90, 75], 
    [60, 85, 90, 85, 60],
    [50, 65, 75, 60, 55]
]

fig_3d = go.Figure(data=[go.Surface(z=z_matrix, x=topics_x, y=exams_y, colorscale='Viridis')])
fig_3d.update_layout(
    scene=dict(xaxis_title='Topics', yaxis_title='Exams', zaxis_title='Importance %'),
    template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400, margin=dict(l=0, r=0, b=0, t=10)
)
st.plotly_chart(fig_3d, use_container_width=True)
st.write("---")

# Session State
if 'search_history' not in st.session_state: st.session_state.search_history = []
if 'ai_questions' not in st.session_state: st.session_state.ai_questions = None
if 'user_answers' not in st.session_state: st.session_state.user_answers = {}
if 'exam_submitted' not in st.session_state: st.session_state.exam_submitted = False
if 'current_level' not in st.session_state: st.session_state.current_level = "Medium"

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
user_query = st.text_area("📝 Type or paste your question here:", placeholder="e.g., Find the explicit formula...", height=110)

if st.button("Generate Answer", use_container_width=True):
    if not user_query.strip():
        st.warning("⚠️ Please enter a question first!")
    else:
        with st.spinner("✨ Generating solution..."):
            if ai_ready and final_key:
                prompt = f"You are an expert university professor in Discrete Mathematics. Provide a rigorous, textbook solution with LaTeX formatting for: {user_query}"
                solution, is_ok = call_gemini_rest(prompt, final_key)
                if is_ok:
                    st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                    st.balloons()
                    st.success("🎉 Solution generated successfully!")
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown(solution)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error(f"❌ AI Error: {solution}")
            else:
                st.error("⚠️ Core AI Engine is not connected. Please put a valid Key in the sidebar input box.")

# সার্চ হিস্ট্রি লগ
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

# ৫. মডিউল ২: মক টেস্ট ইঞ্জিন
st.markdown("<h3 style='color: #38bdf8;'>📝 Interactive Mock Test</h3>", unsafe_allow_html=True)
levels_list = ["Easy", "Medium", "Hard"]
selected_idx = levels_list.index(st.session_state.current_level) if st.session_state.current_level in levels_list else 1

exam_level = st.selectbox("🎯 Select Exam Difficulty Level:", levels_list, index=selected_idx)

if exam_level != st.session_state.current_level or st.session_state.ai_questions is None:
    st.session_state.current_level = exam_level
    st.session_state.ai_questions = [
        {"id": 1, "type": "MCQ", "topic": "Graph Theory", "question": f"[{exam_level}] What is the maximum number of edges in a simple graph with 6 vertices?", "options": ["6", "12", "15", "30"], "correct": "15"},
        {"id": 2, "type": "MATH", "topic": "Combinatorics", "question": f"[{exam_level}] Find the number of distinct permutations of the letters in the word 'PUCSE'.", "options": [], "correct": "120"},
        {"id": 3, "type": "MCQ", "topic": "Set Theory", "question": f"[{exam_level}] If set A has 3 elements, how many elements are in the power set P(A)?", "options": ["3", "6", "8", "9"], "correct": "8"},
        {"id": 4, "type": "MATH", "topic": "Logic", "question": f"[{exam_level}] How many rows will a truth table have for a proposition containing 4 distinct variables?", "options": [], "correct": "16"},
        {"id": 5, "type": "MCQ", "topic": "Relations", "question": f"[{exam_level}] A relation R on set A is reflexive if for all a in A, which condition holds?", "options": ["(a,a) belongs to R", "(a,b) implies (b,a)", "(a,b) and (b,c) implies (a,c)"], "correct": "(a,a) belongs to R"}
    ]

if not st.session_state.exam_submitted:
    with st.form("dynamic_exam_form"):
        st.info(f"⏱️ Exam Regulations: Answer all 5 [{exam_level}] level questions.")
        for q in st.session_state.ai_questions:
            st.markdown(f"#### **Question {q['id']}: {q['question']}**")
            if q['type'] == "MCQ":
                st.session_state.user_answers[q['id']] = st.radio("Select answer:", q['options'], key=f"ai_q_{q['id']}")
            else:
                st.session_state.user_answers[q['id']] = st.text_input("Type numerical answer:", key=f"ai_q_{q['id']}").strip()
            st.write("---")
        if st.form_submit_button("📤 Submit Mock Test"):
            st.session_state.exam_submitted = True
            st.rerun()
elif st.session_state.exam_submitted:
    st.success("🎯 Evaluation Completed!")
    score = sum(1 for q in st.session_state.ai_questions if str(st.session_state.user_answers.get(q['id'], '')).lower() == str(q['correct']).lower())
    wrong = len(st.session_state.ai_questions) - score
    
    fig = go.Figure(data=[go.Pie(labels=['Correct', 'Incorrect'], values=[score, wrong], hole=.4, marker_colors=['#4ade80', '#f43f5e'])])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250)
    st.plotly_chart(fig, use_container_width=True)
    
    if st.button("🔄 Take Another AI Test"):
        st.session_state.exam_submitted = False
        st.session_state.ai_questions = None
        st.rerun()

st.write("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Developed by MD FAZLE RABBI SOHAN | PU CSE Innovation Lab</p>", unsafe_allow_html=True)
