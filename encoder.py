import cv2
import os
import face_recognition
import pickle
from supabase import create_client, Client


import os
SUPABASE_URL = os.getenv("URL")
SUPABASE_KEY = os.getenv("KEY")

if not URL or not KEY:
    raise ValueError("Supabase credentials not found.")

supabase: Client = create_client(URL, KEY)


folderPath = 'Images'
imgList = []
studentIds = []


studentInfo = {
    '101': {'name': 'Student One', 'course': 'B.Tech CSE', 'section': 'A'},
    '102': {'name': 'Student Two', 'course': 'BCA', 'section': 'B'},
    
}


pathList = os.listdir(folderPath)
print(f"Found image files: {pathList}")

for path in pathList:
    img = cv2.imread(os.path.join(folderPath, path))
    student_id = os.path.splitext(path)[0]

    if img is None:
        print(f"Skipping unreadable file: {path}")
        continue

    imgList.append(img)
    studentIds.append(student_id)


    image_path = os.path.join(folderPath, path)
    try:
        with open(image_path, "rb") as f:
            supabase.storage.from_("student").upload(
                f"photos/{path}", f,
                {"content-type": "image/png", "x-upsert": "true"}
            )
        print(f"Uploaded {path} to Supabase Storage")
    except Exception as e:
        print(f"Error uploading {path}: {e}")

  
    metadata = studentInfo.get(student_id, {"name": "Unknown", "course": "NA", "section": "NA"})
    student_payload = {
        "student_id": student_id,
        "name": metadata['name'],
        "course": metadata['course'],
        "section": metadata['section'],
        "total_attendance": 0,
        "image_url": f"{SUPABASE_URL}/storage/v1/object/public/student/photos/{path}"
    }
    try:
        supabase.table("students").upsert(student_payload).execute()
        print(f"Metadata added for {student_id}")
    except Exception as e:
        print(f"Error inserting metadata for {student_id}: {e}")


def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_img)
        if encodings: 
            encodeList.append(encodings[0])
        else:
            print("Warning: No face detected in one of the images.")
    return encodeList

print("Encoding all faces...")
encodeListKnown = findEncodings(imgList)


with open('EncodeFile.p', 'wb') as file:
    pickle.dump((encodeListKnown, studentIds), file)

print("Face encodings saved to 'EncodeFile.p'")
