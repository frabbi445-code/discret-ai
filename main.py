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
        # ফিক্স: v1 গেটওয়ে এবং gemini-1.5-flash-latest মডেল ব্যবহার করা হয়েছে যা নতুন AQ ফরম্যাট সাপোর্ট করে
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text'], True
            return f"Gemini Error {res.status_code}: {res.text}", False
        except Exception as e: return str(e), False

    elif provider_name == "Claude":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            'content-type': 'application/json',
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01'
        }
        payload = {
            "model": "claude-3-5-haiku-latest",
            "max_tokens": 2048,
            "messages": [{"role": "user", "content": prompt_text}]
        }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                return res.json()['content'][0]['text'], True
            return f"Claude Error {res.status_code}: {res.text}", False
        except Exception as e: return str(e), False
        
    return "Unsupported Key Format or Provider.", False

# লাইভ কানেক্টিভিটি টেস্ট পিং কল
if provider and provider != "Unknown":
    test_output, is_ok = call_universal_ai("Ping", final_key, provider)
    if is_ok:
        ai_ready = True
        if provider == "OpenAI": used_gateway = "OpenAI (GPT-4o-mini)"
        elif provider == "Gemini": used_gateway = "Gemini 1.5 Flash (v1)"
        elif provider == "Claude": used_gateway = "Anthropic Claude 3.5 Haiku"
    else:
        connection_error_msg = test_output
elif provider == "Unknown":
    connection_error_msg = "Unknown API key format! Check if it's copied correctly."
else:
    connection_error_msg = "Please provide a valid OpenAI, Gemini, or Claude API key."

# স্ট্যাটাস প্যানেল রেন্ডারিং
if ai_ready:
    status_msg = f"🟢 Core AI Engine: READY TO PERFORM ({used_gateway} Gateway Connected)"
    st.markdown(f'<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">{status_msg}</div>', unsafe_allow_html=True)
else:
    status_msg = f"🔴 Core AI Engine: NOT CONNECTED<br><span style='font-size:12px; font-weight:normal; color:#fda4af !important;'>Reason: {connection_error_msg}</span>"
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
        st.markdown(f"<span style='color: #4ade80; font-weight: bold;'>🔥 Status: ONLINE ({provider})</span>", unsafe_allow_html=True)
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
            if ai_ready and final_key and provider:
                prompt = f"You are an expert university professor in Discrete Mathematics. Provide a rigorous, textbook solution with LaTeX formatting for: {user_query}"
                solution, is_ok = call_universal_ai(prompt, final_key, provider)
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
