import sqlite3
import os

DB_NAME = "faults.db"

if not os.path.exists(DB_NAME):
    print("❌ قاعدة البيانات غير موجودة! شغّل init_database.py أولًا")
    exit()

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# إنشاء جدول الصور
cursor.execute("""
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fault_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    caption TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fault_id) REFERENCES faults(id) ON DELETE CASCADE
)
""")
print("✅ تم إنشاء جدول images بنجاح")

# إنشاء مجلد الرفع
os.makedirs("uploads", exist_ok=True)
print("✅ تم إنشاء مجلد uploads")

conn.commit()
conn.close()
print("\n🎉 جاهز لرفع الصور!")