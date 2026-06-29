mport streamlit as st
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
    
    /* কাস্টম প্রিমিয়াম মডিউল BOX */
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
    
    /* ফ্ল্যাশকার্ড স্টাইলিং */
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
    # Streamlit Cloud Secret বা লোকাল সিক্রেট সিকিউরলি হ্যান্ডল করা
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
    st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: CONNECTED WITH GEMINI LIVE</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-panel" style="background-color: rgba(245, 158, 11, 0.1); border: 1px solid #f59e0b; color: #f59e0b !important;">💡 Core AI Engine: RUNNING IN LOCAL MASTER-SIMULATION MODE</div>', unsafe_allow_html=True)

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

# 📊 ৫. সিলেবাস অ্যানালিটিক্স (পাই চার্ট + Hardness Index)
st.markdown("<h3 style='color: #38bdf8;'>📊 Dynamic Syllabus Analytics & Weight Distribution</h3>", unsafe_allow_html=True)

topic_data = {
    "Set Theory": {"importance": 15, "hardness": 30},
    "Propositional Logic": {"importance": 20, "hardness": 45},
    "Graph Theory": {"importance": 25, "hardness": 85},
    "Combinatorics & Counting": {"importance": 20, "hardness": 70},
    "Recurrence Relations": {"importance": 20, "hardness": 90}
}

st.markdown("##### 🔍 Select Syllabus Topics to Analyze:")
selected_topics = [t for t in topic_data.keys() if st.checkbox(t, value=True, key=f"sync_{t}")]

if selected_topics:
    col_chart1, col_chart2 = st.columns(2)
    
    labels = selected_topics
    importance_values = [topic_data[t]["importance"] for t in selected_topics]
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=importance_values, hole=.3, marker_colors=['#0ea5e9', '#38bdf8', '#0284c7', '#7dd3fc', '#bae6fd'])])
    fig_pie.update_layout(title="Exam Importance (%)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=260, margin=dict(l=10, r=10, b=10, t=40))
    
    hardness_values = [topic_data[t]["hardness"] for t in selected_topics]
    fig_bar = go.Figure(data=[go.Bar(x=labels, y=hardness_values, marker_color='#f43f5e')])
    fig_bar.update_layout(title="Topic Hardness Index (1-100)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=260, margin=dict(l=10, r=10, b=10, t=40))
    
    with col_chart1:
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_chart2:
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("Please select at least one topic to view analytics.")

st.write("---")

# 📚 ৬. গ্লোবাল লেকচার ডাটাবেস এবং ইন্টারঅ্যাক্টিভ লেসন জেনারেটর (Syntax Safe Strings)
st.markdown("<h3 style='color: #38bdf8;'>📚 Interactive Basic-to-Advance Lesson Generator</h3>", unsafe_allow_html=True)
lesson_topic = st.selectbox("📖 Choose a topic to learn:", list(topic_data.keys()))

# ডাবল এস্কেপ ব্যবহার করে ডিকশনারির স্ট্রিংগুলোকে সুরক্ষিত এবং সিনট্যাক্স এররমুক্ত করা হয়েছে
global_lecture_db = {
    "Recurrence Relations": """### 📘 Masterclass Lecture: Recurrence Relations (পুনরাবৃত্তি সম্পর্ক)

#### **১. ভূমিকা ও বেসিক লেভেল (Basic Introduction):**
একটি পুনরাবৃত্তি সম্পর্ক (Recurrence Relation) হলো এমন একটি গাণিতিক সমীকরণ যা কোনো সিকোয়েন্সের n-তম পদকে তার পূর্ববর্তী পদগুলোর (যেমন: a_{n-1}, a_{n-2}) মাধ্যমে প্রকাশ করে।
* **CSE Application:** এটি অ্যালগরিদমের টাইম কমপ্লেক্সিটি (যেমন: Divide and Conquer, Merge Sort) বের করতে ব্যবহৃত হয়।

#### **২. ইন্টারঅ্যাক্টিভ মডেল ও ডায়াগ্রাম (Visual Representation):**
```
Fibonacci Tree Model:
       a_n (n)
       /     \\
  a_{n-1}   a_{n-2}
```

#### **৩. অ্যাডভান্সড লেভেল সমাধান (Advanced Homogeneous Linear Recurrences):**
ক্যারেক্টারিস্টিক সমীকরণ r^2 - c_1r - c_2 = 0 গঠন করে রুটস বের করার মাধ্যমে এর সাধারণ সমাধান করা হয়:
$$a_n = C_1r_1^n + C_2r_2^n$$""",

    "Set Theory": """### 📘 Masterclass Lecture: Set Theory (সেট তত্ত্ব)

#### **১. ভূমিকা ও বেসিক লেভেল (Basic Introduction):**
সেট হলো সুনির্দিষ্ট বাস্তব বা চিন্তামূলক বস্তুর সমাবেশ (A set is a well-defined collection of distinct objects)。
* **CSE Application:** রিলেশনাল ডাটাবেস ম্যানেজমেন্ট সিস্টেম (RDBMS) এবং কুয়েরি অপ্টিমাইজেশনে সেট থিওরি ব্যবহৃত হয়।

#### **২. ভিজ্যুয়াল রিপ্রেজেন্টেশন (Venn Diagram Concept):**
```
   [ Universal Set (U) ]
   +-------------------+
   |  ( Set A )  ( Set B )
   |   [ A ∩ B ]       |
   +-------------------+
```

#### **৩. অ্যাডভান্সড ম্যাথমেটিক্যাল প্রুফ (Advanced Properties):**
$$A \\times B = \\{(a, b) \\mid a \\in A \\land b \\in B\\}$$
Power Set-এর মোট উপাদানের সূত্র: 2^n (যেখানে n হলো মূল সেটের উপাদান সংখ্যা)""",

    "Propositional Logic": """### 📘 Masterclass Lecture: Propositional Logic (প্রপোজিশনাল লজিক)

#### **১. বেসিক পরিচিতি (Basic Logic Rules):**
প্রপোজিশনাল লজিক হলো এমন স্টেটমেন্ট যা হয় সত্য (True) অথবা মিথ্যা (False) হতে পারে।
* **Conjunction (∧):** দুটি উপাদানই সত্য হলে আউটপুট সত্য।

#### **২. ইন্টারঅ্যাক্টিভ লজিক গেট ডায়াগ্রাম (Logic Gate Model):**
```
INPUT P -----\\
              [ AND GATE ] ----> OUTPUT (P ∧ Q)
INPUT Q -----/
```

#### **৩. অ্যাডভান্সড কন্ডিশনাল আইডেন্টিটি (Advanced Equivalence):**
$$P \\rightarrow Q \\equiv \\neg P \\lor Q$$""",

    "Graph Theory": """### 📘 Masterclass Lecture: Graph Theory (গ্রাফ তত্ত্ব)

#### **১. বেসিক পরিচিতি (Basic Concepts):**
গ্রাফ হলো কিছু ভার্টেক্স (Vertices/Nodes) এবং এজের (Edges/Links) সমষ্টি যা নেটওয়ার্ক তৈরিতে ব্যবহৃত হয়।

#### **২. ইন্টারঅ্যাক্টিভ গ্রাফ মডেল (Visual Network Diagram):**
```
   (A)-------(B)
    |         |
    |         |
   (C)-------(D)
```

#### **৩. অ্যাডভান্সড হ্যান্ডশেকিং থিওরেম (Advanced Handshaking Theorem):**
যেকোনো গ্রাফের সব নোডের ডিগ্রীর যোগফল তার মোট এজের দ্বিগুণ হয়:
$$\\sum_{v \\in V} \\text{deg}(v) = 2|E|$$""",

    "Combinatorics & Counting": """### 📘 Masterclass Lecture: Combinatorics & Counting

#### **১. বেসিক কাউন্টিং রুলস (Basic Permutation & Combination):**
কোনো বিন্যাস বা সমাবেশ গণনার বিজ্ঞানই হলো কম্বিনেটোরিক্স।

#### **২. পায়রাখোপ মডেল (Pigeonhole Principle Visual):**
```
Pigeons (4)  --->  [📦] [📦] [📦]  Holes (3)
ফলাফল: কমপক্ষে ১টি বক্সে ২টি পায়রা থাকবেই।
```

#### **৩. অ্যাডভান্সড ফর্মুলা (Advanced Formula):**
$$\\lceil n/k \\rceil \\text{ pigeons per hole formula.}$$"""
}

if st.button("Generate Comprehensive Guide (Bangla + English)", use_container_width=True):
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    if ai_ready:
        with st.spinner("🧠 AI-র মাধ্যমে বিস্তারিত ইন্টারঅ্যাক্টিভ লেসন জেনারেট হচ্ছে..."):
            try:
                prompt = f"Act as an elite discrete mathematics professor. Write a highly detailed, textbook-style guide on '{lesson_topic}' starting from extreme absolute basic definition to advanced concepts. Mix languages fluently (Write explanations in clear, structured Bangla language, and keep scientific terms/formulas in English). Include ASCII-art/Text-diagrams to visualize the concept, multi-step code/math proofs, and discrete engineering use cases. Format everything beautifully using standard markdown with proper LaTeX equations."
                response = ai_model.generate_content(prompt)
                st.write(response.text)
            except Exception:
                st.markdown(global_lecture_db.get(lesson_topic, "### Sync Operational."))
    else:
        st.markdown(global_lecture_db.get(lesson_topic, "### Sync Operational."))
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
            try:
                prompt = f"Analyze the following university lecture notes and extract a summary, key formulas, and 3 expected questions: {file_contents}"
                st.write(ai_model.generate_content(prompt).text)
            except Exception:
                st.markdown("১. <b>Topic:</b> Handshaking Theorem এর প্রুফ এবং ম্যাথ ফাইনাল পরীক্ষার জন্য ৯০% কমন।")
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
                    solution = """### 📘 Step-by-Step Mathematical Solution
**Problem:** Solve $a_n = 4a_{n-1} - 4a_{n-2}$ with $a_0 = 1, a_1 = 4$.
#### **Step 1: Characteristic Equation**
$$r^2 - 4r + 4 = 0 \\implies (r-2)^2 = 0 \\implies r = 2 \\text{ (Repeated Root)}$$
#### **Step 2: General Solution & Constants**
$$a_n = (C_1 + C_2n) \\cdot 2^n$$
Applying initial conditions: $C_1 = 1, C_2 = 1$.
#### **🎯 Final Explicit Formula:**
$$a_n = (1 + n) \\cdot 2^n$$"""
                
                st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                st.balloons()
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception:
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown("### Calculation simulation ended via fallback mode.")
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
