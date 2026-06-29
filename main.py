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
            model_name = "models/gemini-1.5-flash-latest"
        else:
            model_name = "gemini-1.5-flash"
            
        used_model_name = model_name
        ai_model = genai.GenerativeModel(model_name=model_name)
        
        # লাইভ কানেক্টিভিটি টেস্ট পিং কল
        test_resp = ai_model.generate_content("Ping", generation_config={"max_output_tokens": 5})
        if test_resp:
            ai_ready = True
    except Exception as e:
        # ফার্স্ট ট্রাই ফেইল করলে অল্টারনেティブ এন্ডপয়েন্টে ট্রাই করবে
        try:
            model_name = "models/gemini-1.5-pro-latest"
            ai_model = genai.GenerativeModel(model_name=model_name)
            test_resp = ai_model.generate_content("Ping", generation_config={"max_output_tokens": 5})
            if test_resp:
                ai_ready = True
                used_model_name = "gemini-1.5-pro-latest"
        except Exception as inner_e:
            ai_ready = False
            connection_error_msg = f"Primary Error: {str(e)} | Fallback Error: {str(inner_e)}"
else:
    connection_error_msg = "No API Key detected in st.secrets or manual input field."

# ট্রিপল কোটেশন ব্যবহার করে স্ট্যাটাস প্যানেলের ভেতরের জটিল কোটেশন বাগ দূর করা হলো
if ai_ready:
    status_html = f"""
    <div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">
        🟢 Core AI Engine: READY TO PERFORM ({used_model_name})
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
st.markdown("<h3 style='color: #38bdf8;'>📝 Interactive Mid/Final Mock Test</h3>", unsafe_allow_html=True)
st.caption("💡 Select the exam difficulty level and generate 5 real exam-standard questions in English.")

levels_list = ["Easy", "Medium", "Hard"]
if st.session_state.current_level in levels_list:
    selected_idx = levels_list.index(st.session_state.current_level)
else:
    selected_idx = 1

exam_level = st.selectbox(
    "🎯 Select Exam Difficulty Level:",
    levels_list,
    index=selected_idx
)

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
        st.info(f"⏱️ Exam Regulations: Answer all 5 [{exam_level}] level questions below. No negative marking.")
        
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
    
    fig = go.Figure(data=[go.Pie(
        labels=['Correct', 'Incorrect'], 
        values=[score, wrong], 
        hole=.4,
        marker_colors=['#4ade80', '#f43f5e']
    )])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    success_rate = (score / total_q) * 100
    if score == 5:
        grade, color, bg_card = "A+", "#4ade80", "rgba(74, 222, 128, 0.1)"
        feedback = f"Outstanding performance! Your preparation for {exam_level} level questions is 100% perfect. Keep it up!"
    elif score >= 4:
        grade, color, bg_card = "A", "#38bdf8", "rgba(56, 189, 248, 0.1)"
        feedback = f"Excellent job! Your core concepts are highly clear for {exam_level} level problems. Review the minor mistakes to target full marks."
    elif score >= 2:
        grade, color, bg_card = "B", "#fbbf24", "rgba(251, 191, 36, 0.1)"
        feedback = f"Moderate performance. There are gaps in your understanding of {exam_level} level topics. We recommend revising your lecture sheets."
    else:
        grade, color, bg_card = "F (Fail)", "#f43f5e", "rgba(244, 63, 94, 0.1)"
        feedback = f"Unsatisfactory score. You need to rebuild your foundational understanding of {exam_level} level concepts. Use the Universal Math Solver to practice more."

    # রিপোর্ট কার্ড জেনারেশনের জন্য ট্রিপল কোটেশন ব্লক ব্যবহার করে কোটেশন কনফ্লিক্ট দূর করা হলো
    report_html = f"""
        <div style="background:{bg_card}; border:1px solid {color}; padding:20px; border-radius:8px; margin-bottom:25px;">
            <h3 style="color:{color}; margin-top:0; font-weight:600;">📊 Comprehensive Exam Report Card</h3>
            <p style="font-size:16px; color:#e2e8f0; margin:5px 0;"><b>Examinee:</b> MD FAZLE RABBI SOHAN</p>
            <p style="font-size:16px; color:#e2e8f0; margin:5px 0;"><b>Exam Level:</b> {exam_level}</p>
            <p style="font-size:16px; color:#e2e8f0; margin:5px 0;"><b>Final Score:</b> <span style="color:{color}; font-weight:bold;">{score} / {total_q}</span> ({int(success_rate)}% Accuracy)</p>
            <p style="font-size:18px; color:#e2e8f0; margin:10px 0;"><b>Grade:</b> <span style="background:{color}; color:#000; padding:2px 12px; border-radius:4px; font-weight:bold;">{grade}</span></p>
            <hr style="border-color:{color}; opacity:0.2;">
            <p style="font-style:italic; color:#cbd5e1; margin-bottom:0;"><b>🗣️ Academic Feedback & Guidance:</b> {feedback}</p>
        </div>
    """
    st.markdown(report_html, unsafe_allow_html=True)
    
    with st.expander("🔍 Detailed Answer Sheet Review"):
        st.dataframe(pd.DataFrame(detailed_report), use_container_width=True)
    
    if st.button("🔄 Take Another AI Test"):
        st.session_state.exam_submitted = False
        st.session_state.ai_questions = None
        st.rerun()

st.write("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Developed by MD FAZLE RABBI SOHAN | PU CSE Innovation Lab</p>", unsafe_allow_html=True)
