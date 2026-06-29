import streamlit as st
import requests
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

# ২. ডাবল-লেয়ার এপিআই কি কনফিগারেশন রুটিন (Secrets + Manual Input)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None

# সাইডবারে ব্যাকআপ ম্যানুয়াল এপিআই কী ইনপুট বক্স
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🔑 API Configuration</h3>", unsafe_allow_html=True)
manual_key = st.sidebar.text_input("Enter Gemini API Key (If offline):", type="password", help="If st.secrets fails, paste your key here.")

# যেকোনো একটি কী পেলেই কনফিগারেশন রান করবে
final_key = manual_key.strip() if manual_key.strip() else (GEMINI_API_KEY if GEMINI_API_KEY else "")

ai_ready = False
connection_error_msg = ""
used_gateway = "v1 API Gateway"

# ট্রিপল-রুট আল্ট্রা ডিফেন্সিভ জেমিনি REST API রিকোয়েস্ট ফাংশন
def call_gemini_rest(prompt_text, api_key, route_index=1):
    # রুট ১: স্ট্যান্ডার্ড v1 গেটওয়ে (gemini-1.5-flash)
    if route_index == 1:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    # রুট ২: অল্টারনেটিভ v1beta গেটওয়ে (gemini-1.5-flash)
    elif route_index == 2:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    # রুট ৩: লেগেসি গেটওয়ে ফলব্যাক (gemini-pro)
    else:
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}"

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        if response.status_code == 200:
            res_json = response.json()
            return res_json['candidates'][0]['content']['parts'][0]['text'], True, route_index
        else:
            # যদি কারেন্ট রুট ফেইল করে, পরের রুটে ট্রাই করবে (রুট ৩ পর্যন্ত)
            if route_index < 3:
                return call_gemini_rest(prompt_text, api_key, route_index = route_index + 1)
            # সব রুট ফেইল করলে আসল এরর মেসেজ রিটার্ন করবে
            return f"HTTP {response.status_code} - {response.text}", False, route_index
    except Exception as exc:
        if route_index < 3:
            return call_gemini_rest(prompt_text, api_key, route_index = route_index + 1)
        return str(exc), False, route_index

# লাইভ কানেক্টিভিটি ভ্যালিডেশন টেস্ট পিং কল
if final_key:
    clean_key = str(final_key).strip().replace('"', '').replace("'", "")
    test_output, is_ok, successful_route = call_gemini_rest("Ping", clean_key, route_index=1)
    if is_ok:
        ai_ready = True
        if successful_route == 1: used_gateway = "v1 (1.5-flash)"
        elif successful_route == 2: used_gateway = "v1beta (1.5-flash)"
        else: used_gateway = "v1 (gemini-pro)"
    else:
        connection_error_msg = test_output
else:
    connection_error_msg = "No API Key detected in st.secrets or manual input field."

# স্ট্যাটাস প্যানেল রেন্ডারিং (সবুজ সিগন্যাল ফিক্স)
if ai_ready:
    status_html = f"""
    <div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">
        🟢 Core AI Engine: READY TO PERFORM ({used_gateway} Gateway Connected)
    </div>
    """
    st.markdown(status_html, unsafe_allow_html=True)
else:
    status_html = f"""
    <div class="status-panel" style="background-color: rgba(244, 63, 94, 0.1); border: 1px solid #f43f5e; color: #f43f5e !important;">
        🔴 Core AI Engine: NOT CONNECTED<br>
        <span style="font-size:12px; font-weight:normal; color:#fda4af !important;">Reason: {connection_error_msg}</span>
    </div>
    """
    st.markdown(status_html, unsafe_allow_html=True)

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

# Session State ইনিশিয়ালাইজেশন
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'ai_questions' not in st.session_state:
    st.session_state.ai_questions = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'exam_submitted' not in st.session_state:
    st.session_state.exam_submitted = False
if 'current_level' not in st.session_state:
    st.session_state.current_level = "Medium"

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
                if ai_ready and final_key:
                    clean_key = str(final_key).strip().replace('"', '').replace("'", "")
                    prompt = f"You are an expert university professor in Discrete Mathematics. Provide a rigorous, step-by-step, textbook-style solution with proper LaTeX formatting for: {user_query}"
                    
                    # অ্যাপের ভেতরেও আল্ট্রা ফলব্যাক গেটওয়ে কল
                    solution, is_ok, _ = call_gemini_rest(prompt, clean_key, route_index=1)
                    
                    if is_ok:
                        st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                        st.balloons()
                        st.success("🎉 Solution generated successfully!")
                        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                        st.markdown(solution)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"❌ AI Execution
