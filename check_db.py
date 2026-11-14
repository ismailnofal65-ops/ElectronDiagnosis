import sqlite3
import os

print("📁 المسار الحالي:", os.getcwd())
print("📁 مسار قاعدة البيانات:", os.path.abspath("faults.db"))
print()

conn = sqlite3.connect("faults.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM faults")
print("✅ عدد السجلات:", cursor.fetchone()[0])

print("\n📊 التوزيع:")
cursor.execute("SELECT circuit_type, COUNT(*) FROM faults GROUP BY circuit_type")
for row in cursor.fetchall():
    print("   ", row)

print("\n🔍 أول 3 سجلات:")
cursor.execute("SELECT id, circuit_type, component, symptom FROM faults LIMIT 3")
for row in cursor.fetchall():
    print("   ", row)

conn.close()