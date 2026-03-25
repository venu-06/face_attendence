import cv2
import os

def capture_faces(student_id, num_samples=20):
    dataset_path = os.path.join("data", "dataset", str(student_id))
    os.makedirs(dataset_path, exist_ok=True)

    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    if face_cascade.empty():
        raise Exception("Failed to load Haar cascade XML file!")

    cam = cv2.VideoCapture(0)
    count = 0

    while count < num_samples:
        ret, frame = cam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            count += 1
            face_img = gray[y:y+h, x:x+w]
            cv2.imwrite(f"{dataset_path}/user_{count}.jpg", face_img)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)

        cv2.imshow("Capture Faces", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if count >= num_samples:
            break

    cam.release()
    cv2.destroyAllWindows()
