# Panorama App

## Description
Panorama App est une application qui permet de générer des panoramas à partir de plusieurs images en utilisant des techniques de traitement d'images et de vision par ordinateur. L'application aligne et fusionne automatiquement les images pour produire un panorama cohérent.

## Fonctionnalités
- Chargement et prétraitement des images
- Détection et appariement des points caractéristiques
- Alignement des images
- Fusion et correction des couleurs
- Exportation du panorama généré

## Technologies utilisées
- Python
- OpenCV
- NumPy
- Matplotlib

## Installation
### Prérequis
- Python 3.8+
- pip

### Étapes d'installation
1. Cloner le dépôt :
   ```bash
   git clone https://github.com/sarrmouhamed29/panorama_app.git
   cd panorama_app
   ```
2. Créer un environnement virtuel et l'activer :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur macOS/Linux
   venv\Scripts\activate  # Sur Windows
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation
1. Lancer l'application :
   ```bash
   python app.py
   ```
2. Sélectionner les images à fusionner.
3. Obtenir et enregistrer le panorama généré.

## Contribuer
Les contributions sont les bienvenues !
1. Forker le dépôt
2. Créer une branche avec vos modifications :
   ```bash
   git checkout -b ma-nouvelle-fonctionnalite
   ```
3. Committer vos modifications :
   ```bash
   git commit -m "Ajout d'une nouvelle fonctionnalité"
   ```
4. Pousser vers votre fork et créer une Pull Request.

## Licence
Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus d’informations.

