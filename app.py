import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image
import uuid
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title="نظام تشخيص الأعطال الإلكترونية",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS مخصص
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    }

    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-family: 'Cairo', sans-serif !important;
    }

    p, label, .stMarkdown {
        color: #e0e0e0 !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #0f2027 !important;
        border-radius: 10px !important;
        border: 2px solid #00d4ff !important;
        font-size: 1.1em !important;
        font-weight: 600 !important;
    }

    .stSelectbox div[data-baseweb="select"] * {
        color: #0f2027 !important;
        font-size: 1.05em !important;
    }

    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[role="listbox"],
    div[role="option"] {
        background-color: #ffffff !important;
        color: #0f2027 !important;
        font-size: 1.05em !important;
    }

    div[role="option"]:hover,
    div[data-baseweb="popover"] li:hover {
        background-color: #00d4ff !important;
        color: #ffffff !important;
    }

    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #ffffff !important;
        color: #0f2027 !important;
        border-radius: 10px !important;
        border: 2px solid #00d4ff !important;
        font-size: 1.05em !important;
        font-weight: 600 !important;
    }

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #888888 !important;
    }

    .stSelectbox label,
    .stSelectbox label p,
    .stTextInput label,
    .stTextArea label {
        color: #ffffff !important;
        font-size: 1.3em !important;
        font-weight: 700 !important;
    }

    .stMarkdown h3 {
        color: #00d4ff !important;
        font-size: 1.7em !important;
        font-weight: 700 !important;
    }

    .result-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        border-right: 6px solid #00d4ff;
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.2);
    }

    .result-card h3 {
        color: #00d4ff !important;
        margin-bottom: 15px;
        font-size: 1.4em !important;
    }

    .cause-card {
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        border-right: 4px solid #ffd700;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.15);
    }

    .cause-card h4 {
        color: #ffd700 !important;
        margin-bottom: 12px;
        font-size: 1.2em !important;
    }

    .solution-item {
        background: rgba(0, 212, 255, 0.1);
        border-radius: 8px;
        padding: 10px 15px;
        margin: 6px 0;
        border-right: 3px solid #00d4ff;
        color: #ffffff !important;
        font-size: 1.05em;
    }

    .solution-item::before {
        content: "🛠️ ";
        margin-left: 5px;
    }

    .note-item {
        background: rgba(255, 215, 0, 0.1);
        border-radius: 8px;
        padding: 10px 15px;
        margin: 6px 0;
        border-right: 3px solid #ffd700;
        color: #ffd700 !important;
        font-size: 0.95em;
        font-style: italic;
    }

    .note-item::before {
        content: "💡 ";
        margin-left: 5px;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 100%);
        border-left: 3px solid #00d4ff;
    }

    .stButton > button {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: 700;
        font-family: 'Cairo', sans-serif;
        transition: all 0.3s;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #0099cc, #00d4ff);
        transform: scale(1.02);
    }

    .header-box {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
    }

    .header-box h1 {
        color: #0f2027 !important;
        font-size: 2.5em;
        margin: 0;
    }

    .header-box p {
        color: #0f2027 !important;
        font-size: 1.1em;
        margin-top: 10px;
    }

    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #1e3c72;
        color: #ffffff !important;
        border-radius: 10px 10px 0 0;
        padding: 10px 18px;
        font-size: 0.95em;
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        background-color: #00d4ff !important;
        color: #0f2027 !important;
    }

    .stAlert p {
        color: #0f2027 !important;
        font-weight: 600 !important;
    }

    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #00d4ff, transparent);
        margin: 20px 0;
    }

    .search-metric {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border-right: 4px solid #00d4ff;
        margin: 5px 0;
    }

    .search-metric .num {
        color: #00d4ff;
        font-size: 1.8em;
        font-weight: 900;
    }

    .search-metric .label {
        color: #ffffff;
        font-size: 0.95em;
    }

    .delete-warning {
        background: rgba(255, 0, 0, 0.15);
        border: 2px solid #ff4444;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
    }

    .delete-warning h4 {
        color: #ff4444 !important;
        margin-bottom: 10px;
    }

    .delete-warning p {
        color: #ffffff !important;
    }

    .stat-box {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border-right: 5px solid #00d4ff;
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.2);
        margin: 8px 0;
    }

    .stat-box .big-num {
        color: #00d4ff;
        font-size: 2.5em;
        font-weight: 900;
        display: block;
    }

    .stat-box .lbl {
        color: #ffffff;
        font-size: 1em;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# دالة الاتصال
# ============================================================
def get_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faults.db")
    return sqlite3.connect(db_path)
def load_image_bytes(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except Exception:
        return None

# ============================================================
# رأس الصفحة
# ============================================================
st.markdown("""
<div class="header-box">
    <h1>🔧 نظام تشخيص الأعطال الإلكترونية</h1>
    <p>تشخيص ذكي، إدارة كاملة، وإحصائيات تفاعلية</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# الشريط الجانبي
# ============================================================
with st.sidebar:
    st.markdown("### 📊 إحصائيات سريعة")
    conn = get_connection()
    total_faults = pd.read_sql_query("SELECT COUNT(*) as c FROM faults", conn).iloc[0]['c']
    total_causes = pd.read_sql_query("SELECT COUNT(*) as c FROM causes", conn).iloc[0]['c']
    total_solutions = pd.read_sql_query("SELECT COUNT(*) as c FROM solutions", conn).iloc[0]['c']
    
    st.metric("الأعطال", total_faults)
    st.metric("الأسباب", total_causes)
    st.metric("الحلول", total_solutions)
    
    stats = pd.read_sql_query(
        "SELECT circuit_type, COUNT(*) as c FROM faults GROUP BY circuit_type",
        conn
    )
    st.markdown("---")
    st.markdown("### 🔌 توزيع الدوائر")
    for _, row in stats.iterrows():
        st.metric(row['circuit_type'], row['c'])
    
    conn.close()
    
    st.markdown("---")
    st.markdown("### 💡 الإصدار")
    st.caption("v2.5.1 — إحصائيات ورسوم بيانية")

# ============================================================
# التبويبات
# ============================================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🔍 البحث والتشخيص",
    "🔤 البحث بالكلمة",
    "➕ إضافة عطل",
    "🧩 إدارة الأسباب",
    "✏️ حذف وتعديل",
    "📊 الإحصائيات",
    "🖼️ رفع صورة",
    "📋 عرض الكل"
])

# ============================================================
# التبويب 1: البحث
# ============================================================
with tab1:
    st.markdown("### 🔍 اختر المعايير")
    
    conn = get_connection()
    circuit_types = pd.read_sql_query(
        "SELECT DISTINCT circuit_type FROM faults", conn
    )["circuit_type"].tolist()
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_circuit = st.selectbox(
            "🔌 نوع الدائرة:",
            ["-- اختر --"] + circuit_types,
            key="circuit_search"
        )
    
    with col2:
        if selected_circuit != "-- اختر --":
            symptoms = pd.read_sql_query(
                "SELECT DISTINCT symptom FROM faults WHERE circuit_type = ?",
                conn, params=(selected_circuit,)
            )["symptom"].tolist()
            selected_symptom = st.selectbox(
                "📋 وصف العطل:",
                ["-- اختر --"] + symptoms,
                key="symptom_search"
            )
        else:
            selected_symptom = "-- اختر --"
            st.selectbox("📋 وصف العطل:", ["-- اختر --"], disabled=True, key="symptom_disabled")
    
    if selected_circuit != "-- اختر --" and selected_symptom != "-- اختر --":
        faults = pd.read_sql_query(
            """SELECT id, component FROM faults 
               WHERE circuit_type = ? AND symptom = ?""",
            conn, params=(selected_circuit, selected_symptom)
        )
        
        if not faults.empty:
            st.success(f"✅ تم العثور على {len(faults)} عطل")
            
            for _, fault in faults.iterrows():
                st.markdown(f"""
                <div class="result-card">
                    <h3>🔹 {fault['component']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                causes = pd.read_sql_query(
                    "SELECT id, cause_text FROM causes WHERE fault_id = ?",
                    conn, params=(fault['id'],)
                )
                
                if causes.empty:
                    st.info("لا توجد أسباب مسجلة لهذا العطل بعد")
                else:
                    st.markdown(f"**🎯 الأسباب المحتملة ({len(causes)}):**")
                    
                    for _, cause in causes.iterrows():
                        solutions = pd.read_sql_query(
                            "SELECT solution_text FROM solutions WHERE cause_id = ?",
                            conn, params=(cause['id'],)
                        )
                        notes = pd.read_sql_query(
                            "SELECT note_text FROM notes WHERE cause_id = ?",
                            conn, params=(cause['id'],)
                        )
                        
                        cause_html = f"""
                        <div class="cause-card">
                            <h4>💠 {cause['cause_text']}</h4>
                        """
                        for _, sol in solutions.iterrows():
                            cause_html += f'<div class="solution-item">{sol["solution_text"]}</div>'
                        for _, note in notes.iterrows():
                            cause_html += f'<div class="note-item">{note["note_text"]}</div>'
                        cause_html += "</div>"
                        st.markdown(cause_html, unsafe_allow_html=True)
                                        # عرض صور العطل
                fault_images = pd.read_sql_query(
                    "SELECT image_path, caption FROM images WHERE fault_id = ?",
                    conn, params=(fault['id'],)
                )
                if not fault_images.empty:
                    st.markdown(f"**📸 صور العطل ({len(fault_images)}):**")
                    img_cols = st.columns(min(len(fault_images), 3))
                    for idx, (_, img_row) in enumerate(fault_images.iterrows()):
                        img_bytes = load_image_bytes(img_row['image_path'])
                        if img_bytes:
                            with img_cols[idx % 3]:
                                st.image(img_bytes, caption=img_row['caption'] or "", use_container_width=True)
        else:
            st.warning("⚠️ لم يتم العثور على نتائج مطابقة")
    
    conn.close()

# ============================================================
# التبويب 2: البحث بالكلمة
# ============================================================
with tab2:
    st.markdown("### 🔤 البحث بالكلمة المفتاحية")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        keyword = st.text_input(
            "🔎 الكلمة المفتاحية:",
            placeholder="مثال: مكثف، مرحل، جهد، تلف، افحص...",
            key="keyword_search"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_btn = st.button("🔍 ابحث", use_container_width=True)
    
    with st.expander("⚙️ خيارات البحث المتقدم"):
        search_in = st.multiselect(
            "ابحث في:",
            ["نوع الدائرة", "القطعة", "وصف العطل", "الأسباب", "الحلول", "الملاحظات"],
            default=["القطعة", "وصف العطل", "الأسباب", "الحلول"],
            key="search_in"
        )
    
    if keyword and keyword.strip():
        conn = get_connection()
        like_pattern = f"%{keyword.strip()}%"
        
        fault_conditions = []
        if "نوع الدائرة" in search_in:
            fault_conditions.append("circuit_type LIKE ?")
        if "القطعة" in search_in:
            fault_conditions.append("component LIKE ?")
        if "وصف العطل" in search_in:
            fault_conditions.append("symptom LIKE ?")
        
        found_faults = pd.DataFrame()
        if fault_conditions:
            fault_query = f"SELECT id, circuit_type, component, symptom FROM faults WHERE {' OR '.join(fault_conditions)}"
            params = [like_pattern] * len(fault_conditions)
            found_faults = pd.read_sql_query(fault_query, conn, params=params)
        
        found_causes = pd.DataFrame()
        if "الأسباب" in search_in:
            found_causes = pd.read_sql_query(
                """SELECT c.id, c.cause_text, f.component, f.circuit_type, f.id as fault_id
                   FROM causes c JOIN faults f ON f.id = c.fault_id
                   WHERE c.cause_text LIKE ?""",
                conn, params=(like_pattern,)
            )
        
        found_solutions = pd.DataFrame()
        if "الحلول" in search_in:
            found_solutions = pd.read_sql_query(
                """SELECT s.id, s.solution_text, c.cause_text, f.component, f.circuit_type, f.id as fault_id
                   FROM solutions s
                   JOIN causes c ON c.id = s.cause_id
                   JOIN faults f ON f.id = c.fault_id
                   WHERE s.solution_text LIKE ?""",
                conn, params=(like_pattern,)
            )
        
        found_notes = pd.DataFrame()
        if "الملاحظات" in search_in:
            found_notes = pd.read_sql_query(
                """SELECT n.id, n.note_text, c.cause_text, f.component, f.circuit_type, f.id as fault_id
                   FROM notes n
                   JOIN causes c ON c.id = n.cause_id
                   JOIN faults f ON f.id = c.fault_id
                   WHERE n.note_text LIKE ?""",
                conn, params=(like_pattern,)
            )
        
        conn.close()
        
        t_f, t_c, t_s, t_n = len(found_faults), len(found_causes), len(found_solutions), len(found_notes)
        total = t_f + t_c + t_s + t_n
        
        if total == 0:
            st.warning(f"⚠️ لم يتم العثور على نتائج للكلمة: **{keyword}**")
        else:
            st.success(f"✅ {total} نتيجة للكلمة: **{keyword}**")
            
            c1, c2, c3, c4 = st.columns(4)
            for col, num, lbl in [(c1, t_f, "🔹 أعطال"), (c2, t_c, "🎯 أسباب"), (c3, t_s, "🛠️ حلول"), (c4, t_n, "💡 ملاحظات")]:
                with col:
                    st.markdown(f'<div class="search-metric"><div class="num">{num}</div><div class="label">{lbl}</div></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            if t_f > 0:
                st.markdown(f"#### 🔹 الأعطال ({t_f})")
                for _, fault in found_faults.iterrows():
                    st.markdown(f"""
                    <div class="result-card">
                        <h3>🔹 {fault['component']}</h3>
                        <p><strong>الدائرة:</strong> {fault['circuit_type']}</p>
                        <p><strong>وصف العطل:</strong> {fault['symptom']}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            if t_c > 0:
                st.markdown(f"#### 🎯 الأسباب ({t_c})")
                for _, cause in found_causes.iterrows():
                    st.markdown(f"""
                    <div class="cause-card">
                        <h4>💠 {cause['cause_text']}</h4>
                        <p style="color:#00d4ff; font-size:0.9em;">من العطل: <strong>{cause['component']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            if t_s > 0:
                st.markdown(f"#### 🛠️ الحلول ({t_s})")
                for _, sol in found_solutions.iterrows():
                    st.markdown(f"""
                    <div class="cause-card">
                        <h4>🛠️ {sol['solution_text']}</h4>
                        <p style="color:#ffd700; font-size:0.9em;">للسبب: <em>{sol['cause_text']}</em></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            if t_n > 0:
                st.markdown(f"#### 💡 الملاحظات ({t_n})")
                for _, note in found_notes.iterrows():
                    st.markdown(f"""
                    <div class="cause-card">
                        <h4>💡 {note['note_text']}</h4>
                        <p style="color:#ffd700; font-size:0.9em;">للسبب: <em>{note['cause_text']}</em></p>
                    </div>
                    """, unsafe_allow_html=True)
    
    elif not keyword:
        st.info("💡 اكتب كلمة في حقل البحث أعلاه")

# ============================================================
# التبويب 3: إضافة عطل جديد
# ============================================================
with tab3:
    st.markdown("### ➕ إضافة عطل جديد")
    
    conn = get_connection()
    existing_circuits = pd.read_sql_query("SELECT DISTINCT circuit_type FROM faults", conn)["circuit_type"].tolist()
    
    st.markdown("#### 🔌 نوع الدائرة")
    circuit_choice = st.selectbox(
        "اختر نوع الدائرة أو أضف نوعًا جديدًا:",
        existing_circuits + ["➕ نوع جديد..."],
        key="add_circuit_choice"
    )
    
    if circuit_choice == "➕ نوع جديد...":
        circuit_type = st.text_input("✏️ اكتب نوع الدائرة الجديد:", placeholder="مثال: دائرة الصوت", key="add_new_circuit")
    else:
        circuit_type = circuit_choice
    
    st.markdown("---")
    
    with st.form("add_fault_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            component = st.text_input("🔧 القطعة الإلكترونية:", placeholder="مثال: مكثف تنعيم", key="add_component")
        with col2:
            symptom = st.text_input("📋 وصف العطل:", placeholder="مثال: الجهاز لا يعمل نهائيًا", key="add_symptom")
        
        st.markdown("#### 🎯 السبب الأول")
        probable_cause = st.text_input("السبب المحتمل:", placeholder="مثال: مكثف منتفخ أو جاف", key="add_cause")
        solution = st.text_input("🛠️ الحل المقترح:", placeholder="مثال: استبدال بنفس القيمة", key="add_solution")
        notes = st.text_area("💡 ملاحظات (اختياري):", key="add_notes", height=80)
        
        submitted = st.form_submit_button("💾 حفظ العطل", use_container_width=True)
        
        if submitted:
            errors = []
            if not circuit_type or circuit_type.strip() == "": errors.append("❌ نوع الدائرة مطلوب")
            if not component or component.strip() == "": errors.append("❌ القطعة مطلوبة")
            if not symptom or symptom.strip() == "": errors.append("❌ وصف العطل مطلوب")
            if not probable_cause or probable_cause.strip() == "": errors.append("❌ السبب مطلوب")
            if not solution or solution.strip() == "": errors.append("❌ الحل مطلوب")
            
            if errors:
                for err in errors: st.error(err)
            else:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO faults (circuit_type, component, symptom, probable_cause, solution, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    (circuit_type.strip(), component.strip(), symptom.strip(), probable_cause.strip(), solution.strip(), notes.strip() if notes else "")
                )
                fault_id = cursor.lastrowid
                cursor.execute("INSERT INTO causes (fault_id, cause_text) VALUES (?, ?)", (fault_id, probable_cause.strip()))
                cause_id = cursor.lastrowid
                cursor.execute("INSERT INTO solutions (cause_id, solution_text) VALUES (?, ?)", (cause_id, solution.strip()))
                if notes and notes.strip():
                    cursor.execute("INSERT INTO notes (cause_id, note_text) VALUES (?, ?)", (cause_id, notes.strip()))
                conn.commit()
                st.success(f"✅ تم إضافة العطل! (المعرف: {fault_id})")
                st.balloons()
    
    conn.close()

# ============================================================
# التبويب 4: إدارة الأسباب والحلول
# ============================================================
with tab4:
    st.markdown("### 🧩 إدارة الأسباب والحلول")
    
    conn = get_connection()
    
    col1, col2 = st.columns(2)
    with col1:
        circuit_filter = st.selectbox(
            "🔌 نوع الدائرة:",
            ["الكل"] + pd.read_sql_query("SELECT DISTINCT circuit_type FROM faults", conn)["circuit_type"].tolist(),
            key="mgr_circuit"
        )
    
    if circuit_filter == "الكل":
        faults_list = pd.read_sql_query("SELECT id, circuit_type, component, symptom FROM faults ORDER BY circuit_type, component", conn)
    else:
        faults_list = pd.read_sql_query("SELECT id, circuit_type, component, symptom FROM faults WHERE circuit_type = ? ORDER BY component", conn, params=(circuit_filter,))
    
    fault_options = [f"{r['id']} | {r['component']} — {r['symptom']}" for _, r in faults_list.iterrows()]
    
    with col2:
        selected_fault_str = st.selectbox("🔧 اختر العطل:", ["-- اختر --"] + fault_options, key="mgr_fault")
    
    if selected_fault_str != "-- اختر --":
        fault_id = int(selected_fault_str.split(" | ")[0])
        fault_info = pd.read_sql_query("SELECT * FROM faults WHERE id = ?", conn, params=(fault_id,)).iloc[0]
        
        st.markdown(f"""
        <div class="result-card">
            <h3>🔹 {fault_info['component']}</h3>
            <p><strong>الدائرة:</strong> {fault_info['circuit_type']}</p>
            <p><strong>وصف العطل:</strong> {fault_info['symptom']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        existing_causes = pd.read_sql_query("SELECT id, cause_text FROM causes WHERE fault_id = ?", conn, params=(fault_id,))
        
        if existing_causes.empty:
            st.info("لا توجد أسباب — أضف أول سبب أدناه ⬇️")
        else:
            st.markdown(f"#### 2️⃣ الأسباب الحالية ({len(existing_causes)})")
            for _, cause in existing_causes.iterrows():
                sols = pd.read_sql_query("SELECT solution_text FROM solutions WHERE cause_id = ?", conn, params=(cause['id'],))
                nts = pd.read_sql_query("SELECT note_text FROM notes WHERE cause_id = ?", conn, params=(cause['id'],))
                
                cause_html = f'<div class="cause-card"><h4>💠 {cause["cause_text"]}</h4>'
                for _, sol in sols.iterrows():
                    cause_html += f'<div class="solution-item">{sol["solution_text"]}</div>'
                for _, note in nts.iterrows():
                    cause_html += f'<div class="note-item">{note["note_text"]}</div>'
                cause_html += "</div>"
                st.markdown(cause_html, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 3️⃣ إضافة سبب جديد")
        
        with st.form("add_cause_form", clear_on_submit=True):
            new_cause = st.text_input("🎯 نص السبب الجديد:", placeholder="مثال: مكثف مسرب", key="new_cause_text")
            st.markdown("**🛠️ الحلول (أضف حلًا واحدًا على الأقل):**")
            new_solutions = []
            for i in range(3):
                sol = st.text_input(f"الحل {i+1}:", key=f"new_sol_{i}")
                if sol and sol.strip():
                    new_solutions.append(sol.strip())
            new_note = st.text_area("💡 ملاحظة (اختياري):", key="new_note_text", height=70)
            
            if st.form_submit_button("💾 حفظ السبب الجديد", use_container_width=True):
                if not new_cause or new_cause.strip() == "":
                    st.error("❌ نص السبب مطلوب")
                elif not new_solutions:
                    st.error("❌ يجب إضافة حل واحد على الأقل")
                else:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO causes (fault_id, cause_text) VALUES (?, ?)", (fault_id, new_cause.strip()))
                    cause_id = cursor.lastrowid
                    for sol in new_solutions:
                        cursor.execute("INSERT INTO solutions (cause_id, solution_text) VALUES (?, ?)", (cause_id, sol))
                    if new_note and new_note.strip():
                        cursor.execute("INSERT INTO notes (cause_id, note_text) VALUES (?, ?)", (cause_id, new_note.strip()))
                    conn.commit()
                    st.success(f"✅ تم إضافة السبب مع {len(new_solutions)} حل!")
                    st.balloons()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        if not existing_causes.empty:
            st.markdown("#### 4️⃣ إضافة حل لسبب موجود")
            cause_options = [f"{r['id']} | {r['cause_text']}" for _, r in existing_causes.iterrows()]
            selected_cause = st.selectbox("اختر السبب:", cause_options, key="mgr_cause_add_sol")
            
            if selected_cause:
                cause_id = int(selected_cause.split(" | ")[0])
                with st.form("add_solution_form", clear_on_submit=True):
                    new_sol_for_cause = st.text_input("🛠️ الحل الجديد:", key="add_sol_existing")
                    new_note_for_cause = st.text_area("💡 ملاحظة (اختياري):", key="add_note_existing", height=60)
                    
                    if st.form_submit_button("💾 حفظ الحل", use_container_width=True):
                        if not new_sol_for_cause or new_sol_for_cause.strip() == "":
                            st.error("❌ نص الحل مطلوب")
                        else:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO solutions (cause_id, solution_text) VALUES (?, ?)", (cause_id, new_sol_for_cause.strip()))
                            if new_note_for_cause and new_note_for_cause.strip():
                                cursor.execute("INSERT INTO notes (cause_id, note_text) VALUES (?, ?)", (cause_id, new_note_for_cause.strip()))
                            conn.commit()
                            st.success("✅ تم إضافة الحل!")
                            st.balloons()
    
    conn.close()

# ============================================================
# التبويب 5: حذف وتعديل
# ============================================================
with tab5:
    st.markdown("### ✏️ حذف وتعديل البيانات")
    
    manage_type = st.radio(
        "ماذا تريد أن تدير؟",
        ["🔹 الأعطال", "🎯 الأسباب", "🛠️ الحلول", "💡 الملاحظات"],
        horizontal=True,
        key="manage_type"
    )
    
    conn = get_connection()
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    if manage_type == "🔹 الأعطال":
        col1, col2 = st.columns(2)
        with col1:
            cf = st.selectbox("🔌 تصفية:", ["الكل"] + pd.read_sql_query("SELECT DISTINCT circuit_type FROM faults", conn)["circuit_type"].tolist(), key="del_cf")
        
        if cf == "الكل":
            flist = pd.read_sql_query("SELECT id, circuit_type, component, symptom FROM faults ORDER BY circuit_type, id", conn)
        else:
            flist = pd.read_sql_query("SELECT id, circuit_type, component, symptom FROM faults WHERE circuit_type = ? ORDER BY id", conn, params=(cf,))
        
        fopts = [f"{r['id']} | {r['component']} — {r['symptom']}" for _, r in flist.iterrows()]
        
        with col2:
            sel_f = st.selectbox("🔧 اختر العطل:", ["-- اختر --"] + fopts, key="del_fault")
        
        if sel_f != "-- اختر --":
            fid = int(sel_f.split(" | ")[0])
            finfo = pd.read_sql_query("SELECT * FROM faults WHERE id = ?", conn, params=(fid,)).iloc[0]
            
            st.markdown(f"""
            <div class="result-card">
                <h3>🔹 {finfo['component']}</h3>
                <p><strong>الدائرة:</strong> {finfo['circuit_type']}</p>
                <p><strong>وصف العطل:</strong> {finfo['symptom']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            nc = pd.read_sql_query("SELECT COUNT(*) as c FROM causes WHERE fault_id = ?", conn, params=(fid,)).iloc[0]['c']
            ns = pd.read_sql_query("SELECT COUNT(*) as c FROM solutions WHERE cause_id IN (SELECT id FROM causes WHERE fault_id = ?)", conn, params=(fid,)).iloc[0]['c']
            st.info(f"مرتبط بـ **{nc}** سبب و **{ns}** حل")
            
            edit_tab, delete_tab = st.tabs(["✏️ تعديل", "🗑️ حذف"])
            
            with edit_tab:
                with st.form("edit_fault_form"):
                    new_ct = st.text_input("نوع الدائرة:", value=finfo['circuit_type'], key="ef_ct")
                    new_comp = st.text_input("القطعة:", value=finfo['component'], key="ef_comp")
                    new_sym = st.text_input("وصف العطل:", value=finfo['symptom'], key="ef_sym")
                    
                    if st.form_submit_button("💾 حفظ", use_container_width=True):
                        if not new_ct.strip() or not new_comp.strip() or not new_sym.strip():
                            st.error("❌ كل الحقول مطلوبة")
                        else:
                            cur = conn.cursor()
                            cur.execute("UPDATE faults SET circuit_type=?, component=?, symptom=? WHERE id=?", (new_ct.strip(), new_comp.strip(), new_sym.strip(), fid))
                            conn.commit()
                            st.success("✅ تم التحديث!")
                            st.rerun()
            
            with delete_tab:
                st.markdown(f"""
                <div class="delete-warning">
                    <h4>⚠️ تحذير: حذف نهائي</h4>
                    <p>سيتم حذف العطل مع {nc} سبب و {ns} حل.</p>
                </div>
                """, unsafe_allow_html=True)
                
                confirm1 = st.checkbox("أفهم أن الحذف نهائي", key="del_f_c1")
                confirm_text = st.text_input("اكتب **حذف** للتأكيد:", key="del_f_c2")
                
                if st.button("🗑️ حذف نهائيًا", key="del_f_btn"):
                    if not confirm1:
                        st.error("❌ أكد الفهم أولًا")
                    elif confirm_text.strip() != "حذف":
                        st.error("❌ اكتب 'حذف'")
                    else:
                        cur = conn.cursor()
                        cur.execute("DELETE FROM notes WHERE cause_id IN (SELECT id FROM causes WHERE fault_id = ?)", (fid,))
                        cur.execute("DELETE FROM solutions WHERE cause_id IN (SELECT id FROM causes WHERE fault_id = ?)", (fid,))
                        cur.execute("DELETE FROM causes WHERE fault_id = ?", (fid,))
                        cur.execute("DELETE FROM faults WHERE id = ?", (fid,))
                        conn.commit()
                        st.success("✅ تم الحذف!")
                        st.balloons()
                        st.rerun()
    
    elif manage_type == "🎯 الأسباب":
        causes_list = pd.read_sql_query(
            "SELECT c.id, c.cause_text, f.component FROM causes c JOIN faults f ON f.id = c.fault_id ORDER BY f.component, c.id", conn
        )
        copts = [f"{r['id']} | {r['cause_text']} — من: {r['component']}" for _, r in causes_list.iterrows()]
        sel_c = st.selectbox("🎯 اختر السبب:", ["-- اختر --"] + copts, key="del_cause")
        
        if sel_c != "-- اختر --":
            cid = int(sel_c.split(" | ")[0])
            cinfo = pd.read_sql_query("SELECT c.*, f.component FROM causes c JOIN faults f ON f.id = c.fault_id WHERE c.id = ?", conn, params=(cid,)).iloc[0]
            ns = pd.read_sql_query("SELECT COUNT(*) as c FROM solutions WHERE cause_id = ?", conn, params=(cid,)).iloc[0]['c']
            
            st.markdown(f"""
            <div class="cause-card">
                <h4>💠 {cinfo['cause_text']}</h4>
                <p style="color:#00d4ff;">من العطل: <strong>{cinfo['component']}</strong></p>
            </div>
            """, unsafe_allow_html=True)
            st.info(f"مرتبط بـ **{ns}** حل")
            
            edit_tab, delete_tab = st.tabs(["✏️ تعديل", "🗑️ حذف"])
            
            with edit_tab:
                with st.form("edit_cause_form"):
                    new_cause = st.text_input("نص السبب:", value=cinfo['cause_text'], key="ec_text")
                    if st.form_submit_button("💾 حفظ", use_container_width=True):
                        if not new_cause.strip():
                            st.error("❌ نص السبب مطلوب")
                        else:
                            cur = conn.cursor()
                            cur.execute("UPDATE causes SET cause_text=? WHERE id=?", (new_cause.strip(), cid))
                            conn.commit()
                            st.success("✅ تم التحديث!")
                            st.rerun()
            
            with delete_tab:
                st.markdown(f'<div class="delete-warning"><h4>⚠️ حذف نهائي</h4><p>سيتم حذف السبب مع {ns} حل.</p></div>', unsafe_allow_html=True)
                confirm1 = st.checkbox("أفهم", key="del_c_c1")
                confirm_text = st.text_input("اكتب **حذف** للتأكيد:", key="del_c_c2")
                if st.button("🗑️ حذف نهائيًا", key="del_c_btn"):
                    if not confirm1:
                        st.error("❌ أكد الفهم")
                    elif confirm_text.strip() != "حذف":
                        st.error("❌ اكتب 'حذف'")
                    else:
                        cur = conn.cursor()
                        cur.execute("DELETE FROM notes WHERE cause_id = ?", (cid,))
                        cur.execute("DELETE FROM solutions WHERE cause_id = ?", (cid,))
                        cur.execute("DELETE FROM causes WHERE id = ?", (cid,))
                        conn.commit()
                        st.success("✅ تم الحذف!")
                        st.balloons()
                        st.rerun()
    
    elif manage_type == "🛠️ الحلول":
        sols_list = pd.read_sql_query(
            "SELECT s.id, s.solution_text, c.cause_text, f.component FROM solutions s JOIN causes c ON c.id = s.cause_id JOIN faults f ON f.id = c.fault_id ORDER BY f.component, s.id", conn
        )
        sopts = [f"{r['id']} | {r['solution_text'][:60]}... — من: {r['component']}" for _, r in sols_list.iterrows()]
        sel_s = st.selectbox("🛠️ اختر الحل:", ["-- اختر --"] + sopts, key="del_solution")
        
        if sel_s != "-- اختر --":
            sid = int(sel_s.split(" | ")[0])
            sinfo = pd.read_sql_query(
                "SELECT s.*, c.cause_text, f.component FROM solutions s JOIN causes c ON c.id = s.cause_id JOIN faults f ON f.id = c.fault_id WHERE s.id = ?",
                conn, params=(sid,)
            ).iloc[0]
            
            st.markdown(f"""
            <div class="cause-card">
                <h4>🛠️ {sinfo['solution_text']}</h4>
                <p style="color:#ffd700;">للسبب: <em>{sinfo['cause_text']}</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            edit_tab, delete_tab = st.tabs(["✏️ تعديل", "🗑️ حذف"])
            
            with edit_tab:
                with st.form("edit_solution_form"):
                    new_sol = st.text_input("نص الحل:", value=sinfo['solution_text'], key="es_text")
                    if st.form_submit_button("💾 حفظ", use_container_width=True):
                        if not new_sol.strip():
                            st.error("❌ نص الحل مطلوب")
                        else:
                            cur = conn.cursor()
                            cur.execute("UPDATE solutions SET solution_text=? WHERE id=?", (new_sol.strip(), sid))
                            conn.commit()
                            st.success("✅ تم التحديث!")
                            st.rerun()
            
            with delete_tab:
                st.markdown(f'<div class="delete-warning"><h4>⚠️ حذف</h4><p>{sinfo["solution_text"]}</p></div>', unsafe_allow_html=True)
                confirm1 = st.checkbox("أفهم", key="del_s_c1")
                confirm_text = st.text_input("اكتب **حذف** للتأكيد:", key="del_s_c2")
                if st.button("🗑️ حذف نهائيًا", key="del_s_btn"):
                    if not confirm1:
                        st.error("❌ أكد الفهم")
                    elif confirm_text.strip() != "حذف":
                        st.error("❌ اكتب 'حذف'")
                    else:
                        cur = conn.cursor()
                        cur.execute("DELETE FROM solutions WHERE id = ?", (sid,))
                        conn.commit()
                        st.success("✅ تم الحذف!")
                        st.balloons()
                        st.rerun()
    
    elif manage_type == "💡 الملاحظات":
        notes_list = pd.read_sql_query(
            "SELECT n.id, n.note_text, c.cause_text, f.component FROM notes n JOIN causes c ON c.id = n.cause_id JOIN faults f ON f.id = c.fault_id ORDER BY f.component, n.id", conn
        )
        
        if notes_list.empty:
            st.info("لا توجد ملاحظات")
        else:
            nopts = [f"{r['id']} | {r['note_text'][:60]}... — من: {r['component']}" for _, r in notes_list.iterrows()]
            sel_n = st.selectbox("💡 اختر الملاحظة:", ["-- اختر --"] + nopts, key="del_note")
            
            if sel_n != "-- اختر --":
                nid = int(sel_n.split(" | ")[0])
                ninfo = pd.read_sql_query(
                    "SELECT n.*, c.cause_text, f.component FROM notes n JOIN causes c ON c.id = n.cause_id JOIN faults f ON f.id = c.fault_id WHERE n.id = ?",
                    conn, params=(nid,)
                ).iloc[0]
                
                st.markdown(f'<div class="note-item" style="font-size:1.1em;">{ninfo["note_text"]}</div>', unsafe_allow_html=True)
                
                edit_tab, delete_tab = st.tabs(["✏️ تعديل", "🗑️ حذف"])
                
                with edit_tab:
                    with st.form("edit_note_form"):
                        new_note = st.text_input("نص الملاحظة:", value=ninfo['note_text'], key="en_text")
                        if st.form_submit_button("💾 حفظ", use_container_width=True):
                            if not new_note.strip():
                                st.error("❌ النص مطلوب")
                            else:
                                cur = conn.cursor()
                                cur.execute("UPDATE notes SET note_text=? WHERE id=?", (new_note.strip(), nid))
                                conn.commit()
                                st.success("✅ تم التحديث!")
                                st.rerun()
                
                with delete_tab:
                    st.markdown(f'<div class="delete-warning"><h4>⚠️ حذف</h4><p>{ninfo["note_text"]}</p></div>', unsafe_allow_html=True)
                    confirm1 = st.checkbox("أفهم", key="del_n_c1")
                    confirm_text = st.text_input("اكتب **حذف** للتأكيد:", key="del_n_c2")
                    if st.button("🗑️ حذف نهائيًا", key="del_n_btn"):
                        if not confirm1:
                            st.error("❌ أكد الفهم")
                        elif confirm_text.strip() != "حذف":
                            st.error("❌ اكتب 'حذف'")
                        else:
                            cur = conn.cursor()
                            cur.execute("DELETE FROM notes WHERE id = ?", (nid,))
                            conn.commit()
                            st.success("✅ تم الحذف!")
                            st.balloons()
                            st.rerun()
    
    conn.close()

# ============================================================
# التبويب 6: الإحصائيات والرسوم البيانية
# ============================================================
with tab6:
    st.markdown("### 📊 لوحة الإحصائيات والرسوم البيانية")
    
    conn = get_connection()
    
    # بطاقات الإحصائيات
    total_f = pd.read_sql_query("SELECT COUNT(*) as c FROM faults", conn).iloc[0]['c']
    total_c = pd.read_sql_query("SELECT COUNT(*) as c FROM causes", conn).iloc[0]['c']
    total_s = pd.read_sql_query("SELECT COUNT(*) as c FROM solutions", conn).iloc[0]['c']
    total_n = pd.read_sql_query("SELECT COUNT(*) as c FROM notes", conn).iloc[0]['c']
    total_circuits = pd.read_sql_query("SELECT COUNT(DISTINCT circuit_type) as c FROM faults", conn).iloc[0]['c']
    
    c1, c2, c3, c4, c5 = st.columns(5)
    for col, num, lbl, color in [
        (c1, total_f, "🔹 أعطال", "#00d4ff"),
        (c2, total_c, "🎯 أسباب", "#ffd700"),
        (c3, total_s, "🛠️ حلول", "#00ff88"),
        (c4, total_n, "💡 ملاحظات", "#ff8800"),
        (c5, total_circuits, "🔌 دوائر", "#ff44ff"),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-box" style="border-right-color:{color};">
                <span class="big-num" style="color:{color};">{num}</span>
                <span class="lbl">{lbl}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # رسم 1: توزيع الأعطال حسب نوع الدائرة (Pie)
    st.markdown("#### 🔌 توزيع الأعطال حسب نوع الدائرة")
    
    circuit_data = pd.read_sql_query(
        "SELECT circuit_type, COUNT(*) as count FROM faults GROUP BY circuit_type",
        conn
    )
    
    fig_pie = px.pie(
        circuit_data,
        values='count',
        names='circuit_type',
        color_discrete_sequence=['#00d4ff', '#ffd700', '#00ff88', '#ff8800', '#ff44ff', '#44aaff', '#ff4444', '#aa44ff']
    )
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Cairo", color="#ffffff", size=14),
        legend=dict(font=dict(color="#ffffff")),
        margin=dict(t=30, b=30, l=30, r=30),
        height=400
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # رسم 2: أكثر القطع تعرضًا للأعطال (Bar)
    st.markdown("#### 🔧 أكثر القطع تعرضًا للأعطال (Top 10)")
    
    components_data = pd.read_sql_query(
        "SELECT component, COUNT(*) as count FROM faults GROUP BY component ORDER BY count DESC LIMIT 10",
        conn
    )
    
    fig_bar = px.bar(
        components_data,
        x='count',
        y='component',
        orientation='h',
        color='count',
        color_continuous_scale=[[0, '#1e3c72'], [0.5, '#00d4ff'], [1, '#0099cc']],
        text='count'
    )
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Cairo", color="#ffffff", size=13),
        xaxis=dict(title="عدد الأعطال", color="#ffffff", gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(title="القطعة", color="#ffffff"),
        margin=dict(t=30, b=30, l=30, r=30),
        height=450,
        coloraxis_showscale=False
    )
    fig_bar.update_traces(textposition='outside', textfont_color="#ffffff")
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # صف: رسمان جانبيان
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### 🎯 الأعطال حسب عدد الأسباب")
        
        causes_per_fault = pd.read_sql_query(
            """SELECT f.component, COUNT(c.id) as causes_count
               FROM faults f LEFT JOIN causes c ON c.fault_id = f.id
               GROUP BY f.id ORDER BY causes_count DESC LIMIT 10""",
            conn
        )
        
        fig_causes = px.bar(
            causes_per_fault,
            x='component',
            y='causes_count',
            color='causes_count',
            color_continuous_scale=[[0, '#1e3c72'], [0.5, '#ffd700'], [1, '#ffaa00']],
            text='causes_count'
        )
        fig_causes.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Cairo", color="#ffffff", size=12),
            xaxis=dict(title="", color="#ffffff", tickangle=-45),
            yaxis=dict(title="عدد الأسباب", color="#ffffff", gridcolor="rgba(255,255,255,0.1)"),
            margin=dict(t=30, b=80, l=30, r=30),
            height=400,
            coloraxis_showscale=False
        )
        fig_causes.update_traces(textposition='outside', textfont_color="#ffffff")
        st.plotly_chart(fig_causes, use_container_width=True)
    
    with col_b:
        st.markdown("#### 🛠️ توزيع الحلول (Top 10 أسباب)")
        
        sols_per_cause = pd.read_sql_query(
            """SELECT c.cause_text, COUNT(s.id) as sols_count
               FROM causes c LEFT JOIN solutions s ON s.cause_id = c.id
               GROUP BY c.id ORDER BY sols_count DESC LIMIT 10""",
            conn
        )
        
        fig_sols = px.bar(
            sols_per_cause,
            x='cause_text',
            y='sols_count',
            color='sols_count',
            color_continuous_scale=[[0, '#1e3c72'], [0.5, '#00ff88'], [1, '#00cc66']],
            text='sols_count'
        )
        fig_sols.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Cairo", color="#ffffff", size=12),
            xaxis=dict(title="", color="#ffffff", tickangle=-45),
            yaxis=dict(title="عدد الحلول", color="#ffffff", gridcolor="rgba(255,255,255,0.1)"),
            margin=dict(t=30, b=80, l=30, r=30),
            height=400,
            coloraxis_showscale=False
        )
        fig_sols.update_traces(textposition='outside', textfont_color="#ffffff")
        st.plotly_chart(fig_sols, use_container_width=True)
    
    # جدول ملخص
    st.markdown("#### 📋 ملخص شامل لكل دائرة")
    
    summary = pd.read_sql_query(
        """SELECT 
             f.circuit_type as 'نوع الدائرة',
             COUNT(DISTINCT f.id) as 'عدد الأعطال',
             COUNT(DISTINCT c.id) as 'عدد الأسباب',
             COUNT(DISTINCT s.id) as 'عدد الحلول',
             COUNT(DISTINCT n.id) as 'عدد الملاحظات'
           FROM faults f
           LEFT JOIN causes c ON c.fault_id = f.id
           LEFT JOIN solutions s ON s.cause_id = c.id
           LEFT JOIN notes n ON n.cause_id = c.id
           GROUP BY f.circuit_type
           ORDER BY f.circuit_type""",
        conn
    )
    st.dataframe(summary, width='stretch', height=300)
    
    conn.close()

# ============================================================
# التبويب 7: رفع الصور
# ============================================================
with tab7:
    st.markdown("### 🖼️ رفع صورة الدائرة")
    st.markdown("اختر عطلًا موجودًا وارفع صورة الدائرة المعطلة")
    
    conn = get_connection()
    
    # اختيار العطل
    col1, col2 = st.columns(2)
    with col1:
        circuit_filter = st.selectbox(
            "🔌 نوع الدائرة:",
            ["الكل"] + pd.read_sql_query("SELECT DISTINCT circuit_type FROM faults", conn)["circuit_type"].tolist(),
            key="img_circuit_filter"
        )
    
    if circuit_filter == "الكل":
        faults_list = pd.read_sql_query(
            "SELECT id, circuit_type, component, symptom FROM faults ORDER BY circuit_type, component", conn
        )
    else:
        faults_list = pd.read_sql_query(
            "SELECT id, circuit_type, component, symptom FROM faults WHERE circuit_type = ? ORDER BY component",
            conn, params=(circuit_filter,)
        )
    
    fault_options = [f"{r['id']} | {r['component']} — {r['symptom']}" for _, r in faults_list.iterrows()]
    
    with col2:
        selected_fault_str = st.selectbox(
            "🔧 اختر العطل:",
            ["-- اختر --"] + fault_options,
            key="img_fault_select"
        )
    
    if selected_fault_str != "-- اختر --":
        fault_id = int(selected_fault_str.split(" | ")[0])
        
        fault_info = pd.read_sql_query(
            "SELECT * FROM faults WHERE id = ?", conn, params=(fault_id,)
        ).iloc[0]
        
        st.markdown(f"""
        <div class="result-card">
            <h3>🔹 {fault_info['component']}</h3>
            <p><strong>الدائرة:</strong> {fault_info['circuit_type']}</p>
            <p><strong>وصف العطل:</strong> {fault_info['symptom']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # عرض الصور الحالية
        st.markdown("#### 📸 الصور الحالية لهذا العطل")
        
        existing_images = pd.read_sql_query(
            "SELECT id, image_path, caption, uploaded_at FROM images WHERE fault_id = ? ORDER BY uploaded_at DESC",
            conn, params=(fault_id,)
        )
        
        if existing_images.empty:
            st.info("لا توجد صور مسجلة لهذا العطل بعد")
        else:
            n_cols = 3
            cols = st.columns(n_cols)
            for i, (_, img) in enumerate(existing_images.iterrows()):
                with cols[i % n_cols]:
    
                    img_data = load_image_bytes(img['image_path'])
                    if img_data:
                        st.image(img_data, caption=img['caption'] or "", use_container_width=True)
                    else:
                        st.warning(f"⚠️ الصورة غير موجودة: {img['image_path']}")
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # رفع صورة جديدة
        st.markdown("#### ➕ رفع صورة جديدة")
        
        with st.form("upload_image_form", clear_on_submit=True):
            uploaded_file = st.file_uploader(
                "📁 اختر صورة (JPG / PNG):",
                type=["jpg", "jpeg", "png"],
                key="img_uploader"
            )
            
            caption = st.text_input(
                "📝 وصف الصورة (اختياري):",
                placeholder="مثال: الصورة من الأعلى بعد الفك",
                key="img_caption"
            )
            
            submit_img = st.form_submit_button("💾 حفظ الصورة", use_container_width=True)
            
            if submit_img:
                if uploaded_file is None:
                    st.error("❌ يجب اختيار صورة أولًا")
                else:
                    # حفظ الصورة
                    ext = uploaded_file.name.split(".")[-1].lower()
                    unique_name = f"fault_{fault_id}_{uuid.uuid4().hex[:8]}.{ext}"
                    save_path = os.path.join("uploads", unique_name)
                    
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # حفظ في قاعدة البيانات
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO images (fault_id, image_path, caption) VALUES (?, ?, ?)",
                        (fault_id, save_path, caption.strip() if caption else "")
                    )
                    conn.commit()
                    
                    st.success(f"✅ تم رفع الصورة بنجاح! (المعرف: {cursor.lastrowid})")
                    img_data = load_image_bytes(save_path)
                    if img_data:
                        st.image(img_data, caption="الصورة المرفوعة", use_container_width=True)                    
                    st.balloons()
        
        # حذف صورة
        if not existing_images.empty:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown("#### 🗑️ حذف صورة")
            
            img_options = [f"{r['id']} | {r['caption'] or 'بدون وصف'} — {r['uploaded_at']}" for _, r in existing_images.iterrows()]
            selected_img = st.selectbox("اختر الصورة:", ["-- اختر --"] + img_options, key="img_delete_select")
            
            if selected_img != "-- اختر --":
                img_id = int(selected_img.split(" | ")[0])
                img_record = pd.read_sql_query(
                    "SELECT * FROM images WHERE id = ?", conn, params=(img_id,)
                ).iloc[0]
                
                confirm_del = st.checkbox("أفهم أن الحذف نهائي", key="img_del_confirm")
                
                if st.button("🗑️ حذف الصورة", key="img_del_btn"):
                    if not confirm_del:
                        st.error("❌ أكد الفهم أولًا")
                    else:
                        # حذف الملف من القرص
                        if os.path.exists(img_record['image_path']):
                            os.remove(img_record['image_path'])
                        
                        # حذف من قاعدة البيانات
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM images WHERE id = ?", (img_id,))
                        conn.commit()
                        
                        st.success("✅ تم حذف الصورة!")
                        st.rerun()
    
    conn.close()

# ============================================================
# التبويب 8: عرض الكل
# ============================================================
with tab8:
    st.markdown("### 📋 جميع الأعطال")
    
    conn = get_connection()
    query = """
    SELECT f.id, f.circuit_type, f.component, f.symptom,
           COUNT(DISTINCT c.id) as causes_count,
           COUNT(DISTINCT s.id) as solutions_count,
           COUNT(DISTINCT i.id) as images_count
    FROM faults f
    LEFT JOIN causes c ON c.fault_id = f.id
    LEFT JOIN solutions s ON s.cause_id = c.id
    LEFT JOIN images i ON i.fault_id = f.id
    GROUP BY f.id ORDER BY f.circuit_type, f.id
    """
    all_faults = pd.read_sql_query(query, conn)
    
    filter_circuit = st.selectbox("🔍 تصفية:", ["الكل"] + all_faults['circuit_type'].unique().tolist(), key="filter_circuit_all")
    if filter_circuit != "الكل":
        all_faults = all_faults[all_faults['circuit_type'] == filter_circuit]
    
    display_df = all_faults.rename(columns={
        'id': 'المعرف', 'circuit_type': 'نوع الدائرة', 'component': 'القطعة',
        'symptom': 'وصف العطل', 'causes_count': 'عدد الأسباب', 
        'solutions_count': 'عدد الحلول', 'images_count': 'عدد الصور'
    })
    st.dataframe(display_df, width='stretch', height=450)
    st.caption(f"إجمالي الأعطال: {len(all_faults)}")
    conn.close()
    
    conn = get_connection()
    query = """
    SELECT f.id, f.circuit_type, f.component, f.symptom,
           COUNT(DISTINCT c.id) as causes_count,
           COUNT(DISTINCT s.id) as solutions_count
    FROM faults f
    LEFT JOIN causes c ON c.fault_id = f.id
    LEFT JOIN solutions s ON s.cause_id = c.id
    GROUP BY f.id ORDER BY f.circuit_type, f.id
    """
    all_faults = pd.read_sql_query(query, conn)
    
    filter_circuit = st.selectbox("🔍 تصفية:", ["الكل"] + all_faults['circuit_type'].unique().tolist(), key="filter_circuit")
    if filter_circuit != "الكل":
        all_faults = all_faults[all_faults['circuit_type'] == filter_circuit]
    
    display_df = all_faults.rename(columns={
        'id': 'المعرف', 'circuit_type': 'نوع الدائرة', 'component': 'القطعة',
        'symptom': 'وصف العطل', 'causes_count': 'عدد الأسباب', 'solutions_count': 'عدد الحلول'
    })
    st.dataframe(display_df, width='stretch', height=450)
    st.caption(f"إجمالي الأعطال: {len(all_faults)}")
    conn.close()

# ============================================================
# تذييل
# ============================================================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#00d4ff;'>💡 مشروع تشخيص الأعطال الإلكترونية — v2.5.1 (إحصائيات ورسوم بيانية) 💚</p>",
    unsafe_allow_html=True
)