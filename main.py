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
ai_model = None
connection_error_msg = ""
used_model_name = ""

if final_key:
    clean_key = str(final_key).strip().replace('"', '').replace("'", "")
    try:
        genai.configure(api_key=clean_key)
        
        # AQ কী-র জন্য নির্দিষ্ট মডেল পাথ অ্যাসাইন
        if clean_key.startswith("AQ"):
            model_name = 'models/gemini-1.5-flash-latest'
        else:
            model_name = 'gemini-1.5-flash'
            
        used_model_name = model_name
        ai_model = genai.GenerativeModel(model_name=model_name)
        
        # লাইভ কানেক্টিভিটি টেস্ট পিং কল
        test_resp = ai_model.generate_content("Ping", generation_config={"max_output_tokens": 5})
        if test_resp:
            ai_ready = True
    except Exception as e:
        # ফার্স্ট ট্রাই ফেইল করলে অল্টারনেটিভ এন্ডপয়েন্টে ট্রাই করবে
        try:
            model_name = 'models/gemini-1.5-pro-latest'
            ai_model = genai.GenerativeModel(model_name=model_name)
            test_resp = ai_model.generate_content("Ping", generation_config={"max_output_tokens": 5})
            if test_resp:
                ai_ready = True
                used_model_name = 'gemini-1.5-pro-latest'
        except Exception as inner_e:
            ai_ready = False
            connection_error_msg = f"Primary Error: {str(e)} | Fallback Error: {str(inner_e)}"
else:
    connection_error_msg = "No API Key detected in st.secrets or manual input field."

# সবার ওপরে দৃশ্যমান লাইভ ইন্ডিকেটর প্যানেল
if ai_ready:
    st.markdown(f'<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: READY TO PERFORM ({used_model_name})</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="status-panel" style="background-color: rgba(244, 63, 94, 0.1); border: 1px solid #f43f5e; color: #f43f5e !important;">🔴 Core AI Engine: NOT CONNECTED<br><span style="font-size:12px; font-weight:normal; color:#fda4af !important;">Reason: {connection_error_msg}</span></div>', unsafe_allow_html=True)

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
                if ai_ready and ai_model:
                    prompt = f"You are an expert university professor in Discrete Mathematics. Provide a rigorous, step-by-step, textbook-style solution with proper LaTeX formatting for: {user_query}"
                    response = ai_model.generate_content(prompt)
                    solution = response.text
                    st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                    
                    st.balloons()
                    st.success("🎉 Solution generated successfully!")
                    
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown(solution)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("⚠️ Core AI Engine is currently not connected. Please check your API Key.")
                
            except Exception as e:
                st.error(f"❌ Core AI Engine Execution Error: {e}")

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
st.markdown("<h3 style='color: #38bdf8;'>📝 Interactive Mid/Final Mock Test</h3>
