import sqlite3
import os

DB_NAME = "faults.db"

# ============================================================
# 1. الاتصال بقاعدة البيانات
# ============================================================
if not os.path.exists(DB_NAME):
    print("❌ خطأ: قاعدة البيانات faults.db غير موجودة!")
    print("   شغّل init_database.py أولًا.")
    exit()

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

print("✅ تم الاتصال بقاعدة البيانات")

# ============================================================
# 2. إنشاء الجداول الجديدة
# ============================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS causes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fault_id INTEGER NOT NULL,
    cause_text TEXT NOT NULL,
    FOREIGN KEY (fault_id) REFERENCES faults(id) ON DELETE CASCADE
)
""")
print("✅ تم إنشاء جدول causes")

cursor.execute("""
CREATE TABLE IF NOT EXISTS solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cause_id INTEGER NOT NULL,
    solution_text TEXT NOT NULL,
    FOREIGN KEY (cause_id) REFERENCES causes(id) ON DELETE CASCADE
)
""")
print("✅ تم إنشاء جدول solutions")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cause_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    FOREIGN KEY (cause_id) REFERENCES causes(id) ON DELETE CASCADE
)
""")
print("✅ تم إنشاء جدول notes")

# ============================================================
# 3. ترحيل البيانات الحالية
# ============================================================
# نقرأ كل الأعطال الحالية، وننشئ لكل عطل سببًا واحدًا وحلًا واحدًا
cursor.execute("""
SELECT id, probable_cause, solution, notes FROM faults
""")
existing_faults = cursor.fetchall()

print(f"\n📦 سيتم ترحيل {len(existing_faults)} سجلًا...")

for fault_id, probable_cause, solution, notes in existing_faults:
    # إدخال السبب
    cursor.execute("""
        INSERT INTO causes (fault_id, cause_text) VALUES (?, ?)
    """, (fault_id, probable_cause))
    cause_id = cursor.lastrowid
    
    # إدخال الحل
    cursor.execute("""
        INSERT INTO solutions (cause_id, solution_text) VALUES (?, ?)
    """, (cause_id, solution))
    
    # إدخال الملاحظة إن وجدت
    if notes and notes.strip():
        cursor.execute("""
            INSERT INTO notes (cause_id, note_text) VALUES (?, ?)
        """, (cause_id, notes))

conn.commit()
print("✅ تم ترحيل جميع السجلات إلى الهيكل الجديد")

# ============================================================
# 4. إضافة أمثلة لأعطال متعددة الأسباب والحلول
# ============================================================
# نضيف لعطل "مكثف تنعيم" (id=1) سببًا ثانيًا وحلولًا إضافية
print("\n🎯 إضافة أمثلة متعددة الأسباب والحلول...")

# البحث عن عطل مكثف تنعيم
cursor.execute("""
    SELECT id FROM faults WHERE component = 'مكثف تنعيم' LIMIT 1
""")
row = cursor.fetchone()

if row:
    fault_id = row[0]
    
    # إضافة سبب ثانٍ: "مكثف جاف (فقدان سعة)"
    cursor.execute("""
        INSERT INTO causes (fault_id, cause_text) VALUES (?, ?)
    """, (fault_id, "مكثف جاف (فقدان سعة)"))
    cause2_id = cursor.lastrowid
    
    # إضافة حلين للسبب الثاني
    cursor.execute("""
        INSERT INTO solutions (cause_id, solution_text) VALUES (?, ?)
    """, (cause2_id, "استبدال المكثف بمكثف جديد بنفس السعة"))
    
    cursor.execute("""
        INSERT INTO solutions (cause_id, solution_text) VALUES (?, ?)
    """, (cause2_id, "استبدال بمكثف أعلى جهدًا (للمتانة)"))
    
    # إضافة ملاحظة للسبب الثاني
    cursor.execute("""
        INSERT INTO notes (cause_id, note_text) VALUES (?, ?)
    """, (cause2_id, "قس سعة المكثف بمقياس السعة إن أمكن"))
    
    print(f"   ✅ تمت إضافة سبب ثانٍ وحلين للعطل: مكثف تنعيم")

# البحث عن عطل "فتيل (Fuse)"
cursor.execute("""
    SELECT id FROM faults WHERE component = 'فتيل (Fuse)' LIMIT 1
""")
row = cursor.fetchone()

if row:
    fault_id = row[0]
    
    # إضافة سبب ثانٍ: "قصر في الحمل الخارجي"
    cursor.execute("""
        INSERT INTO causes (fault_id, cause_text) VALUES (?, ?)
    """, (fault_id, "قصر في الحمل الخارجي"))
    cause2_id = cursor.lastrowid
    
    # إضافة حلين للسبب الثاني
    cursor.execute("""
        INSERT INTO solutions (cause_id, solution_text) VALUES (?, ?)
    """, (cause2_id, "افصل الحمل وافحصه بشكل منفصل"))
    
    cursor.execute("""
        INSERT INTO solutions (cause_id, solution_text) VALUES (?, ?)
    """, (cause2_id, "استبدال الفتيل بعد إصلاح الحمل"))
    
    cursor.execute("""
        INSERT INTO notes (cause_id, note_text) VALUES (?, ?)
    """, (cause2_id, "لا تضع فتيلًا بأمبير أعلى أبدًا"))
    
    print(f"   ✅ تمت إضافة سبب ثانٍ وحلين للعطل: فتيل (Fuse)")

conn.commit()

# ============================================================
# 5. إحصائيات نهائية
# ============================================================
print("\n📊 إحصائيات قاعدة البيانات بعد الترحيل:")
cursor.execute("SELECT COUNT(*) FROM faults")
print(f"   • الأعطال: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM causes")
print(f"   • الأسباب: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM solutions")
print(f"   • الحلول: {cursor.fetchone()[0]}")
cursor.execute("SELECT COUNT(*) FROM notes")
print(f"   • الملاحظات: {cursor.fetchone()[0]}")

conn.close()
print("\n🎉 تمت إعادة الهيكلة بنجاح!")
print("   الخطوة التالية: تعديل app.py لعرض الأسباب والحلول المتعددة")