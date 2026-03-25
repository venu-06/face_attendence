import cv2
import os
import numpy as np

def train_model():
    dataset_path = "data/dataset"
    faces = []
    labels = []

    # Loop through each student folder
    for student_id in os.listdir(dataset_path):
        student_folder = os.path.join(dataset_path, student_id)

        if not os.path.isdir(student_folder):
            continue  # skip non-folder files

        for img_name in os.listdir(student_folder):
            img_path = os.path.join(student_folder, img_name)
            gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if gray is None:
                continue  # skip invalid images
            faces.append(gray)
            labels.append(int(student_id))

    if len(faces) == 0:
        print("No faces found. Train skipped.")
        return

    # Create LBPH recognizer and train
    model = cv2.face.LBPHFaceRecognizer_create()
    model.train(faces, np.array(labels))

    # Ensure model folder exists
    os.makedirs("model", exist_ok=True)
    model.save("model/lbph_model.yml")

    print(f"LBPH model trained with {len(faces)} face images from {len(set(labels))} students.")
