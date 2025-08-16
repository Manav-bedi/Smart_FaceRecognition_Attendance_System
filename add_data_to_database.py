from supabase import create_client, Client
import os


SUPABASE_URL = os.getenv("URL")
SUPABASE_KEY = os.getenv("KEY")

if not URL or not KEY:
    raise ValueError("Supabase credentials not found.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Replace with your own data or fetch dynamically
data = {
    "101": {
        "name": "Student One",
        "year": "2nd",
        "section": "B1",
        "course": "B.Tech",
        "total_attendance": 0,
        "last_attendance": "2025-05-19"
    },
    "102": {
        "name": "Student Two",
        "year": "2nd",
        "section": "F1",
        "course": "B.Tech",
        "total_attendance": 0,
        "last_attendance": "2025-05-19"
    },
    "103": {
        "name": "Student Three",
        "year": "2nd",
        "section": "C2",
        "course": "B.Tech",
        "total_attendance": 0,
        "last_attendance": "2025-05-19"
    },
    "104": {
        "name": "Student Four",
        "year": "2nd",
        "section": "A1",
        "course": "B.Tech",
        "total_attendance": 0,
        "last_attendance": "2025-05-19"
    }
}

# ================== Insert Data into Supabase ==================
for student_id, value in data.items():
    record = {
        "student_id": student_id,
        "name": value["name"],
        "year": value["year"],
        "section": value["section"],
        "course": value["course"],
        "total_attendance": value["total_attendance"],
        "last_attendance": value["last_attendance"]
    }

    try:
        res = supabase.table("students").insert(record).execute()
        print(f"Inserted: {student_id} -> {res}")
    except Exception as e:
        print(f"Error inserting {student_id}: {e}")
