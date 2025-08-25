# Projet de Reconnaissance Faciale

Ce projet implémente un système de reconnaissance faciale utilisant des réseaux de neurones convolutifs (CNN) avec une interface web pour faciliter son utilisation.

## Documentation

[📄 Lire le rapport directement](https://github.com/USERNAME/REPO/blob/main/rapport_ai_mahrouch.pdf)






## Technologies Utilisées

- Python
- TensorFlow/Keras pour le modèle CNN
- Flask pour l'interface web
- OpenCV pour le traitement d'images
- HTML/CSS/JavaScript pour le frontend

## Structure du Projet

```
application web/
├── app.py                                 # Application Flask principale
├── haarcascade_frontalface_default.xml   # Classificateur Haar Cascade pour la détection de visages
├── label_encoder.pkl                      # Encodeur d'étiquettes entraîné
├── model_faces.h5                         # Modèle CNN entraîné
├── static/                               # Ressources statiques
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── templates/                            # Templates HTML
│   └── index.html
├── test_images/                          # Images de test
└── uploads/                              # Dossier pour les images téléchargées
```

## Installation

1. Clonez le repository :
```bash
git clone https://github.com/mohamedmahrouch/face-recognition.git
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancez l'application :
```bash
python app.py
```

## Fonctionnalités

- Détection de visages en temps réel
- Interface web conviviale pour le téléchargement d'images
- Reconnaissance faciale précise utilisant un modèle CNN
- Visualisation des résultats

## Architecture du Modèle

Le modèle utilise une architecture CNN (Convolutional Neural Network) optimisée pour la reconnaissance faciale. Il a été entraîné sur un dataset diversifié pour assurer une bonne performance de généralisation.

## Résultats

Le modèle a démontré de bonnes performances avec :
- Une précision élevée dans la reconnaissance des visages
- Une robustesse face à différentes conditions d'éclairage
- Une bonne capacité de généralisation

Les résultats détaillés sont disponibles dans le dossier `les résutats/` et incluent :
- Accuracy.png : Courbe d'apprentissage montrant l'évolution de la précision
- Loss.png : Courbe d'apprentissage montrant l'évolution de la perte
- matrice de confusion.png : Matrice de confusion pour l'évaluation du modèle

## Contributeur

- Mohamed Mahrouch

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
