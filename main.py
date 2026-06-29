import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import random

# ১. পেজ সেটিংস ও উচ্চ-কন্ট্রাস্ট মার্জিত থিম (High-Contrast Academic Theme)
st.set_page_config(page_title="DiscreteMind AI", page_icon="🧠", layout="centered")

# কাস্টম CSS: টেক্সট কালার একদম স্পষ্ট এবং রিডিবল করার জন্য ফিক্স
st.markdown("""
    <style>
    /* মেইন ব্যাকগ্রাউন্ড */
    .stApp {
        background-color: #0f172a;
    }
    /* সাধারণ সব লেখার কালার উজ্জ্বল সাদা করা হলো যেন স্পষ্ট পড়া যায় */
    .stApp, p, span, label, li {
        color: #f8fafc !important;
        font-size: 16px;
    }
    /* টাইটেল ও হেডিং স্টাইলিಂಗ್ */
    h1 {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
    }
    h2, h3, h4 {
        color: #38bdf8 !important;
        font-weight: 600 !important;
    }
    /* জেমিনি এআই থেকে আসা আউটপুট টেক্সট ও LaTeX ব্লকের ভেতরের লেখার কালার ফিক্স */
    div[data-testid="stMarkdownContainer"] {
        color: #f1f5f9 !important;
    }
    .katex {
        color: #38bdf8 !important; /* গাণিতিক সূত্রগুলো হাইলাইট করার জন্য */
        font-size: 1.05em !important;
    }
    /* বাটন ডিজাইন */
    .stButton>button {
        background: #0284c7 !important;
        color: #ffffff !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: #0369a1 !important;
        transform: translateY(-1px);
    }
    /* ফর্ম ও কার্ড সেটিংস */
    div[data-testid="stForm"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }
    /* কন্টেইনার বক্স */
    div[data-testid="stBlock"] {
        color: #f8fafc !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 DiscreteMind AI: Universal Course Solver")
st.subheader("Omni-Topic Discrete Mathematics Engine & Interactive Exam Lab")
st.write("Presidency University | CSE Dept | Academic Edition")
st.write("---")

# ২. প্রফেশনাল সাইডবার ড্যাশবোর্ড
st.sidebar.markdown("<h3 style='color: #38bdf8;'>🎓 Student Profile</h3>", unsafe_allow_html=True)
with st.sidebar.container(border=True):
    st.write("**Project Target:** Universal Math Solver & Mock Test")
    st.write("**Developer:** MD FAZLE RABBI SOHAN")
    st.write("**Institution:** Presidency University")
    st.write("**Department:** CSE")
    st.markdown("<span style='color: #4ade80; font-weight: bold;'>🔥 Core AI Engine: Active</span>", unsafe_allow_html=True)

st.sidebar.write("---")
st.sidebar.page_link("https://presidency.edu.bd/", label="Presidency University Portal", icon="🏫")

# ৩. স্ট্রিমলিট সিক্রেটস থেকে এপিআই কি রিড করা
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None

# ৪. ইউনিভার্সাল সিঙ্গেল ইনপুট ইন্টারফেস
st.markdown("<h3 style='color: #38bdf8;'>🚀 Universal Math Input Box</h3>", unsafe_allow_html=True)
st.caption("💡 ট্রুথ টেবিল, সেট, গ্রাফ থিওরি, ট্রি, পারমিউটেশন, প্রব্যাবিলিটি বা রিকুরেন্স রিলেশন—যেকোনো গাণিতিক প্রশ্ন নিচের বক্সে লেখো:")

user_query = st.text_area(
    "📝 তোমার ডিসক্রিট ম্যাথের প্রশ্নটি এখানে টাইপ করো বা পেস্ট করো:",
    value="",
    placeholder="যেমন: In a class of 50 students, 30 like C and 25 like Java...",
    height=120
)

if st.button("🚀 এক্সপার্ট এআই समाधान জেনারেট করো", use_container_width=True):
    if not user_query.strip():
        st.warning("⚠️ দয়া করে আগে ইনপুট বক্সে কোনো প্রশ্ন লিখো!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for percent_complete in range(10, 101, 30):
            time.sleep(0.1)
            progress_bar.progress(percent_complete)
            status_text.markdown(f"⚙️ **এআই ওমনি-পার্সার ম্যাথ অ্যানালাইসিস করছে... {percent_complete}%**")
            
        with st.spinner("✨ সমাধান একাডেমিক স্ট্যান্ডার্ডে ফরম্যাট করা হচ্ছে..."):
            try:
                if GEMINI_API_KEY:
                    genai.configure(api_key=GEMINI_API_KEY)
                    model = genai.GenerativeModel(model_name='gemini-2.5-flash')
                    prompt = f"You are an expert university professor in Discrete Mathematics. Provide a rigorous, step-by-step, textbook-style solution for the student's query. Use clean and correct LaTeX formatting for matrices or formulas: {user_query}"
                    response = model.generate_content(prompt)
                    output_text = response.text
                else:
                    output_text = "\n⚠️ **System Note:** Please add your `GEMINI_API_KEY` in Streamlit Secrets to solve custom questions live."
            except Exception as e:
                output_text = f"❌ API Method Access Error: {e}. অনুগ্রহ করে নিশ্চিত করুন যে আপনার API key-টি সচল এবং সঠিক পারমিশনযুক্ত।"
            
            status_text.empty()
            progress_bar.empty()
            st.balloons()
            st.success("🎉 সমাধান সফলভাবে জেনারেট হয়েছে!")
            with st.container(border=True):
                st.markdown(output_text)

st.write("---")

# 🧠 ৫. ইন্টারেক্টিভ মক টেস্ট সিমুলেটর
st.markdown("<h3 style='color: #38bdf8;'>📝 Interactive Mid/Final Mock Test</h3>", unsafe_allow_html=True)
st.caption("💡 এটি একটি রিয়েল-টাইম এক্সাম ল্যাব। প্রশ্নগুলোর উত্তর সিলেক্ট করার সাথে সাথে তোমার লাইভ প্র唝্রেস বার আপডেট হবে।")

if 'mock_seed' not in st.session_state or st.sidebar.button("🔄 প্রশ্নপত্র নতুন করে জেনারেট করো"):
    st.session_state.mock_seed = random.randint(1, 9999)
    st.session_state.test_submitted = False
    st.session_state.answers = {}

random.seed(st.session_state.mock_seed)
nodes_count = random.randint(4, 6)
max_edges = int(nodes_count * (nodes_count - 1) / 2)
subset_n = random.randint(3, 5)

questions_list = [
    {
        "id": 1,
        "topic": "Graph Theory",
        "question": f"১. একটি Simple Graph-এ যদি মোট নোড বা ভার্টেক্স সংখ্যা {nodes_count} হয়, তবে গ্রাফটিতে সর্বোচ্চ কতটি এজ (Edges) থাকতে পারে?",
        "options": [f"{nodes_count}টি", f"{max_edges}টি", f"{nodes_count * 2}টি"],
        "correct": f"{max_edges}টি"
    },
    {
        "id": 2,
        "topic": "Graph Theory",
        "question": "২. ডিসক্রিট ম্যাথে একটি কানেক্টেড গ্রাফে যদি কোনো সাইকেল (Cycle) না থাকে, তবে তাকে কী বলা হয়?",
        "options": ["Tree (বৃক্ষ)", "Complete Graph", "Bipartite Graph"],
        "correct": "Tree (বৃক্ষ)"
    },
    {
        "id": 3,
        "topic": "Set Theory & Relations",
        "question": f"৩. একটি সেটে উপাদান সংখ্যা {subset_n} হলে, সেটটির রিফ্লেক্সিভ রিলেশন (Reflexive Relations) এর সংখ্যা কতটি হবে?",
        "options": [f"2^{subset_n * (subset_n - 1)}টি", f"2^{subset_n**2}টি", f"{2**subset_n}টি"],
        "correct": f"2^{subset_n * (subset_n - 1)}টি"
    },
    {
        "topic": "Set Theory & Relations",
        "id": 4,
        "question": "৪. যদি কোনো ফাংশন একই সাথে One-to-One এবং Onto হয়, তবে তাকে কী ধরণের ফাংশন বলা হয়?",
        "options": ["Bijective Function", "Surjective Function", "Injective Function"],
        "correct": "Bijective Function"
    },
    {
        "topic": "Propositional Logic",
        "id": 5,
        "question": "৫. প্রপোজিশনাল লজিকের নিয়ম অনুযায়ী, একটি কন্ডিশনাল উক্তি P → Q কখন একমাত্র মিথ্যা (False) হয়?",
        "options": ["যখন P সত্য এবং Q মিথ্যা", "যখন দুটি উক্তিই মিথ্যা হয়", "যখন P মিথ্যা এবং Q সত্য"],
        "correct": "যখন P সত্য এবং Q মিথ্যা"
    }
]

# লাইভ প্রগ্রেস ট্র্যাকিং
answered_count = sum(1 for q in questions_list if st.session_state.answers.get(q['id']) is not None)
completion_rate = answered_count / len(questions_list)

if not st.session_state.test_submitted:
    st.markdown(f"**📝 তোমার পরীক্ষার প্রগ্রেস:** {answered_count} / 5 টি প্রশ্নের উত্তর দিয়েছ")
    st.progress(completion_rate)
    
    with st.form("mock_test_form"):
        st.markdown("<p style='color:#f43f5e; font-weight:bold;'>⏱️ পরীক্ষার নিয়মাবলী: নিচে ৫টি প্রশ্ন দেওয়া আছে। প্রতিটি প্রশ্নের জন্য ১ মার্কস। কোনো নেগেটিভ মার্কিং নেই।</p>", unsafe_allow_html=True)
        st.write("---")
        
        for q in questions_list:
            st.markdown(f"#### **{q['question']}**")
            st.markdown(f"<span style='background-color:#334155; padding:4px 8px; border-radius:4px; color:#38bdf8; font-size:14px;'>🏷️ টপিক: {q['topic']}</span>", unsafe_allow_html=True)
            
            st.session_state.answers[q['id']] = st.radio(
                "সভিক উত্তরটি সিলেক্ট করো:", 
                q['options'], 
                key=f"mock_ans_{q['id']}_{st.session_state.mock_seed}"
            )
            st.write("---")
            
        submit_test = st.form_submit_button("📤 সাবমিট মক টেস্ট (Submit Exam)")
        
        if submit_test:
            st.session_state.test_submitted = True
            st.rerun()

else:
    # 🎯 ইভালুয়েশন ও অ্যাকাডেমিক ফিডব্যাক কার্ড
    st.balloons()
    
    score = 0
    detailed_report = []
    
    for q in questions_list:
        user_ans = st.session_state.answers.get(q['id'])
        is_correct = user_ans == q['correct']
        if is_correct:
            score += 1
        detailed_report.append({
            "প্রশ্ন": q['question'],
            "তোমার উত্তর": user_ans,
            "সঠিক উত্তর": q['correct'],
            "ফলাফল": "✅ সঠিক" if is_correct else "❌ ভুল"
        })
        
    success_rate = (score / 5) * 100
    if score == 5:
        grade, color, bg_card = "A+", "#4ade80", "rgba(74, 222, 128, 0.1)"
        feedback = "অসাধারণ পারফরম্যান্স! তোমার ডিসক্রিট ম্যাথ প্রিপারেশন ১০০% পারফেক্ট। ল্যাব ফাইনাল এবং থিওরিতে তুমি নির্ঘাত ফুল মার্কস পাচ্ছো। কিপ ইট আপ!"
    elif score >= 4:
        grade, color, bg_card = "A", "#38bdf8", "rgba(56, 189, 248, 0.1)"
        feedback = "খুব ভালো পারফরম্যান্স! মাইনর কিছু গ্যাপ ছাড়া তোমার বেসিক কনসেপ্ট বেশ পরিষ্কার। ভুল হওয়া প্রশ্নগুলো আরেকবার রিভিশন দিলে ল্যাবে চমৎকার এ-প্লাস নিশ্চিত।"
    elif score >= 2:
        grade, color, bg_card = "B", "#fbbf24", "rgba(251, 191, 36, 0.1)"
        feedback = "মাঝারি পারফরম্যান্স। গ্রাফ থিওরি এবং লজিকের কিছু জায়গায় তোমার এখনও ঘাটতি রয়েছে। ল্যাব লেকচার শিটগুলো ভালোভাবে রিভিশন দেওয়ার পরামর্শ দেওয়া হলো।"
    else:
        grade, color, bg_card = "F (Fail)", "#f43f5e", "rgba(244, 63, 94, 0.1)"
        feedback = "অসন্তোষজনক স্কোর। ডিসক্রিট ম্যাথমেটিক্সের মূল থিওরিগুলো তোমার আরেকবার স্ক্র্যাচ থেকে পড়া উচিত। পরীক্ষার আগে কোনো টপিক বুঝতে সমস্যা হলে উপরের এআই সলভার ইঞ্জিন ব্যবহার করে প্র্যাকটিস করো।"

    # মার্জিত প্রফেশনাল রিপোর্ট কার্ড ড্যাশবোর্ড
    st.markdown(f"""
        <div style='background:{bg_card}; border:1px solid {color}; padding:20px; border-radius:8px; margin-bottom:25px;'>
            <h3 style='color:{color}; margin-top:0; font-weight:600;'>📊 Comprehensive Exam Report Card</h3>
            <p style='font-size:16px; color:#e2e8f0; margin:5px 0;'><b>পরীক্ষার্থী:</b> MD FAZLE RABBI SOHAN</p>
            <p style='font-size:16px; color:#e2e8f0; margin:5px 0;'><b>প্রাপ্ত স্কোর:</b> <span style='color:{color}; font-weight:bold;'>{score} / 5</span> ({int(success_rate)}% Accuracy)</p>
            <p style='font-size:18px; color:#e2e8f0; margin:10px 0;'><b>ফাইনাল গ্রেড:</b> <span style='background:{color}; color:#000; padding:2px 12px; border-radius:4px; font-weight:bold;'>{grade}</span></p>
            <hr style='border-color:{color}; opacity:0.2;'>
            <p style='font-style:italic; color:#cbd5e1; margin-bottom:0;'><b>🗣️ একাডেমিক ফিডব্যাক ও গাইডলাইন:</b> {feedback}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # বিস্তারিত রিভিউ টেবিল
    with st.expander("🔍 প্রশ্নভিত্তিক উত্তরপত্র পর্যালোচনা (Detailed Answer Review)"):
        df_report = pd.DataFrame(detailed_report)
        st.dataframe(df_report, use_container_width=True)

    if st.button("🔄 নতুন প্রশ্নপত্রে আবার মক টেস্ট দাও"):
        st.session_state.mock_seed = random.randint(1, 9999)
        st.session_state.test_submitted = False
        st.session_state.answers = {}
        st.rerun()

st.write("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Developed by MD FAZLE RABBI SOHAN | PU CSE Innovation Lab</p>", unsafe_allow_html=True)
