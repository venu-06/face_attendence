import cv2
from datetime import datetime
from utils.db import get_db
from config import MODEL_PATH

def mark_attendance(student_id):
    # Ensure student_id is an integer
    student_id = int(student_id)

    # Load the trained face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_PATH)

    # Initialize the camera
    cam = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Capture one frame from the camera
    ret, frame = cam.read()
    cam.release()

    if not ret:
        print("Failed to capture image from camera")
        return False

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_detector.detectMultiScale(gray, 1.3, 5)

    # Loop through detected faces
    for (x, y, w, h) in faces:
        id_, confidence = recognizer.predict(gray[y:y+h, x:x+w])

        # If recognized and confidence is acceptable
        if id_ == student_id and confidence < 70:
            db = get_db()
            cur = db.cursor()
            now = datetime.now()

            # Insert attendance record with date as string
            cur.execute(
    "INSERT INTO attendance VALUES (NULL, ?, ?, ?, ?)",
    (
        student_id,               # must be int
        now.strftime("%Y-%m-%d"), # date as string
        now.strftime("%H:%M:%S"), # time as string
        "Present"
    )
)

            db.commit()
            db.close()
            return True

    # If no face matched
    return False
