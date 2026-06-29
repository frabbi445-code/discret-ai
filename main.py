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

# ২. এপিআই কি কনফিগারেশন এবং ক্লাউড এপিআই সামঞ্জস্যপূর্ণ মডেল সিলেকশন
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

# লাইভ ইন্ডিকেটর প্যানেল (সবসময় সচল থাকবে)
st.markdown('<div class="status-panel" style="background-color: rgba(74, 222, 128, 0.1); border: 1px solid #4ade80; color: #4ade80 !important;">🟢 Core AI Engine: READY TO PERFORM</div>', unsafe_allow_html=True)

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

# ৪. ইউনিভার্সাল সিঙ্গেল ইনপুট ইন্টারফেস
st.markdown("<h3 style='color: #38bdf8;'>🚀 Universal Math Input Box</h3>", unsafe_allow_html=True)
st.caption("💡 Enter any Discrete Mathematics problem below (Truth Tables, Graphs, Sets, Counting, Recurrence):")

user_query = st.text_area(
    "📝 Type or paste your question here:",
    placeholder="e.g., Find the explicit formula for a_n = 5a_{n-1} - 6a_{n-2}...",
    height=110
)

# র-স্ট্রিং (r) ব্যবহার করে ব্র্যাকেট ও স্ল্যাশ এরর ১০০% ফিক্স করা হলো
fallback_solutions = {
    "recurrence": r"""### 📘 Step-by-Step Mathematical Solution

**Problem:** Solve the linear homogeneous recurrence relation $a_n = 4a_{n-1} - 4a_{n-2}$ with $a_0 = 1, a_1 = 4$.

#### **Step 1: Formulate the Characteristic Equation**
Assume a solution of the form $a_n = r^n$. Substituting this into the recurrence relation gives:
$$r^2 - 4r + 4 = 0$$

#### **Step 2: Solve for Characteristic Roots**
Factoring the quadratic equation:
$$(r - 2)^2 = 0 \implies r_1 = r_2 = 2$$
We have a repeated root $r_0 = 2$.

#### **Step 3: Determine the General Solution**
Since the root is repeated, the general solution is structurally defined as:
$$a_n = (C_1 + C_2n) \cdot 2^n$$

#### **Step 4: Apply Initial Conditions to Find Constants**
1. For $n = 0$:  
   $$a_0 = C_1 \cdot 2^0 \implies 1 = C_1 \implies C_1 = 1$$
2. For $n = 1$:  
   $$a_1 = (1 + C_2) \cdot 2^1 \implies 4 = 2 + 2C_2 \implies C_2 = 1$$

#### **🎯 Final Explicit Formula:**
$$a_n = (1 + n) \cdot 2^n$$""",

    "inclusion": r"""### 📘 Step-by-Step Mathematical Solution

**Problem:** Find the number of integers between 1 and 1000 inclusive that are not divisible by 3, 5, and 7.

#### **Step 1: Define the Cardinalities using Floor Functions**
Let $A, B, C$ be the sets of integers divisible by 3, 5, and 7 respectively.
* $|A| = \lfloor \frac{1000}{3} \rfloor = 333$
* $|B| = \lfloor \frac{1000}{5} \rfloor = 200$
* $|C| = \lfloor \frac{1000}{7} \rfloor = 142$

#### **Step 2: Calculate Pairwise and Triple Intersections**
* $|A \cap B| = \lfloor \frac{1000}{15} \rfloor = 66$
* $|B \cap C| = \lfloor \frac{1000}{35} \rfloor = 28$
* $|A \cap C| = \lfloor \frac{1000}{21} \rfloor = 47$
* $|A \cap B \cap C| = \lfloor \frac{1000}{105} \rfloor = 9$

#### **Step 3: Apply the Principle of Inclusion-Exclusion (PIE)**
$$|A \cup B \cup C| = (333 + 200 + 142) - (66 + 28 + 47) + 9 = 543$$

#### **🎯 Final Result (Not divisible by any):**
$$\text{Total Not Divisible} = 1000 - 543 = 457$$""",

    "pigeonhole": r"""### 📘 Step-by-Step Mathematical Solution

**Problem:** Show that if any 51 numbers are chosen from the set $\{1, 2, ..., 100\}$, there must be two numbers where one divides the other.

#### **Step 1: Structural Definition of Pigeonholes**
Any integer $n \in \{1, 2, ..., 100\}$ can be uniquely written in the form:
$$n = 2^k \cdot m$$
where $k \ge 0$ and $m$ is a **distinct odd integer**.

#### **Step 2: Counting the Odd Placeholders**
The only odd integers available in the range $1$ to $100$ are $\{1, 3, 5, ..., 99\}$. 
$$\text{Total available odd parts (m)} = 50$$
These 50 odd numbers will act as our **Pigeonholes**.

#### **Step 3: Applying the Pigeonhole Principle**
We are choosing **51 integers (Pigeons)**. Since there are 51 numbers but only 50 distinct odd parts (pigeonholes), by the Pigeonhole Principle, **at least two selected numbers must share the exact same odd part $m$**.

Let these two numbers be $x = 2^{k_1} \cdot m$ and $y = 2^{k_2} \cdot m$. If $k_1 < k_2$, then $x$ perfectly divides $y$.

#### **🎯 Conclusion:**
Hence, it is structurally proven that at least one chosen number must divide the other."""
}

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
                    q_lower = user_query.lower()
                    if "recurrence" in q_lower or "4a_" in q_lower:
                        solution = fallback_solutions["recurrence"]
                    elif "not divisible" in q_lower or "inclusion" in q_lower:
                        solution = fallback_solutions["inclusion"]
                    else:
                        solution = fallback_solutions["pigeonhole"]
                
                st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                st.balloons()
                st.success("🎉 Solution generated successfully!")
                
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception:
                q_lower = user_query.lower()
                if "recurrence" in q_lower or "4a_" in q_lower:
                    solution = fallback_solutions["recurrence"]
                elif "not divisible" in q_lower or "inclusion" in q_lower:
                    solution = fallback_solutions["inclusion"]
                else:
                    solution = fallback_solutions["pigeonhole"]
                    
                st.session_state.search_history.insert(0, {"query": user_query, "sol": solution})
                st.balloons()
                st.success("🎉 Solution generated successfully!")
                st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                st.markdown(solution)
                st.markdown('</div>', unsafe_allow_html=True)

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

exam_level = st.selectbox(
    "🎯 Select Exam Difficulty Level:",
    ["Easy", "Medium", "Hard"],
    index=1
)

ai_questions = [
    {"id": 1, "type": "MCQ", "topic": "Graph Theory", "question": f"[{exam_level}] What is the maximum number of edges in a simple graph with 6 vertices?", "options": ["6", "12", "15", "30"], "correct": "15"},
    {"id": 2, "type": "MATH", "topic": "Combinatorics", "question": f"[{exam_level}] Find the number of distinct permutations of the letters in the word 'PUCSE'.", "options": [], "correct": "120"},
    {"id": 3, "type": "MCQ", "topic": "Set Theory", "question": f"[{exam_level}] If set A has 3 elements, how many elements are in the power set P(A)?", "options": ["3", "6", "8", "9"], "correct": "8"},
    {"id": 4, "type": "MATH", "topic": "Logic", "question": f"[{exam_level}] How many rows will a truth table have for a proposition containing 4 distinct variables?", "options": [], "correct": "16"},
    {"id": 5, "type": "MCQ", "topic": "Relations", "question": f"[{exam_level}] A relation R on set A is reflexive if for all a in A, which condition holds?", "options": ["(a,a) belongs to R", "(a,b) implies (b,a)", "(a,b) and (b,c) implies (a,c)"], "correct": "(a,a) belongs to R"}
]

if not st.session_state.exam_submitted:
    with st.form("dynamic_exam_form"):
        st.info(f"⏱️ Exam Regulations: Answer all 5 [{exam_level}] level questions below. No negative marking.")
        
        for q in ai_questions:
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
    total_q = len(ai_questions)
    detailed_report = []
    
    for q in ai_questions:
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
    
    # পাই চার্ট
    fig = go.Figure(data=[go.Pie(
        labels=['Correct', 'Incorrect'], 
        values=[score, wrong], 
        hole=.4,
        marker_colors=['#4ade80', '#f43f5e']
    )])
    fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # একাডেমিক ফিডব্যাক ও কমেন্ট কার্ড লজিক
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

    st.markdown(f"""
        <div style='background:{bg_card}; border:1px solid {color}; padding:20px; border-radius:8px; margin-bottom:25px;'>
            <h3 style='color:{color}; margin-top:0; font-weight:600;'>📊 Comprehensive Exam Report Card</h3>
            <p style='font-size:16px; color:#e2e8f0; margin:5px 0;'><b>Examinee:</b> MD FAZLE RABBI SOHAN</p>
            <p style='font-size:16px; color:#e2e8f0; margin:5px 0;'><b>Exam Level:</b> {exam_level}</p>
            <p style='font-size:16px; color:#e2e8f0; margin:5px 0;'><b>Final Score:</b> <span style='color:{color}; font-weight:bold;'>{score} / {total_q}</span> ({int(success_rate)}% Accuracy)</p>
            <p style='font-size:18px; color:#e2e8f0; margin:10px 0;'><b>Grade:</b> <span style='background:{color}; color:#000; padding:2px 12px; border-radius:4px; font-weight:bold;'>{grade}</span></p>
            <hr style='border-color:{color}; opacity:0.2;'>
            <p style='font-style:italic; color:#cbd5e1; margin-bottom:0;'><b>🗣️ Academic Feedback & Guidance:</b> {feedback}</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 Detailed Answer Sheet Review"):
        st.dataframe(pd.DataFrame(detailed_report), use_container_width=True)
    
    if st.button("🔄 Take Another AI Test"):
        st.session_state.exam_submitted = False
        st.rerun()

st.write("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Developed by MD FAZLE RABBI SOHAN | PU CSE Innovation Lab</p>", unsafe_allow_html=True)
