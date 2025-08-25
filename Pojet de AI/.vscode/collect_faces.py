import cv2
import os

# Initialisation du classificateur Haar pour la détection de visage
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Demander le nom de la personne
person_name = input("Entrez le nom de la personne : ").strip()
dataset_path = 'dataset'
person_path = os.path.join(dataset_path, person_name)

# Créer le dossier s'il n'existe pas
os.makedirs(person_path, exist_ok=True)

# Démarrer la webcam
cap = cv2.VideoCapture(0)

print("[INFO] Capture en cours... Appuyez sur 'q' pour quitter.")
count = 0
max_images = 1000

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERREUR] Impossible de lire la webcam.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Détection de visage
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # Extraire le visage
        face = gray[y:y + h, x:x + w]
        face = cv2.resize(face, (200, 200))

        # Enregistrer l'image du visage
        file_path = os.path.join(person_path, f"{count}.jpg")
        cv2.imwrite(file_path, face)
        count += 1

        # Affichage avec rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{count}/{max_images}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow('Collecte de visages', frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or count >= max_images:
        break

cap.release()
cv2.destroyAllWindows()

print(f"[INFO] {count} images enregistrées dans {person_path}")
