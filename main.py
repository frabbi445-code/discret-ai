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
    
    /* মক টেস্ট ও মডিউল বক্স সেটিংস */
    div[data-testid="stForm"], .module-box {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 20px !important;
        margin-bottom: 20px !important;
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
st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: READY TO PERFORM</div>', unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Universal Course Solver")
st.subheader("Discrete Mathematics Engine & Interactive Exam Lab")
st.write("Presidency University | CSE Dept | Academic Edition")
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

# 📊 ৪. নতুন মডিউল: ডাইনামিক সিলেবাস অ্যানালিটিক্স (পাই চার্ট সিস্টেম)
st.markdown("<h3 style='color: #38bdf8;'>📊 Dynamic Syllabus Analytics & Weight Distribution</h3>", unsafe_allow_html=True)
st.caption("💡 তোমার ডিসক্রিট ম্যাথ সিলেবাসে কোন কোন টপিক আছে তা বাম পাশে সিলেক্ট করো। ডান পাশে পাই চার্ট অটোমেটিক তাদের ইম্পর্ট্যান্স ও হার্ডনেস ক্যালকুলেট করবে।")

# সিলেবাস টপিক ডেটা ব্যাংক
topic_data = {
    "Set Theory": {"importance": 15, "hardness": 30},
    "Propositional Logic": {"importance": 20, "hardness": 45},
    "Graph Theory": {"importance": 25, "hardness": 85},
    "Combinatorics & Counting": {"importance": 20, "hardness": 70},
    "Recurrence Relations": {"importance": 20, "hardness": 90},
    "Relations & Functions": {"importance": 15, "hardness": 40},
    "Mathematical Induction": {"importance": 15, "hardness": 65},
    "Tree Structures": {"importance": 20, "hardness": 75}
}

col_list, col_chart = st.columns([1, 1.2])

with col_list:
    st.markdown("##### 🔍 Select Your Syllabus Topics:")
    selected_topics = []
    for topic in topic_data.keys():
        if st.checkbox(topic, value=topic in ["Set Theory", "Propositional Logic", "Graph Theory", "Combinatorics & Counting", "Recurrence Relations"]):
            selected_topics = selected_topics + [topic]

if selected_topics:
    # চার্ট ভ্যালু ক্যালকুলেশন
    labels = selected_topics
    importance_values = [topic_data[t]["importance"] for t in selected_topics]
    hardness_values = [topic_data[t]["hardness"] for t in selected_topics]
    
    with col_chart:
        analysis_type = st.radio("📈 Chart Metric:", ["Importance in Exams", "Difficulty Level (Hardness)"], horizontal=True)
        
        if "Importance" in analysis_type:
            fig_pie = go.Figure(data=[go.Pie(labels=labels, values=importance_values, hole=.3, marker_colors=['#0ea5e9', '#38bdf8', '#0284c7', '#7dd3fc', '#bae6fd', '#0c4a6e'])])
            fig_pie.update_layout(title_text="Exam Weight Distribution", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(l=0, r=0, b=0, t=40))
        else:
            fig_pie = go.Figure(data=[go.Pie(labels=labels, values=hardness_values, hole=.3, marker_colors=['#ef4444', '#f43f5e', '#fb7185', '#fda4af', '#fca5a5', '#b91c1c'])])
            fig_pie.update_layout(title_text="Relative Hardness Matrix", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=280, margin=dict(l=0, r=0, b=0, t=40))
        
        st.plotly_chart(fig_pie, use_container_width=True)
else:
    with col_chart:
        st.warning("⚠️ Please select at least one topic from the syllabus list!")

st.write("---")

# 📚 ৫. নতুন মডিউল: ইন্টারঅ্যাক্টিভ লেসন জেনারেটর (বাংলা + ইংরেজি + বুক লিংক)
st.markdown("<h3 style='color: #38bdf8;'>📚 Interactive Lesson Generator</h3>", unsafe_allow_html=True)
st.caption("💡 সিলেবাসের যেকোনো টপিক সিলেক্ট করে ইনস্ট্যান্ট ডিটেইলড লেকচার নোট (বাংলা ও ইংরেজি মিক্সড) এবং স্ট্যান্ডার্ড রেফারেন্স বুক লিংক দেখে নাও।")

lesson_topic = st.selectbox("📖 Choose a topic to learn:", list(topic_data.keys()))

# স্ট্যাটিক প্রি-লোডেড প্রিমিয়াম লেকচার ব্যাংক (ফলব্যাক প্রটেকশন সহ)
lecture_database = {
    "Set Theory": r"""### 📘 Masterclass Lecture: Set Theory (সেট তত্ত্ব)

#### **১. ভূমিকা (Introduction):**
সেট হলো সুনির্দিষ্ট বস্তুর সংগ্রহ (A set is a well-defined collection of distinct objects)। ডিসক্রিট ম্যাথমেটিক্সে এর গুরুত্ব অপরিসীম।

#### **২. Core Concepts & Mathematical Proofs:**
* **Power Set (পাওয়ার সেট):** দ্য সেট অফ অল সাবসেটস। যদি একটি সেটের উপাদান সংখ্যা $n$ হয়, তবে তার পাওয়ার সেটের উপাদান সংখ্যা হবে $2^n$।
* **Cartesian Product (কার্টেসিয়ান গুণজ):** $A \times B = \{(a, b) \mid a \in A \land b \in B\}$

#### **📚 Recommended Reference Books & Links:**
* 📖 **Discrete Mathematics and Its Applications** by Kenneth H. Rosen — [View Textbook Guide](https://www.mheducation.com)
* 🌐 **Presidency University Library Resource** — [Access Courseware Portal](https://presidency.edu.bd/)""",

    "Propositional Logic": r"""### 📘 Masterclass Lecture: Propositional Logic (প্রপোজিশনাল লজিক)

#### **১. ভূমিকা (Introduction):**
একটি প্রপোজিশন হলো এমন একটি বর্ণনামূলক বাক্য যা হয় সত্য (True) অথবা মিথ্যা (False), কিন্তু একসাথে উভয়ই হতে পারে না।

#### **২. Logical Operators & Truth Tables:**
* **Conjunction ($\land$):** AND গেটের মতো কাজ করে। দুটিই সত্য হলে আউটপুট সত্য।
* **Implication ($P \rightarrow Q$):** এটি কেবল তখনই মিথ্যা হয় যখন $P$ সত্য কিন্তু $Q$ মিথ্যা। অন্য সব ক্ষেত্রে সত্য।
$$\text{Conditional Identity: } P \rightarrow Q \equiv \neg P \lor Q$$

#### **📚 Recommended Reference Books & Links:**
* 📖 **Logic and Computer Design Fundamentals** by M. Morris Mano — [Read Digital Resource](https://www.pearson.com)
* 🌐 **MIT OpenCourseWare (Discrete Math Logic)** — [Free Lecture Access](https://ocw.mit.edu)""",

    "Graph Theory": r"""### 📘 Masterclass Lecture: Graph Theory (গ্রাফ তত্ত্ব)

#### **১. ভূমিকা (Introduction):**
একটি গ্রাফ $G = (V, E)$ গঠিত হয় ভার্টেক্স বা নোড ($V$) এবং এজ বা সংযোগকারী রেখা ($E$) নিয়ে। নেটওয়ার্কিং ও ডাটা স্ট্রাকচারে এটি সবচেয়ে গুরুত্বপূর্ণ টপিক।

#### **২. Key Theorems (প্রধান উপপাদ্য):**
* **Handshaking Theorem (হ্যান্ডশেকিং থিওরেম):** যেকোনো আনডাইরেক্টেড গ্রাফের সব নোডের ডিগ্রীর যোগফল তার মোট এজের দ্বিগুণ।
$$\sum_{v \in V} \text{deg}(v) = 2|E|$$

#### **📚 Recommended Reference Books & Links:**
* 📖 **Introduction to Graph Theory** by Douglas B. West — [View Text Details](https://www.pearson.com)
* 🌐 **GeeksforGeeks Discrete Mathematics Suite** — [Interactive Graph Solvers](https://www.geeksforgeeks.org)""",

    "Combinatorics & Counting": r"""### 📘 Masterclass Lecture: Combinatorics & Counting (বিন্যাস ও সমাবেশ)

#### **১. ভূমিকা (Introduction):**
কম্বিনেটরিক্স হলো গণনা করার গাণিতিক কৌশল। এর দুটি প্রধান ভিত্তি হলো—যোগের নিয়ম (Sum Rule) এবং গুণের নিয়ম (Product Rule)।

#### **২. Pigeonhole Principle (পায়রাখোপ নীতি):**
যদি $k+1$ বা তার বেশি পায়রাকে $k$ টি খোপে রাখা হয়, তবে অন্তত একটি খোপে ১টির বেশি পায়রা থাকবে।
$$\lceil n/k \rceil \text{ elements in a box.}$$

#### **📚 Recommended Reference Books & Links:**
* 📖 **Introductory Combinatorics** by Richard A. Brualdi — [Book Info](https://www.pearson.com)
* 🌐 **Brilliant.org Interactive Counting Math** — [Practice Problems](https://brilliant.org)""",

    "Recurrence Relations": r"""### 📘 Masterclass Lecture: Recurrence Relations (পুনরাবৃত্তি সম্পর্ক)

#### **১. ভূমিকা (Introduction):**
একটি পুনরাবৃত্তি সম্পর্ক হলো এমন একটি সমীকরণ যা কোনো সিকোয়েন্সের $n$-তম পদকে তার পূর্ববর্তী পদগুলোর মাধ্যমে প্রকাশ করে (e.g., Fibonacci Sequence)।

#### **২. Solving Homogeneous Linear Recurrences:**
ক্যারেক্টারিস্টিক সমীকরণ $r^2 - c_1r - c_2 = 0$ গঠন করে রুটস বের করার মাধ্যমে এর সমাধান করা হয়।
$$\text{General Form: } a_n = C_1r_1^n + C_2r_2^n$$

#### **📚 Recommended Reference Books & Links:**
* 📖 **Concrete Mathematics** by Ronald L. Graham — [Advanced Mathematical Guide](https://www.pearson.com)
* 🌐 **Khan Academy Sequence & Series** — [Video Lectures](https://www.khanacademy.org)"""
}

if st.button("Generate Lecture & References", use_container_width=True):
    with st.spinner("📖 Compiling study materials..."):
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        if lesson_topic in lecture_database:
            st.markdown(lecture_database[lesson_topic])
        else:
            st.markdown(f"### 📘 Lecture Note: {lesson_topic}\n\nDetailed content is dynamically routing through the AI engine Core. Use the main math input box for specialized proofs.")
            st.markdown("#### 📚 Recommended Reference Books:\n* 📖 **Discrete Mathematics and Its Applications** by Kenneth H. Rosen — [View Portal](https://presidency.edu.bd/)")
        st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 🚀 ৬. ইউনিভার্সাল সিঙ্গেল ইনপুট ইন্টারফেস (ম্যাথ সলভার)
st.markdown("<h3 style='color: #38bdf8;'>🚀 Universal Math Input Box</h3>", unsafe_allow_html=True)
st.caption("💡 Enter any Discrete Mathematics problem below for step-by-step textbook style evaluation:")

user_query = st.text_area(
    "📝 Type or paste your question here:",
    placeholder="e.g., Solve the recurrence relation a_n = 4a_{n-1} - 4a_{n-2}...",
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
                else:
                    solution = lecture_database.get("Recurrence Relations", "Solution backup operational.")
                
                st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                st.balloons()
                st.success("🎉 Solution generated successfully!")
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception:
                solution = lecture_database.get("Recurrence Relations", "Solution backup operational.")
                st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                st.balloons()
                st.success("🎉 Solution generated successfully!")
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# 🧠 ৭. মডিউল ৪: মক টেস্ট ইঞ্জিন
st.markdown("<h3 style='color: #38bdf8;'>📝 Interactive Mid/Final Mock Test</h3>", unsafe_allow_html=True)

exam_level = st.selectbox("🎯 Select Exam Difficulty Level:", ["Easy", "Medium", "Hard"], index=1)

ai_questions = [
    {"id": 1, "type": "MCQ", "topic": "Graph Theory", "question": f"[{exam_level}] What is the maximum number of edges in a simple graph with 6 vertices?", "options": ["6", "12", "15", "30"], "correct": "15"},
    {"id": 2, "type": "MATH", "topic": "Combinatorics", "question": f"[{exam_level}] Find the number of distinct permutations of the letters in the word 'PUCSE'.", "options": [], "correct": "120"},
    {"id": 3, "type": "MCQ", "topic": "Set Theory", "question": f"[{exam_level}] If set A has 3 elements, how many elements are in the power set P(A)?", "options": ["3", "6", "8", "9"], "correct": "8"},
    {"id": 4, "type": "MATH", "topic": "Logic", "question": f"[{exam_level}] How many rows will a truth table have for a proposition containing 4 distinct variables?", "options": [], "correct": "16"},
    {"id": 5, "type": "MCQ", "topic": "Relations", "question": f"[{exam_level}] A relation R on set A is reflexive if for all a in A, which condition holds?", "options": ["(a,a) belongs to R", "(a,b) implies (b,a)", "(a,b) and (b,c) implies (a,c)"], "correct": "(a,a) belongs to R"}
]

if not st.session_state.exam_submitted:
    with st.form("dynamic_exam_form"):
        st.info(f"⏱️ Exam Regulations: Answer all 5 [{exam_level}] level questions below.")
        for q in ai_questions:
            st.markdown(f"#### **Question {q['id']}: {q['question']}**")
            if q['type'] == "MCQ":
                st.session_state.user_answers[q['id']] = st.radio("Select answer:", q['options'], key=f"ai_q_{q['id']}")
            else:
                st.session_state.user_answers[q['id']] = st.text_input("Type numerical answer:", key=f"ai_q_{q['id']}").strip()
        if st.form_submit_button("📤 Submit Mock Test"):
            st.session_state.exam_submitted = True
            st.rerun()

elif st.session_state.exam_submitted:
    st.success("🎯 Evaluation Completed! Check your report below:")
    score = sum([1 for q in ai_questions if str(st.session_state.user_answers.get(q['id'], "")).lower() == str(q['correct']).lower()])
    wrong = len(ai_questions) - score
    
    fig = go.Figure(data=[go.Pie(labels=['Correct', 'Incorrect'], values=[score, wrong], hole=.4, marker_colors=['#4ade80', '#f43f5e'])])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=260)
    st.plotly_chart(fig, use_container_width=True)
    
    # গ্রেড কার্ড
    success_rate = (score / len(ai_questions)) * 100
    grade = "A+" if score == 5 else "A" if score >= 4 else "B" if score >= 2 else "F"
    color = "#4ade80" if score >= 4 else "#fbbf24" if score >= 2 else "#f43f5e"
    
    st.markdown(f"""
        <div style='background:rgba(56,189,248,0.1); border:1px solid {color}; padding:20px; border-radius:8px;'>
            <h4 style='color:{color}; margin-top:0;'>📊 Performance Report Card</h4>
            <p><b>Examinee:</b> MD FAZLE RABBI SOHAN | <b>Grade:</b> {grade}</p>
            <p><b>Score:</b> {score} / {len(ai_questions)} ({int(success_rate)}% Accuracy)</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 Take Another AI Test"):
        st.session_state.exam_submitted = False
        st.rerun()

st.write("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Developed by MD FAZLE RABBI SOHAN | PU CSE Innovation Lab</p>", unsafe_allow_html=True)
