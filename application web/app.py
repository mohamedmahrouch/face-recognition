# -*- coding: utf-8 -*-

from flask import Flask, render_template, Response, jsonify, request, redirect, url_for
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import pickle
from datetime import datetime
import time
import os
import base64

# --- Constantes ---
IMG_SIZE = 200
PROCESS_EVERY_N_FRAMES = 5
UPLOAD_FOLDER = 'uploads' # Dossier pour stocker temporairement les images uploadées
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True) # Créer le dossier s'il n'existe pas

# --- Chargement des modèles et de l'encodeur ---
try:
    model = load_model("model_faces.h5")
    with open("label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except Exception as e:
    print(f"[ERREUR] Impossible de charger les fichiers : {e}")
    exit()

# --- Stockage global ---
camera = cv2.VideoCapture(0)
recognition_history = []

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_face(face_img):
    """Prétraite l'image d'un visage recadré pour la prédiction."""
    face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    face_resized = cv2.resize(face_gray, (IMG_SIZE, IMG_SIZE))
    face_normalized = face_resized / 255.0
    face_reshaped = np.reshape(face_normalized, (1, IMG_SIZE, IMG_SIZE, 1))
    return face_reshaped

def process_and_predict(image_np):
    """
    Détecte les visages, prédit leur identité et dessine les résultats sur l'image.
    Retourne l'image annotée et une liste des prédictions.
    """
    gray_frame = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5, minSize=(50, 50))
    
    predictions = []

    for (x, y, w, h) in faces:
        face_roi = image_np[y:y+h, x:x+w]
        processed_face = preprocess_face(face_roi)

        prediction = model.predict(processed_face, verbose=0)[0]
        confidence = float(np.max(prediction))
        class_index = np.argmax(prediction)
        name = label_encoder.inverse_transform([class_index])[0]

        predictions.append({'name': name, 'confidence': round(confidence * 100, 2)})

        label = f"{name} ({confidence*100:.1f}%)"
        color = (0, 255, 0) if confidence > 0.75 else (0, 255, 255)
        
        cv2.rectangle(image_np, (x, y), (x+w, y+h), color, 2)
        cv2.putText(image_np, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return image_np, predictions

def gen_frames():
    """Générateur de frames vidéo pour le streaming."""
    frame_count = 0
    last_faces_info = []

    while True:
        success, frame = camera.read()
        if not success:
            time.sleep(0.1)
            continue

        frame_count += 1
        
        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            # Réinitialiser la liste pour stocker les nouvelles détections
            current_faces_info = []
            
            # Détecter et prédire sur la frame actuelle
            annotated_frame, predictions = process_and_predict(frame.copy()) # Utiliser une copie
            
            # Mettre à jour les informations des visages
            for pred in predictions:
                # Logique d'historique
                is_new = True
                if recognition_history and recognition_history[-1]['name'] == pred['name']:
                    is_new = False
                
                if is_new and pred['confidence'] > 75:
                    recognition_history.append({
                        "name": pred['name'],
                        "confidence": pred['confidence'],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            
        


        annotated_frame, _ = process_and_predict(frame.copy())
        
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Page d'accueil."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Route pour le flux vidéo."""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
# Route pour récupérer la liste des images de test
@app.route('/test-images')
def get_test_images():
    test_images = []
    test_folder = os.path.join('static', 'images')
    fichiers = os.listdir(test_folder)

    # Afficher chaque fichier
    for fichier in fichiers:
        print(fichier)
    
    if os.path.exists(test_folder):
        for filename in os.listdir(test_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                test_images.append({
                    'name': filename,
                    'path': os.path.join(test_folder, filename),
                    'url': url_for('static', filename=f'test_images/{filename}')
                })
    
    return jsonify(test_images)

# Route pour analyser une image de test
@app.route('/analyze-test-image', methods=['POST'])
def analyze_test_image():
    """Analyse une image de test spécifique."""
    data = request.get_json()
    image_name = data.get('image_name')
    
    if not image_name or '..' in image_name or '/' in image_name:
        return jsonify({'error': 'Nom d\'image invalide'}), 400
    
    image_path = os.path.join('static', 'test_images', image_name)
    
    if not os.path.exists(image_path):
        return jsonify({'error': 'Image non trouvée'}), 404
    
    try:
        image = cv2.imread(image_path)
        if image is None:
            return jsonify({'error': 'Impossible de lire l\'image'}), 400
            
        annotated_image, predictions = process_and_predict(image)
        
        _, buffer = cv2.imencode('.jpg', annotated_image)
        img_str = base64.b64encode(buffer).decode('utf-8')
        image_data = f'data:image/jpeg;base64,{img_str}'
        
        return jsonify({
            'success': True,
            'predictions': predictions,
            'image_data': image_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/history')
def history():
    """API pour récupérer l'historique."""
    return jsonify(list(reversed(recognition_history[-10:])))

@app.route('/upload', methods=['POST'])
def upload_image():
    """Gère l'upload d'une image pour la reconnaissance."""
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if file and allowed_file(file.filename):
        # Lire l'image depuis le flux en mémoire
        filestr = file.read()
        npimg = np.frombuffer(filestr, np.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        # Traiter l'image
        annotated_image, predictions = process_and_predict(image)

        # Encoder l'image annotée en base64 pour l'afficher dans le HTML
        _, buffer = cv2.imencode('.jpg', annotated_image)
        img_str = base64.b64encode(buffer).decode('utf-8')
        img_src = f'data:image/jpeg;base64,{img_str}'

        return jsonify({
            'success': True,
            'image_data': img_src,
            'predictions': predictions
        })
    else:
        return jsonify({'error': 'Type de fichier non autorisé'}), 400

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, threaded=True)