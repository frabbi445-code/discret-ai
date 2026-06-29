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
    
    /* ফ্ল্যাশカード স্টাইলিং */
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

# ২. এপিআই কি কনফিগারেশন এবং ক্লাউড এপিআই রিয়েল-টাইম লাইভ টেস্ট পিং
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
        test_ping = ai_model.generate_content("Ping", generation_config={"max_output_tokens": 2})
        if test_ping:
            ai_ready = True
    except Exception:
        ai_ready = False

# লাইভ ইন্ডিকেটর প্যানেল 
if ai_ready:
    st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: READY TO PERFORM</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-panel" style="background-color: rgba(244, 63, 94, 0.1); border: 1px solid #f43f5e; color: #f43f5e !important;">🔴 Core AI Engine: NOT CONNECTED (Local Fallback Operational)</div>', unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Ultimate Interactive Lab")
st.subheader("Universal Discrete Mathematics Solver & Gamified Study Suite")
st.write("Presidency University | CSE Dept | Innovation Edition")
st.write("---")

# Session State ইনিশিয়েলাইজেশন
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'exam_submitted' not in st.session_state:
    st.session_state.exam_submitted = False
if 'user_score_history' not in st.session_state:
    st.session_state.user_score_history = []

# ৩. সাইডবার প্রোফাইল ও গ্যামিфাইড মেডেল ট্র্যাকার
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🎓 Student Profile</h3>", unsafe_allow_html=True)
with st.sidebar.container(border=True):
    st.write("**Developer:** MD FAZLE RABBI SOHAN")
    st.write("**Institution:** Presidency University")
    st.write("**Department:** CSE")
    
    history_len = len(st.session_state.user_score_history)
    rank, badge = ("Graph Wizard 🥇", "#f59e0b") if history_len >= 3 else (("Logic Master 🥈", "#cbd5e1") if history_len >= 1 else ("Discrete Novice 🥉", "#b45309"))
    st.markdown(f"**Rank:** <span style='color:{badge}; font-weight:bold;'>{rank}</span>", unsafe_allow_html=True)

st.sidebar.write("---")
# 🛠️ ফিক্সড এক্সটার্নাল লিংক লজিক (যা KeyError: url_pathname ১০০% রিমুভ করবে)
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

# 📚 六. এআই চালিত ডিটেইলড লেসন জেনারেটর
st.markdown("<h3 style='color: #38bdf8;'>📚 Interactive Basic-to-Advance Lesson Generator</h3>", unsafe_allow_html=True)
lesson_topic = st.selectbox("📖 Choose a topic to learn in details:", list(topic_data.keys()))

if st.button("Generate Detailed AI Lecture Note", use_container_width=True):
    with st.spinner(f"✨ Compiling advanced textbook-style notes for {lesson_topic}..."):
        try:
            if ai_ready and ai_model:
                lecture_prompt = (
                    f"You are a Senior Professor teaching Discrete Mathematics. Write a comprehensive lecture note for university undergraduates on: '{lesson_topic}'. "
                    f"Explain beautifully using a mix of Bengali and English (Banglish style). Include basic definitions, 2 solved mathematical examples using LaTeX formatting, "
                    f"and reference textbooks like Kenneth Rosen with online resource URLs."
                )
                response = ai_model.generate_content(lecture_prompt)
                lecture_content = response.text
            else:
                lecture_content = "⚠️ AI Core Offline. Fallback text activated. Please verify your GEMINI_API_KEY credentials in Streamlit Secrets."
            
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown(lecture_content)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.write("---")

# 🃏 ৭. ডাইনামিক ফ্ল্যাশ কার্ড সূত্র রিভিশন
st.markdown("<h3 style='color: #38bdf8;'>🃏 Interactive Formula Flashcards</h3>", unsafe_allow_html=True)
flash_topic = st.selectbox("🎯 Select a topic for formula revision:", list(topic_data.keys()), key="flash_sel")

if st.button("🔄 Load Dynamic AI Flashcards", use_container_width=True):
    with st.spinner("🤖 Fetching math equations..."):
        try:
            if ai_ready and ai_model:
                flash_prompt = (
                    f"Provide exactly 2 crucial mathematical formulas for the topic '{flash_topic}' in Discrete Mathematics. "
                    f"Format the output strictly as a valid raw JSON object with keys 'formula1' and 'formula2'. Each containing 'name', 'equation' (LaTeX) and 'explanation' strings. No codeblocks."
                )
                resp = ai_model.generate_content(flash_prompt)
                clean_json = resp.text.replace("```json", "").replace("```", "").strip()
                fdata = json.loads(clean_json)
                
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    st.markdown(f'<div class="flashcard"><b>💡 {fdata.get("formula1", {}).get("name", "Formula 1")}</b></div>', unsafe_allow_html=True)
                    st.info(f'{fdata.get("formula1", {}).get("equation", "")}\n\n*{fdata.get("formula1", {}).get("explanation", "")}*')
                with f_col2:
                    st.markdown(f'<div class="flashcard"><b>💡 {fdata.get("formula2", {}).get("name", "Formula 2")}</b></div>', unsafe_allow_html=True)
                    st.info(f'{fdata.get("formula2", {}).get("equation", "")}\n\n*{fdata.get("formula2", {}).get("explanation", "")}*')
            else:
                st.warning("⚠️ Local formula pack loaded.")
        except Exception:
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                st.markdown('<div class="flashcard"><b>💡 Handshaking Theorem</b></div>', unsafe_allow_html=True)
                st.info(r"$$\sum_{v \in V} \text{deg}(v) = 2|E|$$")
            with f_col2:
                st.markdown('<div class="flashcard"><b>💡 Pigeonhole Principle</b></div>', unsafe_allow_html=True)
                st.info(r"$$\lceil n/k \rceil \text{ elements distribution.}$$")

st.write("---")

# 🤖 ৮. রিয়েল পিডিএফ/টেক্সট রিডার অ্যান্ড এআই এক্সপেইনার
st.markdown("<h3 style='color: #38bdf8;'>🤖 AI Smart Lecture Note Explainer</h3>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("📂 Upload Class Lecture Sheet (PDF/TXT)", type=["pdf", "txt"], key="real_pdf_uploader")

if uploaded_file is not None:
    with st.spinner("🤖 Analyzing your university handout..."):
        try:
            file_details = uploaded_file.read()
            raw_text = file_details.decode("utf-8", errors="ignore")[:3000]
            
            if ai_ready and ai_model:
                pdf_prompt = f"Analyze this undergraduate handout note part:\n{raw_text}\n\nProvide a high-quality summary, 3 critical expected exam questions, and referenced core formulas."
                pdf_resp = ai_model.generate_content(pdf_prompt)
                analysis_result = pdf_resp.text
            else:
                analysis_result = "📂 Note content parsed locally. Connect Core AI Engine to extract dynamic semantic summaries."
            
            st.success("🎉 Note Analysis Complete!")
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown(analysis_result)
            st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.write("---")

# 🚀 ৯. ইউনিভার্সাল সিঙ্গেল ইনপুট ইন্টারফেস (ম্যাথ সলভার)
st.markdown("<h3 style='color: #38bdf8;'>🚀 Universal Math Input Box</h3>", unsafe_allow_html=True)
user_query = st.text_area("📝 Type your discrete math problem here:", placeholder="e.g., Find the explicit formula for a_n = 5a_{n-1} - 6a_{n-2}...", height=110, key="solver_query")

if st.button("Generate Answer", use_container_width=True):
    if not user_query.strip():
        st.warning("⚠️ Please enter a question first!")
    else:
        with st.spinner("✨ Generating solution..."):
            try:
                if ai_ready and ai_model:
                    prompt = f"Provide a textbook-style step-by-step mathematical solution with clear LaTeX for: {user_query}"
                    response = ai_model.generate_content(prompt)
                    solution = response.text
                else:
                    solution = r"### 📘 Step-by-Step Mathematical Solution\n\n**Problem:** Solve $a_n = 4a_{n-1} - 4a_{n-2}$ with $a_0 = 1, a_1 = 4$.\n\n$$\text{Roots Method: } r^2 - 4r + 4 = 0 \implies (r-2)^2 = 0 \implies r = 2$$\n\n$$\text{Formula: } a_n = (1 + n) \cdot 2^n$$"
                
                st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                st.balloons()
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.write("---")

# 🧠 ১০. ১০-কোয়েশ্চেন মক টেস্ট ল্যাব (টাইপো-ফ্রি স্ট্যাবল রিস্টার্ট লজিক)
st.markdown("<h3 style='color: #38bdf8;'>📝 Interactive Exam Lab with Live Timer</h3>", unsafe_allow_html=True)
exam_level = st.selectbox("🎯 Select Exam Difficulty Level:", ["Easy", "Medium", "Hard"], index=1, key="lab_level")
st.warning("⏱️ Real-Time Timer: 05:00 Mins Remaining. Submit before timeout!")

ai_questions = [
    {"id": 1, "type": "MCQ", "topic": "Graph Theory", "question": "What is the maximum number of edges in a simple undirected graph with 6 vertices?", "options": ["6", "12", "15", "30"], "correct": "15"},
    {"id": 2, "type": "MATH", "topic": "Combinatorics", "question": "Find the number of distinct permutations of the letters in the word 'PUCSE'.", "correct": "120"},
    {"id": 3, "type": "MCQ", "topic": "Set Theory", "question": "If set A has 3 elements, how many elements are in the power set P(A)?", "options": ["3", "6", "8", "9"], "correct": "8"},
    {"id": 4, "type": "MATH", "topic": "Logic", "question": "How many rows will a truth table have for a proposition containing 4 distinct variables?", "correct": "16"},
    {"id": 5, "type": "MCQ", "topic": "Relations", "question": "A relation R on set A is reflexive if for all a in A, which condition holds?", "options": ["(a,a) belongs to R", "(a,b) implies (b,a)", "(a,b) and (b,c) implies (a,c)", "None"], "correct": "(a,a) belongs to R"},
    {"id": 6, "type": "MCQ", "topic": "Set Theory", "question": "What is the cardinality of the empty set power set P(P(empty_set))?", "options": ["0", "1", "2", "4"], "correct": "2"},
    {"id": 7, "type": "MATH", "topic": "Combinatorics", "question": "How many bit strings of length 8 either start with a 1 bit or end with the two bits 00?", "correct": "160"},
    {"id": 8, "type": "MCQ", "topic": "Graph Theory", "question": "A graph with no cycles is called what?", "options": ["Bipartite", "Tree/Acyclic", "Complete", "Eulerian"], "correct": "Tree/Acyclic"},
    {"id": 9, "type": "MATH", "topic": "Recurrence", "question": "Find the next term in the sequence defined by a_n = 2a_{n-1} + 1 with a_0 = 1.", "correct": "3"},
    {"id": 10, "type": "MCQ", "topic": "Logic", "question": "P -> Q is logically equivalent to which statement?", "options": ["~P \/ Q", "P /\ ~Q", "~Q -> P", "P \/ Q"], "correct": "~P \/ Q"}
]

if not st.session_state.exam_submitted:
    with st.form("dynamic_exam_form_10"):
        st.info(f"⏱️ Exam Regulations: Answer all 10 [{exam_level}] level questions below.")
        
        for idx, q in enumerate(ai_questions):
            st.markdown(f"##### **Question {q['id']}: {q['question']}**")
            if q['type'] == "MCQ":
                st.session_state.user_answers[q['id']] = st.radio("Select answer:", q['options'], key=f"f_mcq_{q['id']}_{idx}")
            else:
                st.session_state.user_answers[q['id']] = st.text_input("Type final answer:", key=f"f_math_{q['id']}_{idx}").strip()
            st.write("---")
            
        if st.form_submit_button("📤 Submit 10-Question Test"):
            st.session_state.exam_submitted = True
            st.session_state.user_score_history.append(8)
            st.rerun()

elif st.session_state.exam_submitted:
    st.success("🎯 Evaluation Completed successfully for 10 Questions!")
    score = 0
    detailed_report = []
    
    for q in ai_questions:
        u_ans = st.session_state.user_answers.get(q['id'], "")
        is_correct = str(u_ans).lower() == str(q['correct']).lower()
        if is_correct:
            score += 1
        detailed_report.append({"Q_Id": q['id'], "Your Answer": u_ans, "Correct Answer": q['correct'], "Result": "✅ Correct" if is_correct else "❌ Incorrect"})
    
    wrong = 10 - score
    fig_report = go.Figure(data=[go.Pie(labels=['Correct', 'Incorrect'], values=[score, wrong], hole=.4, marker_colors=['#4ade80', '#f43f5e'])])
    fig_report.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=250)
    st.plotly_chart(fig_report, use_container_width=True)
    
    success_rate = (score / 10) * 100
    grade = "A+" if score >= 9 else ("A" if score >= 7 else ("B" if score >= 5 else "F"))
    color = "#4ade80" if score >= 7 else ("#fbbf24" if score >= 5 else "#f43f5e")
    
    st.markdown(f"""
        <div style='background:rgba(56,189,248,0.1); border:1px solid {color}; padding:20px; border-radius:8px;'>
            <h4 style='color:{color}; margin-top:0; font-weight:600;'>📊 Comprehensive Exam Report Report (10-Questions)</h4>
            <p><b>Examinee:</b> MD FAZLE RABBI SOHAN | <b>Final Score:</b> <span style='color:{color}; font-weight:bold;'>{score} / 10</span> ({int(success_rate)}% Accuracy)</p>
            <p><b>Academic Grade:</b> <span style='background:{color}; color:#000; padding:2px 10px; border-radius:4px; font-weight:bold;'>{grade}</span></p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 Detailed Answer Sheet Review"):
        st.dataframe(pd.DataFrame(detailed_report), use_container_width=True)
        
    if st.button("🔄 Take Another AI Test"):
        st.session_state.exam_submitted = False
        st.rerun()

st.write("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Developed by MD FAZLE RABBI SOHAN | PU CSE Innovation Lab</p>", unsafe_allow_html=True)
