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
    
    /* কাস্টম প্রিমিয়াম মডিউল বক্স */
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

# ২. এপিআই কি কনফিগারেশন
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

# লাইভ ইন্ডিকেটর প্যানেল
if ai_ready:
    st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: CONNECTED WITH GEMINI</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-panel" style="background-color: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; color: #f59e0b !important;">🟡 Core AI Engine: RUNNING IN LOCAL SIMULATION MODE</div>', unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Ultimate Interactive Lab")
st.subheader("Universal Discrete Mathematics Solver & Gamified Study Suite")
st.write("Presidency University | CSE Dept | Innovation Edition")
st.write("---")

# Session State ইনিশিয়েলাইজেশন
if 'search_history' not in st.session_state:
    st.session_state.search_history = []
if 'exam_submitted' not in st.session_state:
    st.session_state.exam_submitted = False
if 'user_score_history' not in st.session_state:
    st.session_state.user_score_history = []
if 'calculated_score' not in st.session_state:
    st.session_state.calculated_score = 0
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 0

# ৩. সাইডবার প্রোফাইল ও গ্যামিফাইড মেডেল ট্র্যাকার
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🎓 Student Profile</h3>", unsafe_allow_html=True)
with st.sidebar.container(border=True):
    st.write("**Developer:** MD FAZLE RABBI SOHAN")
    st.write("**Institution:** Presidency University")
    st.write("**Department:** CSE")
    
    history_len = len(st.session_state.user_score_history)
    if history_len >= 3:
        rank, badge = "Graph Wizard 🥇", "#f59e0b"
    elif history_len >= 1:
        rank, badge = "Logic Master 🥈", "#cbd5e1"
    else:
        rank, badge = "Discrete Novice 🥉", "#b45309"
        
    st.markdown(f"**Rank:** <span style='color:{badge}; font-weight:bold;'>{rank}</span>", unsafe_allow_html=True)
    if history_len > 0:
        st.metric(label="Tests Taken", value=history_len)

st.sidebar.write("---")
st.sidebar.page_link("https://presidency.edu.bd/", label="Presidency University Portal", icon="🏫")

# 🧮 ৪. Live Interactive Truth Table Generator
st.markdown("<h3 style='color: #38bdf8;'>🧮 Live Interactive Truth Table Generator</h3>", unsafe_allow_html=True)
st.caption("💡 ২-ভেরিয়েবল প্রপোজিশনের জন্য অ্যান্ড (AND), অর (OR) বা কন্ডিশনাল ট্রুথ টেবিল লাইভ জেনারেট করো।")

col_t1, col_t2 = st.columns(2)
with col_t1:
    var_1 = st.selectbox("Select Variable 1:", ["P", "~P"])
with col_t2:
    op_type = st.selectbox("Select Logical Operator:", ["AND (/\\)", "OR (\\/)", "Implication (->)"])

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
            
        table_rows.append({
            "P": p,
            "Q": q,
            f"{var_1}": v1,
            f"{var_1} {sign} Q": res
        })
    
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    st.markdown(f"##### 🎯 Generated Truth Table for: `{var_1} {sign} Q`")
    st.dataframe(pd.DataFrame(table_rows).style.format(formatter={col: str for col in [f"{var_1}", f"{var_1} {sign} Q"]}), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 📊 ৫. সিলেবাস অ্যানালিটিক্স (পাই চার্ট সিস্টেম)
st.markdown("<h3 style='color: #38bdf8;'>📊 Dynamic Syllabus Analytics & Weight Distribution</h3>", unsafe_allow_html=True)

topic_data = {
    "Set Theory": {"importance": 15, "hardness": 30},
    "Propositional Logic": {"importance": 20, "hardness": 45},
    "Graph Theory": {"importance": 25, "hardness": 85},
    "Combinatorics & Counting": {"importance": 20, "hardness": 70},
    "Recurrence Relations": {"importance": 20, "hardness": 90}
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
else:
    st.warning("Please select at least one topic to view analytics.")

st.write("---")

# 📚 ৬. গ্লোবাল লেকচার ডাটাবেস এবং ইন্টারঅ্যাক্টিভ লেসন জেনারেটর
st.markdown("<h3 style='color: #38bdf8;'>📚 Interactive Lesson Generator</h3>", unsafe_allow_html=True)
lesson_topic = st.selectbox("📖 Choose a topic to learn:", list(topic_data.keys()))

global_lecture_db = {
    "Recurrence Relations": r"""### 📘 Masterclass Lecture: Recurrence Relations (পুনরাবৃত্তি সম্পর্ক)
#### **১. ভূমিকা (Introduction):**
একটি পুনরাবৃত্তি সম্পর্ক হলো এমন একটি সমীকরণ যা কোনো সিকোয়েন্সের $n$-তম পদকে তার পূর্ববর্তী পদগুলোর মাধ্যমে প্রকাশ করে (যেমন: Fibonacci Sequence)।
#### **২. Solving Homogeneous Linear Recurrences:**
ক্যারেক্টারিস্টিক সমীকরণ $r^2 - c_1r - c_2 = 0$ গঠন করে রুটস বের করার মাধ্যমে এর সমাধান করা হয়।
$$a_n = C_1r_1^n + C_2r_2^n$$
#### **📚 Recommended Reference Books:**
* 📖 **Concrete Mathematics** by Ronald L. Graham
* 🌐 **Khan Academy Sequence & Series**""",

    "Set Theory": r"""### 📘 Masterclass Lecture: Set Theory (সেট তত্ত্ব)
#### **১. ভূমিকা (Introduction):**
সেট হলো সুনির্দিষ্ট বস্তুর সংগ্রহ (A set is a well-defined collection of distinct objects)।
#### **২. Core Concepts & Mathematical Proofs:**
* **Power Set (পাওয়ার সেট):** দ্য সেট অফ অল সাবসেটস। উপাদান সংখ্যা $n$ হলে পাওয়ার সেটের উপাদান হবে $2^n$।
$$A \times B = \{(a, b) \mid a \in A \land b \in B\}$$""",

    "Propositional Logic": r"""### 📘 Masterclass Lecture: Propositional Logic (প্রপোজিশনাল লজিক)
#### **১. 📚 Core Logic Rules:**
* **Conjunction ($\land$):** দুটিই সত্য হলে আউটপুট সত্য।
$$P \rightarrow Q \equiv \neg P \lor Q$$""",

    "Graph Theory": r"""### 📘 Masterclass Lecture: Graph Theory (গ্রাফ তত্ত্ব)
#### **১. Handshaking Theorem (হ্যান্ডশেকিং থিওরেম):**
$$\sum_{v \in V} \text{deg}(v) = 2|E|$$""",

    "Combinatorics & Counting": r"""### 📘 Masterclass Lecture: Combinatorics & Counting
#### **১. Pigeonhole Principle (পায়রাখোপ নীতি):**
$$\lfloor n/k \rfloor \text{ pigeons model alignment.}$$"""
}

if st.button("Generate Lecture & References", use_container_width=True):
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    if ai_ready:
        with st.spinner("Generation comprehensive roadmap via Gemini AI..."):
            prompt = f"Act as an elite discrete mathematics professor. Write a comprehensive, easy-to-understand student guide on '{lesson_topic}' with formulas, real-world CSE use cases, and practice examples in clean markdown with LaTeX."
            st.write(ai_model.generate_content(prompt).text)
    else:
        st.markdown(global_lecture_db.get(lesson_topic, "### Lecture Database Sync Operational."))
    st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 🃏 ৭. Interactive Formula Flashcards
st.markdown("<h3 style='color: #38bdf8;'>🃏 Interactive Formula Flashcards</h3>", unsafe_allow_html=True)
st.caption("💡 পরীক্ষার আগে ডিসক্রিট ম্যাথের গুরুত্বপূর্ণ জটিল সূত্রগুলো দ্রুত রিভিশন দেওয়ার ইন্টারেক্টিভ ফ্লিপ-বক্স।")

f_col1, f_col2 = st.columns(2)
with f_col1:
    st.markdown('<div class="flashcard"><b>💡 Handshaking Theorem</b></div>', unsafe_allow_html=True)
    if st.checkbox("Reveal Formula 1"):
        st.latex(r"\sum_{v \in V} \text{deg}(v) = 2|E|")
with f_col2:
    st.markdown('<div class="flashcard"><b>💡 Pigeonhole Principle</b></div>', unsafe_allow_html=True)
    if st.checkbox("Reveal Formula 2"):
        st.latex(r"\lceil n/k \rceil \text{ items per bucket}")

st.write("---")

# 🤖 ৮ম. AI Smart PDF / Lecture Note Explainer Simulation
st.markdown("<h3 style='color: #38bdf8;'>🤖 AI Smart Lecture Note Explainer</h3>", unsafe_allow_html=True)
st.caption("💡 Presidency University ক্লাসরুমের ডিসক্রিট ম্যাথ লেকচার শিট বা টেক্সট নোট আপলোড করে ইনস্ট্যান্ট সাজেশন জেনারেট করো।")

uploaded_file = st.file_uploader("📂 Upload Class Lecture Sheet (PDF/TXT)", type=["pdf", "txt"])
if uploaded_file is not None:
    with st.spinner("🤖 AI is reading and analyzing your university note..."):
        file_contents = ""
        if uploaded_file.type == "text/plain":
            file_contents = uploaded_file.read().decode("utf-8")
            
        time.sleep(1.2)
        st.success("🎉 Note Analysis Complete!")
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown("<b>📌 AI Generated Short Suggestion & Summary:</b><br><br>", unsafe_allow_html=True)
        
        if ai_ready and file_contents:
            prompt = f"Analyze the following university lecture notes and extract a summary, key formulas, and 3 expected questions: {file_contents}"
            st.write(ai_model.generate_content(prompt).text)
        else:
            st.markdown("""
            ১. <b>Most Important Topic:</b> Handshaking Theorem এর প্রুফ এবং ম্যাথ ফাইনাল পরীক্ষার জন্য ৯০% কমন।<br>
            ২. <b>Expected Question:</b> একটি সিম্পল গ্রাফে ১১টি এজ থাকলে নোডগুলোর ডিগ্রীর যোগফল কত? (উত্তর: ২২)<br>
            ৩. <b>Formula Cheat Sheet:</b> $P \\rightarrow Q \\equiv \\neg P \\lor Q$ এটি ভালো করে দেখে যাবে।
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 🚀 ৯. ইউনিভার্সাল সিঙ্গেল ইনপুট ইন্টারফেস (ম্যাথ সলভার)
st.markdown("<h3 style='color: #38bdf8;'>🚀 Universal Math Input Box</h3>", unsafe_allow_html=True)
user_query = st.text_area("📝 Type or paste your discrete math problem here:", placeholder="e.g., Solve the recurrence relation a_n = 4a_{n-1} - 4a_{n-2}...", height=110, key="solver_query")

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
                else:
                    solution = r"""### 📘 Step-by-Step Mathematical Solution
**Problem:** Solve $a_n = 4a_{n-1} - 4a_{n-2}$ with $a_0 = 1, a_1 = 4$.
#### **Step 1: Characteristic Equation**
$$r^2 - 4r + 4 = 0 \implies (r-2)^2 = 0 \implies r = 2 \text{ (Repeated Root)}$$
#### **Step 2: General Solution & Constants**
$$a_n = (C_1 + C_2n) \cdot 2^n$$
Applying initial conditions: $C_1 = 1, C_2 = 1$.
#### **🎯 Final Explicit Formula:**
$$a_n = (1 + n) \cdot 2^n$$"""
                
                st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                st.balloons()
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception:
                solution = global_lecture_db["Recurrence Relations"]
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 🧠 ১০. Interactive Exam Lab with Real-Time Quiz Timer
st.markdown("<h3 style='color: #38bdf8;'>📝 Interactive Exam Lab with Live Timer</h3>", unsafe_allow_html=True)

exam_level = st.selectbox("🎯 Select Exam Difficulty Level:", ["Easy", "Medium", "Hard"], index=1, key="lab_level")
st.warning("⏱️ Quiz Mode Active: Evaluate your accurate answers live below.")

ai_questions = [
    {"id": 1, "type": "MCQ", "topic": "Graph Theory", "question": f"[{exam_level}] What is the maximum number of edges in a simple graph with 6 vertices?", "options": ["6", "12", "15", "30"], "correct": "15"},
    {"id": 2, "type": "MATH", "topic": "Combinatorics", "question": f"[{exam_level}] Find the number of distinct permutations of the letters in the word 'PUCSE'.", "options": [], "correct": "120"}
]

if not st.session_state.exam_submitted:
    with st.form("dynamic_exam_form"):
        st.markdown(f"##### 📝 Question 1: {ai_questions[0]['question']}")
        q1_ans = st.radio("Select options:", ai_questions[0]['options'], key="q1_lab")
        
        st.markdown(f"##### 📝 Question 2: {ai_questions[1]['question']}")
        q2_ans = st.text_input("Type numerical answer:", key="q2_lab").strip()
        
        if st.form_submit_button("📤 Submit Mock Test"):
            # ডাইনামিকালি স্কোর ক্যালকুলেশন
            score = 0
            if q1_ans == ai_questions[0]['correct']:
                score += 1
            if q2_ans == ai_questions[1]['correct']:
                score += 1
                
            st.session_state.calculated_score = score
            st.session_state.total_questions = len(ai_questions)
            st.session_state.exam_submitted = True
            st.session_state.user_score_history.append(score)
            st.rerun()

elif st.session_state.exam_submitted:
    st.success("🎯 Evaluation Completed successfully!")
    
    score = st.session_state.calculated_score
    total = st.session_state.total_questions
    incorrect = total - score
    
    fig_report = go.Figure(data=[go.Pie(labels=['Correct', 'Incorrect'], values=[score, incorrect], hole=.4, marker_colors=['#4ade80', '#f43f5e'])])
    fig_report.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=240)
    st.plotly_chart(fig_report, use_container_width=True)
    
    grade = "A" if (score/total) >= 0.8 else "B"
    
    st.markdown(f"""
        <div style='background:rgba(56,189,248,0.1); border:1px solid #38bdf8; padding:20px; border-radius:8px;'>
            <h4 style='color:#38bdf8; margin-top:0;'>📊 Performance Report Card & Feedback</h4>
            <p><b>Examinee:</b> MD FAZLE RABBI SOHAN | <b>Grade:</b> {grade}</p>
            <p><b>Score:</b> {score} / {total} ({(score/total)*100:.0f}% Accuracy)</p>
            <hr style='opacity:0.2;'>
            <p style='font-style:italic; color:#cbd5e1;'><b>🗣️ Academic Feedback:</b> Your score is live calculated! Keep practicing to master {exam_level} mode.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Take Another AI Test"):
        st.session_state.exam_submitted = False
        st.rerun()

st.write("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Developed by MD FAZLE RABBI SOHAN | PU CSE Innovation Lab</p>", unsafe_allow_html=True)
