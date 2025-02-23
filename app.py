from flask import Flask, render_template, request, redirect, send_file, jsonify
import os
from image_processor import ImageStitcher
from werkzeug.utils import secure_filename
import cv2 as cv
import numpy as np
import base64

app = Flask(__name__)

# configuration 
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "static/results"
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

# creer les dossiers s'ils n'existent pas 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# initialiser le processeur d'images
image_stitcher = ImageStitcher()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

def encode_image_to_base64(image):
    """Convert an OpenCV image to base64 string"""
    _, buffer = cv.imencode('.jpg', image)
    return base64.b64encode(buffer).decode('utf-8')

@app.route('/stitch', methods=['POST'])
def stitch():
    if 'images' not in request.files:
        return jsonify({"error": "Aucun fichier n'est uploadé"}), 400
    
    files = request.files.getlist('images')
    if not files:
        return jsonify({"error": "Aucun fichier n'est selectionné"}), 400
    
    # sauvegarde des fichiers uploads
    image_paths = []
    for file in files: 
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_paths.append(filepath)
            
    if not image_paths:
        return jsonify({"error": "Aucune image valide uploadée"}), 400
    
    # Charger les images pour visualisation du processus
    images = [cv.imread(path) for path in image_paths]
    
    # effectuer le stitching avec capture des étapes intermédiaires
    result_img, message, process_images = image_stitcher.stitch_images_with_process(image_paths)
    
    # nettoyer les fichiers uploadés 
    for path in image_paths:
        try: 
            os.remove(path)
        except:
            pass
        
    if result_img is None:
        return jsonify({"error": message}), 400
    
    # sauvegarder l'image resultante 
    output_filename = 'result.jpg'
    output_path = os.path.join(app.config['RESULT_FOLDER'], output_filename)
    cv.imwrite(output_path, result_img)
    
    # Préparer les données pour l'affichage du processus
    process_data = []
    process_steps = [
        "Détection des points clés",
        "Correspondance des points clés",
        "Estimation homographique",
        "Alignement des images",
        "Fusion des images",
        "Post-traitement"
    ]
    
    for i, img in enumerate(process_images):
        if i < len(process_steps):
            step_name = process_steps[i]
        else:
            step_name = f"Étape {i+1}"
        
        base64_img = encode_image_to_base64(img)
        process_data.append({
            "step": step_name,
            "image": base64_img
        })
    
    # Renvoyer le chemin relatif de l'image résultante et les données du processus
    return jsonify({
        "result_path": f"/{app.config['RESULT_FOLDER']}/{output_filename}",
        "process_steps": process_data
    })

if __name__=='__main__':
    app.run(debug=True)