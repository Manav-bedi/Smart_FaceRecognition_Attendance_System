import pickle
import cvzone
import cv2
import os
import time
import face_recognition
import numpy as np
import urllib.request
from supabase import create_client, Client


import os
SUPABASE_URL = os.getenv("url")
SUPABASE_KEY = os.getenv("key")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('Resources/Background.png')

folderModePath = 'Resources/Modes'
modePath = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePath]


with open('EncodeFile.p', 'rb') as file:
    encodeListKnown, studentIds = pickle.load(file)


markedStudents = set()
statusImg = imgModeList[0]
imageCache = {}  

def fetch_image_from_url(url):
    try:
        resp = urllib.request.urlopen(url)
        img_array = np.asarray(bytearray(resp.read()), dtype=np.uint8)
        return cv2.imdecode(img_array, -1)
    except:
        return None

while True:
    success, img = cap.read()
    if not success:
        continue

    imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgRGB = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgRGB)
    encodeCurrFrame = face_recognition.face_encodings(imgRGB, faceCurrFrame)

    imgBackground[162:162+480, 55:55+640] = img

    if faceCurrFrame:
        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                student_id = studentIds[matchIndex]
                print(f"Recognized: {student_id}")

          
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = [v * 4 for v in (y1, x2, y2, x1)]
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                if student_id not in markedStudents:
                    try:
                        
                        res = supabase.table("students").select("*").eq("student_id", student_id).execute()
                        data = res.data[0]

                 
                        new_attendance = (data.get("total_attendance") or 0) + 1
                        supabase.table("students").update({
                            "total_attendance": new_attendance,
                            "last_attendance": time.strftime('%Y-%m-%d')
                        }).eq("student_id", student_id).execute()

                        markedStudents.add(student_id)
                        statusImg = imgModeList[2] 
                        print(f"Attendance marked for {student_id}")

                        image_url = data.get("image_url")
                        if image_url:
                            if student_id not in imageCache:
                                student_img = fetch_image_from_url(image_url)
                                if student_img is not None:
                                    student_img = cv2.resize(student_img, (216, 216))
                                    imageCache[student_id] = student_img
                            if student_id in imageCache:
                                imgBackground[44:260, 550:766] = imageCache[student_id]

                       
                        cv2.putText(imgBackground, f"{data['name']}", (860, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
                        cv2.putText(imgBackground, f"{data['course']} - {data['section']}", (860, 500), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
                        cv2.putText(imgBackground, f"Attendance: {new_attendance}", (860, 540), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    except Exception as e:
                        print("Error updating attendance:", e)
                        statusImg = imgModeList[1]

                else:
                    print(f"{student_id} already marked.")
                    statusImg = imgModeList[3]

        time.sleep(0.3) 
    else:
        statusImg = imgModeList[1]

    imgBackground[44:44+633, 808:808+414] = statusImg
    cv2.imshow('Face Attendance System', imgBackground)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()

