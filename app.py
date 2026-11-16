import streamlit as st
import pandas as pd
import os
import uuid
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from sqlalchemy import text

# ============================================================
# إعدادات الصفحة (أول أمر Streamlit)
# ============================================================
st.set_page_config(
    page_title="نظام تشخيص الأعطال الإلكترونية",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# بوابة التحقق من الهوية (Auth0)
# ============================================================
if not st.user.is_logged_in:
    st.title("🔐 تسجيل الدخول مطلوب")
    st.write("مرحبًا! يرجى تسجيل الدخول للمتابعة.")
    st.button("تسجيل الدخول", on_click=st.login)
    st.stop()

ADMIN_EMAIL = "ismailnofal65@gmail.com"  # ← ضع بريدك هنا
if st.user.email == ADMIN_EMAIL:
    user_role = "admin"
else:
    user_role = "visitor"

# ============================================================
# CSS مخصص
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); }
    h1, h2, h3, h4 { color: #ffffff !important; }
    p, label, .stMarkdown { color: #e0e0e0 !important; }
    .stSelectbox div[data-baseweb="select"] > div, .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #ffffff !important; color: #0f2027 !important; border-radius: 10px !important;
        border: 2px solid #00d4ff !important; font-size: 1.05em !important;
    }
    div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li { background-color: #ffffff !important; color: #0f2027 !important; }
    div[role="option"]:hover { background-color: #00d4ff !important; color: #ffffff !important; }
    .stSelectbox label, .stTextInput label, .stTextArea label { color: #ffffff !important; font-size: 1.3em !important; font-weight: 700 !important; }
    .stMarkdown h3 { color: #00d4ff !important; font-size: 1.7em !important; }
    .result-card { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 15px; padding: 25px; margin: 15px 0; border-right: 6px solid #00d4ff; }
    .result-card h3 { color: #00d4ff !important; }
    .cause-card { background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%); border-radius: 12px; padding: 20px; margin: 12px 0; border-right: 4px solid #ffd700; }
    .cause-card h4 { color: #ffd700 !important; }
    .solution-item { background: rgba(0, 212, 255, 0.1); border-radius: 8px; padding: 10px 15px; margin: 6px 0; border-right: 3px solid #00d4ff; color: #ffffff !important; }
    .note-item { background: rgba(255, 215, 0, 0.1); border-radius: 8px; padding: 10px 15px; margin: 6px 0; border-right: 3px solid #ffd700; color: #ffd700 !important; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f2027 0%, #203a43 100%); border-left: 3px solid #00d4ff; }
    .stButton > button { background: linear-gradient(90deg, #00d4ff, #0099cc); color: white; border-radius: 10px; font-weight: 700; width: 100%; }
    .header-box { background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%); padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 30px; }
    .header-box h1 { color: #0f2027 !important; font-size: 2.5em; }
    .header-box p { color: #0f2027 !important; }
    .stTabs [data-baseweb="tab"] { background-color: #1e3c72; color: #ffffff !important; border-radius: 10px 10px 0 0; font-weight: 700; }
    .stTabs [aria-selected="true"] { background-color: #00d4ff !important; color: #0f2027 !important; }
    .stat-box { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 15px; padding: 20px; text-align: center; border-right: 5px solid #00d4ff; }
    .stat-box .big-num { color: #00d4ff; font-size: 2.5em; font-weight: 900; display: block; }
    .delete-warning { background: rgba(255, 0, 0, 0.15); border: 2px solid #ff4444; border-radius: 12px; padding: 20px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# دوال مساعدة
# ============================================================
def get_db():
    return st.connection("postgresql", type="sql")

def load_image_bytes(path):
    try:
        with open(path, "rb") as f: return f.read()
    except: return None

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
    st.markdown(f"👤 **{st.user.name}**")
    st.caption(f"الدور: {'👑 أدمن' if user_role == 'admin' else '👁️ زائر'}")
    if st.button("تسجيل الخروج"):
        st.logout()
    
    st.markdown("---")
    conn = get_db()
    try:
        total_faults = conn.query("SELECT COUNT(*) as c FROM faults", ttl=0).iloc[0]['c']
        total_causes = conn.query("SELECT COUNT(*) as c FROM causes", ttl=0).iloc[0]['c']
        total_solutions = conn.query("SELECT COUNT(*) as c FROM solutions", ttl=0).iloc[0]['c']
        st.metric("الأعطال", total_faults)
        st.metric("الأسباب", total_causes)
        st.metric("الحلول", total_solutions)
        
        stats = conn.query("SELECT circuit_type, COUNT(*) as c FROM faults GROUP BY circuit_type", ttl=0)
        st.markdown("---")
        st.markdown("### 🔌 توزيع الدوائر")
        for _, row in stats.iterrows():
            st.metric(row['circuit_type'], row['c'])
    except Exception as e:
        st.error(f"خطأ في تحميل الإحصائيات: {e}")

# ============================================================
# التبويبات
# ============================================================
tabs_names = ["🔍 البحث والتشخيص", "🔤 البحث بالكلمة", "➕ إضافة عطل", "🧩 إدارة الأسباب", "✏️ حذف وتعديل", "📊 الإحصائيات", "🖼️ رفع صورة", "📋 عرض الكل", "🤖 الذكاء الاصطناعي"]
if user_role != "admin":
    tabs_names = ["🔍 البحث والتشخيص", "🔤 البحث بالكلمة", "📊 الإحصائيات", "📋 عرض الكل"]

tabs = st.tabs(tabs_names)
tab_map = {name: tab for name, tab in zip(tabs_names, tabs)}

# ============================================================
# التبويب 1: البحث
# ============================================================
with tab_map.get("🔍 البحث والتشخيص", st.empty()):
    st.markdown("### 🔍 اختر المعايير")
    conn = get_db()
    try:
        circuit_types = conn.query("SELECT DISTINCT circuit_type FROM faults", ttl=0)["circuit_type"].tolist()
        col1, col2 = st.columns(2)
        with col1:
            selected_circuit = st.selectbox("🔌 نوع الدائرة:", ["-- اختر --"] + circuit_types, key="circuit_search")
        with col2:
            if selected_circuit != "-- اختر --":
                symptoms = conn.query("SELECT DISTINCT symptom FROM faults WHERE circuit_type = :ct", params={"ct": selected_circuit}, ttl=0)["symptom"].tolist()
                selected_symptom = st.selectbox("📋 وصف العطل:", ["-- اختر --"] + symptoms, key="symptom_search")
            else:
                selected_symptom = "-- اختر --"
                st.selectbox("📋 وصف العطل:", ["-- اختر --"], disabled=True, key="symptom_disabled")

        if selected_circuit != "-- اختر --" and selected_symptom != "-- اختر --":
            faults = conn.query("SELECT id, component FROM faults WHERE circuit_type = :ct AND symptom = :sym", params={"ct": selected_circuit, "sym": selected_symptom}, ttl=0)
            if not faults.empty:
                st.success(f"✅ تم العثور على {len(faults)} عطل")
                for _, fault in faults.iterrows():
                    st.markdown(f'<div class="result-card"><h3>🔹 {fault["component"]}</h3></div>', unsafe_allow_html=True)
                    causes = conn.query("SELECT id, cause_text FROM causes WHERE fault_id = :fid", params={"fid": fault['id']}, ttl=0)
                    if causes.empty:
                        st.info("لا توجد أسباب مسجلة")
                    else:
                        st.markdown(f"**🎯 الأسباب المحتملة ({len(causes)}):**")
                        for _, cause in causes.iterrows():
                            solutions = conn.query("SELECT solution_text FROM solutions WHERE cause_id = :cid", params={"cid": cause['id']}, ttl=0)
                            notes = conn.query("SELECT note_text FROM notes WHERE cause_id = :cid", params={"cid": cause['id']}, ttl=0)
                            cause_html = f'<div class="cause-card"><h4>💠 {cause["cause_text"]}</h4>'
                            for _, sol in solutions.iterrows(): cause_html += f'<div class="solution-item">{sol["solution_text"]}</div>'
                            for _, note in notes.iterrows(): cause_html += f'<div class="note-item">{note["note_text"]}</div>'
                            cause_html += "</div>"
                            st.markdown(cause_html, unsafe_allow_html=True)
                    
                    images = conn.query("SELECT image_path, caption FROM images WHERE fault_id = :fid", params={"fid": fault['id']}, ttl=0)
                    if not images.empty:
                        st.markdown("**📸 صور العطل:**")
                        for _, img in images.iterrows():
                            img_data = load_image_bytes(img['image_path'])
                            if img_data: st.image(img_data, caption=img['caption'] or "", use_container_width=True)
            else:
                st.warning("⚠️ لم يتم العثور على نتائج")
    except Exception as e:
        st.error(f"خطأ: {e}")

# ============================================================
# التبويب 2: البحث بالكلمة
# ============================================================
with tab_map.get("🔤 البحث بالكلمة", st.empty()):
    st.markdown("### 🔤 البحث بالكلمة المفتاحية")
    keyword = st.text_input("🔎 الكلمة المفتاحية:", key="keyword_search")
    if keyword and keyword.strip():
        conn = get_db()
        like_pattern = f"%{keyword.strip()}%"
        try:
            found_faults = conn.query("SELECT id, circuit_type, component, symptom FROM faults WHERE component ILIKE :kw OR symptom ILIKE :kw", params={"kw": like_pattern}, ttl=0)
            found_causes = conn.query("SELECT c.id, c.cause_text, f.component FROM causes c JOIN faults f ON f.id = c.fault_id WHERE c.cause_text ILIKE :kw", params={"kw": like_pattern}, ttl=0)
            found_solutions = conn.query("SELECT s.id, s.solution_text, c.cause_text, f.component FROM solutions s JOIN causes c ON c.id = s.cause_id JOIN faults f ON f.id = c.fault_id WHERE s.solution_text ILIKE :kw", params={"kw": like_pattern}, ttl=0)
            
            total = len(found_faults) + len(found_causes) + len(found_solutions)
            if total == 0: st.warning(f"⚠️ لا توجد نتائج للكلمة: {keyword}")
            else:
                st.success(f"✅ {total} نتيجة")
                if not found_faults.empty:
                    st.markdown("#### 🔹 الأعطال")
                    for _, f in found_faults.iterrows(): st.markdown(f'<div class="result-card"><h3>🔹 {f["component"]}</h3><p>وصف العطل: {f["symptom"]}</p></div>', unsafe_allow_html=True)
                if not found_causes.empty:
                    st.markdown("#### 🎯 الأسباب")
                    for _, c in found_causes.iterrows(): st.markdown(f'<div class="cause-card"><h4>💠 {c["cause_text"]}</h4><p>من العطل: {c["component"]}</p></div>', unsafe_allow_html=True)
                if not found_solutions.empty:
                    st.markdown("#### 🛠️ الحلول")
                    for _, s in found_solutions.iterrows(): st.markdown(f'<div class="cause-card"><h4>🛠️ {s["solution_text"]}</h4><p>للسبب: {s["cause_text"]}</p></div>', unsafe_allow_html=True)
        except Exception as e: st.error(f"خطأ في البحث: {e}")

# ============================================================
# التبويب 3: إضافة عطل
# ============================================================
with tab_map.get("➕ إضافة عطل", st.empty()):
    if user_role != "admin": st.warning("⚠️ هذه الصفحة للأدمن فقط")
    else:
        st.markdown("### ➕ إضافة عطل جديد")
        conn = get_db()
        try:
            existing_circuits = conn.query("SELECT DISTINCT circuit_type FROM faults", ttl=0)["circuit_type"].tolist()
            circuit_choice = st.selectbox("🔌 نوع الدائرة:", existing_circuits + ["➕ نوع جديد..."], key="add_circuit_choice")
            circuit_type = st.text_input("✏️ اكتب نوع الدائرة الجديد:", key="add_new_circuit") if circuit_choice == "➕ نوع جديد..." else circuit_choice
            
            with st.form("add_fault_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1: component = st.text_input("🔧 القطعة الإلكترونية:", key="add_component")
                with col2: symptom = st.text_input("📋 وصف العطل:", key="add_symptom")
                
                st.markdown("#### 🎯 السبب الأول")
                probable_cause = st.text_input("السبب المحتمل:", key="add_cause")
                solution = st.text_input("🛠️ الحل المقترح:", key="add_solution")
                notes = st.text_area("💡 ملاحظات (اختياري):", key="add_notes", height=80)
                
                if st.form_submit_button("💾 حفظ العطل", use_container_width=True):
                    if not all([circuit_type, component, symptom, probable_cause, solution]):
                        st.error("❌ كل الحقول مطلوبة")
                    else:
                        with conn.session as session:
                            res = session.execute(text("INSERT INTO faults (circuit_type, component, symptom, probable_cause, solution, notes) VALUES (:ct, :c, :s, :pc, :sol, :n) RETURNING id"), 
                                                  {"ct": circuit_type.strip(), "c": component.strip(), "s": symptom.strip(), "pc": probable_cause.strip(), "sol": solution.strip(), "n": notes.strip() if notes else ""})
                            fault_id = res.fetchone()[0]
                            
                            res = session.execute(text("INSERT INTO causes (fault_id, cause_text) VALUES (:fid, :txt) RETURNING id"), {"fid": fault_id, "txt": probable_cause.strip()})
                            cause_id = res.fetchone()[0]
                            
                            session.execute(text("INSERT INTO solutions (cause_id, solution_text) VALUES (:cid, :txt)"), {"cid": cause_id, "txt": solution.strip()})
                            if notes and notes.strip(): session.execute(text("INSERT INTO notes (cause_id, note_text) VALUES (:cid, :txt)"), {"cid": cause_id, "txt": notes.strip()})
                            session.commit()
                        st.success("✅ تم الإضافة بنجاح!"); st.balloons()
        except Exception as e: st.error(f"خطأ: {e}")

# ============================================================
# التبويب 4: إدارة الأسباب
# ============================================================
with tab_map.get("🧩 إدارة الأسباب", st.empty()):
    if user_role != "admin": st.warning("⚠️ هذه الصفحة للأدمن فقط")
    else:
        st.markdown("### 🧩 إدارة الأسباب والحلول")
        conn = get_db()
        try:
            circuit_filter = st.selectbox("🔌 نوع الدائرة:", ["الكل"] + conn.query("SELECT DISTINCT circuit_type FROM faults", ttl=0)["circuit_type"].tolist(), key="mgr_circuit")
            q = "SELECT id, circuit_type, component, symptom FROM faults ORDER BY component"
            p = {}
            if circuit_filter != "الكل":
                q = "SELECT id, circuit_type, component, symptom FROM faults WHERE circuit_type = :ct ORDER BY component"
                p = {"ct": circuit_filter}
            faults_list = conn.query(q, params=p, ttl=0)
            fault_options = [f"{r['id']} | {r['component']} — {r['symptom']}" for _, r in faults_list.iterrows()]
            selected_fault_str = st.selectbox("🔧 اختر العطل:", ["-- اختر --"] + fault_options, key="mgr_fault")
            
            if selected_fault_str != "-- اختر --":
                fid = int(selected_fault_str.split(" | ")[0])
                fault_info = conn.query("SELECT * FROM faults WHERE id = :id", params={"id": fid}, ttl=0).iloc[0]
                st.markdown(f'<div class="result-card"><h3>🔹 {fault_info["component"]}</h3><p>وصف العطل: {fault_info["symptom"]}</p></div>', unsafe_allow_html=True)
                
                existing_causes = conn.query("SELECT id, cause_text FROM causes WHERE fault_id = :fid", params={"fid": fid}, ttl=0)
                if not existing_causes.empty:
                    for _, cause in existing_causes.iterrows():
                        sols = conn.query("SELECT solution_text FROM solutions WHERE cause_id = :cid", params={"cid": cause['id']}, ttl=0)
                        nts = conn.query("SELECT note_text FROM notes WHERE cause_id = :cid", params={"cid": cause['id']}, ttl=0)
                        cause_html = f'<div class="cause-card"><h4>💠 {cause["cause_text"]}</h4>'
                        for _, sol in sols.iterrows(): cause_html += f'<div class="solution-item">{sol["solution_text"]}</div>'
                        for _, note in nts.iterrows(): cause_html += f'<div class="note-item">{note["note_text"]}</div>'
                        cause_html += "</div>"
                        st.markdown(cause_html, unsafe_allow_html=True)
                
                with st.form("add_cause_form", clear_on_submit=True):
                    st.markdown("#### ➕ إضافة سبب جديد")
                    new_cause = st.text_input("🎯 نص السبب:", key="new_cause_text")
                    new_sols = [st.text_input(f"الحل {i+1}:", key=f"new_sol_{i}") for i in range(3)]
                    new_note = st.text_area("💡 ملاحظة (اختياري):", key="new_note_text", height=70)
                    if st.form_submit_button("💾 حفظ السبب", use_container_width=True):
                        if not new_cause or not any(new_sols): st.error("❌ نص السبب وحل واحد على الأقل مطلوبان")
                        else:
                            with conn.session as session:
                                res = session.execute(text("INSERT INTO causes (fault_id, cause_text) VALUES (:fid, :txt) RETURNING id"), {"fid": fid, "txt": new_cause.strip()})
                                cid = res.fetchone()[0]
                                for sol in new_sols:
                                    if sol and sol.strip(): session.execute(text("INSERT INTO solutions (cause_id, solution_text) VALUES (:cid, :txt)"), {"cid": cid, "txt": sol.strip()})
                                if new_note and new_note.strip(): session.execute(text("INSERT INTO notes (cause_id, note_text) VALUES (:cid, :txt)"), {"cid": cid, "txt": new_note.strip()})
                                session.commit()
                            st.success("✅ تم إضافة السبب!"); st.balloons()
        except Exception as e: st.error(f"خطأ: {e}")

# ============================================================
# التبويب 5: حذف وتعديل
# ============================================================
with tab_map.get("✏️ حذف وتعديل", st.empty()):
    if user_role != "admin": st.warning("⚠️ هذه الصفحة للأدمن فقط")
    else:
        st.markdown("### ✏️ حذف وتعديل البيانات")
        manage_type = st.radio("ماذا تريد أن تدير؟", ["🔹 الأعطال", "🎯 الأسباب", "🛠️ الحلول", "💡 الملاحظات"], horizontal=True, key="manage_type")
        conn = get_db()
        try:
            if manage_type == "🔹 الأعطال":
                cf = st.selectbox("🔌 تصفية:", ["الكل"] + conn.query("SELECT DISTINCT circuit_type FROM faults", ttl=0)["circuit_type"].tolist(), key="del_cf")
                q = "SELECT id, circuit_type, component, symptom FROM faults ORDER BY id"
                p = {}
                if cf != "الكل": q = "SELECT id, circuit_type, component, symptom FROM faults WHERE circuit_type = :ct ORDER BY id"; p = {"ct": cf}
                flist = conn.query(q, params=p, ttl=0)
                fopts = [f"{r['id']} | {r['component']} — {r['symptom']}" for _, r in flist.iterrows()]
                sel_f = st.selectbox("🔧 اختر العطل:", ["-- اختر --"] + fopts, key="del_fault")
                if sel_f != "-- اختر --":
                    fid = int(sel_f.split(" | ")[0])
                    finfo = conn.query("SELECT * FROM faults WHERE id = :id", params={"id": fid}, ttl=0).iloc[0]
                    st.markdown(f'<div class="result-card"><h3>🔹 {finfo["component"]}</h3><p>وصف العطل: {finfo["symptom"]}</p></div>', unsafe_allow_html=True)
                    
                    edit_tab, delete_tab = st.tabs(["✏️ تعديل", "🗑️ حذف"])
                    with edit_tab:
                        with st.form("edit_fault_form"):
                            new_ct = st.text_input("نوع الدائرة:", value=finfo['circuit_type'], key="ef_ct")
                            new_comp = st.text_input("القطعة:", value=finfo['component'], key="ef_comp")
                            new_sym = st.text_input("وصف العطل:", value=finfo['symptom'], key="ef_sym")
                            if st.form_submit_button("💾 حفظ", use_container_width=True):
                                if not all([new_ct, new_comp, new_sym]): st.error("❌ كل الحقول مطلوبة")
                                else:
                                    with conn.session as session:
                                        session.execute(text("UPDATE faults SET circuit_type=:ct, component=:c, symptom=:s WHERE id=:id"), {"ct": new_ct.strip(), "c": new_comp.strip(), "s": new_sym.strip(), "id": fid})
                                        session.commit()
                                    st.success("✅ تم التحديث!"); st.rerun()
                    with delete_tab:
                        st.markdown('<div class="delete-warning"><h4>⚠️ حذف نهائي</h4><p>سيتم حذف العطل مع كل ما يرتبط به.</p></div>', unsafe_allow_html=True)
                        c1 = st.checkbox("أفهم", key="del_f_c1")
                        c2 = st.text_input("اكتب 'حذف':", key="del_f_c2")
                        if st.button("🗑️ حذف", key="del_f_btn"):
                            if c1 and c2.strip() == "حذف":
                                with conn.session as session:
                                    session.execute(text("DELETE FROM notes WHERE cause_id IN (SELECT id FROM causes WHERE fault_id = :id)"), {"id": fid})
                                    session.execute(text("DELETE FROM solutions WHERE cause_id IN (SELECT id FROM causes WHERE fault_id = :id)"), {"id": fid})
                                    session.execute(text("DELETE FROM causes WHERE fault_id = :id"), {"id": fid})
                                    session.execute(text("DELETE FROM faults WHERE id = :id"), {"id": fid})
                                    session.commit()
                                st.success("✅ تم الحذف!"); st.balloons(); st.rerun()
                            else: st.error("❌ أكد الحذف")
        except Exception as e: st.error(f"خطأ: {e}")

# ============================================================
# التبويب 6: الإحصائيات
# ============================================================
with tab_map.get("📊 الإحصائيات", st.empty()):
    st.markdown("### 📊 لوحة الإحصائيات")
    conn = get_db()
    try:
        total_f = conn.query("SELECT COUNT(*) as c FROM faults", ttl=0).iloc[0]['c']
        total_c = conn.query("SELECT COUNT(*) as c FROM causes", ttl=0).iloc[0]['c']
        total_s = conn.query("SELECT COUNT(*) as c FROM solutions", ttl=0).iloc[0]['c']
        total_n = conn.query("SELECT COUNT(*) as c FROM notes", ttl=0).iloc[0]['c']
        total_circuits = conn.query("SELECT COUNT(DISTINCT circuit_type) as c FROM faults", ttl=0).iloc[0]['c']
        
        c1, c2, c3, c4, c5 = st.columns(5)
        for col, num, lbl, color in [(c1, total_f, "🔹 أعطال", "#00d4ff"), (c2, total_c, "🎯 أسباب", "#ffd700"), (c3, total_s, "🛠️ حلول", "#00ff88"), (c4, total_n, "💡 ملاحظات", "#ff8800"), (c5, total_circuits, "🔌 دوائر", "#ff44ff")]:
            with col: st.markdown(f'<div class="stat-box" style="border-right-color:{color};"><span class="big-num" style="color:{color};">{num}</span><span class="lbl">{lbl}</span></div>', unsafe_allow_html=True)
        
        st.markdown("#### 🔌 توزيع الأعطال حسب نوع الدائرة")
        circuit_data = conn.query("SELECT circuit_type, COUNT(*) as count FROM faults GROUP BY circuit_type", ttl=0)
        if not circuit_data.empty:
            fig_pie = px.pie(circuit_data, values='count', names='circuit_type', color_discrete_sequence=['#00d4ff', '#ffd700', '#00ff88', '#ff8800', '#ff44ff'])
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Cairo", color="#ffffff"))
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.markdown("#### 🔧 أكثر القطع تعرضًا للأعطال (Top 10)")
        components_data = conn.query("SELECT component, COUNT(*) as count FROM faults GROUP BY component ORDER BY count DESC LIMIT 10", ttl=0)
        if not components_data.empty:
            fig_bar = px.bar(components_data, x='count', y='component', orientation='h', color='count', color_continuous_scale=[[0, '#1e3c72'], [1, '#00d4ff']], text='count')
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Cairo", color="#ffffff"), coloraxis_showscale=False)
            st.plotly_chart(fig_bar, use_container_width=True)
    except Exception as e: st.error(f"خطأ: {e}")

# ============================================================
# التبويب 7: رفع صورة
# ============================================================
with tab_map.get("🖼️ رفع صورة", st.empty()):
    if user_role != "admin": st.warning("⚠️ هذه الصفحة للأدمن فقط")
    else:
        st.markdown("### 🖼️ رفع صورة الدائرة")
        conn = get_db()
        try:
            circuit_filter = st.selectbox("🔌 نوع الدائرة:", ["الكل"] + conn.query("SELECT DISTINCT circuit_type FROM faults", ttl=0)["circuit_type"].tolist(), key="img_circuit_filter")
            q = "SELECT id, circuit_type, component, symptom FROM faults ORDER BY component"
            p = {}
            if circuit_filter != "الكل": q = "SELECT id, circuit_type, component, symptom FROM faults WHERE circuit_type = :ct ORDER BY component"; p = {"ct": circuit_filter}
            faults_list = conn.query(q, params=p, ttl=0)
            fault_options = [f"{r['id']} | {r['component']} — {r['symptom']}" for _, r in faults_list.iterrows()]
            selected_fault_str = st.selectbox("🔧 اختر العطل:", ["-- اختر --"] + fault_options, key="img_fault_select")
            
            if selected_fault_str != "-- اختر --":
                fid = int(selected_fault_str.split(" | ")[0])
                fault_info = conn.query("SELECT * FROM faults WHERE id = :id", params={"id": fid}, ttl=0).iloc[0]
                st.markdown(f'<div class="result-card"><h3>🔹 {fault_info["component"]}</h3><p>وصف العطل: {fault_info["symptom"]}</p></div>', unsafe_allow_html=True)
                
                existing_images = conn.query("SELECT id, image_path, caption FROM images WHERE fault_id = :fid", params={"fid": fid}, ttl=0)
                if not existing_images.empty:
                    st.markdown("#### 📸 الصور الحالية")
                    for _, img in existing_images.iterrows():
                        img_data = load_image_bytes(img['image_path'])
                        if img_data: st.image(img_data, caption=img['caption'] or "", use_container_width=True)
                
                with st.form("upload_image_form", clear_on_submit=True):
                    uploaded_file = st.file_uploader("📁 اختر صورة:", type=["jpg", "jpeg", "png"], key="img_uploader")
                    caption = st.text_input("📝 وصف الصورة (اختياري):", key="img_caption")
                    if st.form_submit_button("💾 حفظ الصورة", use_container_width=True):
                        if not uploaded_file: st.error("❌ اختر صورة")
                        else:
                            os.makedirs("uploads", exist_ok=True)
                            ext = uploaded_file.name.split(".")[-1].lower()
                            unique_name = f"fault_{fid}_{uuid.uuid4().hex[:8]}.{ext}"
                            save_path = os.path.join("uploads", unique_name)
                            with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
                            with conn.session as session:
                                session.execute(text("INSERT INTO images (fault_id, image_path, caption) VALUES (:fid, :path, :cap)"), {"fid": fid, "path": save_path, "cap": caption.strip() if caption else ""})
                                session.commit()
                            st.success("✅ تم رفع الصورة!"); st.balloons()
                            st.image(load_image_bytes(save_path), use_container_width=True)
        except Exception as e: st.error(f"خطأ: {e}")

# ============================================================
# التبويب 8: عرض الكل
# ============================================================
with tab_map.get("📋 عرض الكل", st.empty()):
    st.markdown("### 📋 جميع الأعطال")
    conn = get_db()
    try:
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
        all_faults = conn.query(query, ttl=0)
        filter_circuit = st.selectbox("🔍 تصفية:", ["الكل"] + all_faults['circuit_type'].unique().tolist(), key="filter_circuit_all")
        if filter_circuit != "الكل": all_faults = all_faults[all_faults['circuit_type'] == filter_circuit]
        display_df = all_faults.rename(columns={'id': 'المعرف', 'circuit_type': 'نوع الدائرة', 'component': 'القطعة', 'symptom': 'وصف العطل', 'causes_count': 'عدد الأسباب', 'solutions_count': 'عدد الحلول', 'images_count': 'عدد الصور'})
        st.dataframe(display_df, width='stretch', height=450)
        st.caption(f"إجمالي الأعطال: {len(all_faults)}")
    except Exception as e: st.error(f"خطأ: {e}")
# ============================================================
# التبويب 9: الذكاء الاصطناعي (Computer Vision)
# ============================================================
with tab_map.get("🤖 الذكاء الاصطناعي", st.empty()):
    st.markdown("### 🤖 تحليل الصور بالذكاء الاصطناعي")
    st.markdown("ارفع صورة للوحة دوائر إلكترونية، وسيقوم النموذج بالتعرف على مكوناتها.")

    from ultralytics import YOLO
    import numpy as np

    # تحميل النموذج (مع التخزين المؤقت لتجنب التحميل المتكرر)
    from huggingface_hub import hf_hub_download

    @st.cache_resource
    def load_pcb_model():
        try:
            # تحميل النموذج تلقائياً من Hugging Face
            model_path = hf_hub_download(
                repo_id="JcProg/PCBInspect-AI", 
                filename="YoloV12-Medium-160-FineTuned.pt"
            )
            return YOLO(model_path)
        except Exception as e:
            st.error(f"❌ فشل تحميل النموذج: {e}")
            return None

    model = load_pcb_model()

    if model is None:
        st.stop()

    uploaded_file_ai = st.file_uploader("📸 اختر صورة للوحة الدوائر:", type=["jpg", "jpeg", "png"], key="ai_uploader")

    if uploaded_file_ai is not None:
        # عرض الصورة الأصلية
        image_ai = Image.open(uploaded_file_ai)
        st.image(image_ai, caption="الصورة الأصلية", width='stretch')

        # تحويل الصورة إلى مصفوفة
        img_array_ai = np.array(image_ai)

        with st.spinner("🔍 جاري تحليل الصورة..."):
            results_ai = model(img_array_ai)
            res_plotted_ai = results_ai[0].plot()

            st.success("✅ تم تحليل الصورة!")
            st.image(res_plotted_ai, caption="نتيجة التحليل", width='stretch')

            st.markdown("### 🔍 القطع التي تم اكتشافها:")
            names_ai = results_ai[0].names
            boxes_ai = results_ai[0].boxes

            if len(boxes_ai) == 0:
                st.warning("⚠️ لم يتم اكتشاف أي قطع معروفة في الصورة.")
            else:
                for box in boxes_ai:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    st.write(f"- **{names_ai[class_id]}** (بدقة: {confidence*100:.1f}%)")
# ============================================================
# تذييل
# ============================================================
st.markdown("---")
st.markdown("<p style='text-align:center; color:#00d4ff;'>💡 مشروع تشخيص الأعطال الإلكترونية — v3.0 (PostgreSQL + Auth0) 💚</p>", unsafe_allow_html=True)