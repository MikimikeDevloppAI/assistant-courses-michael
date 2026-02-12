#!/bin/bash

# Script de démarrage pour l'Assistant Courses Michael
echo "🛒 Démarrage Assistant Courses Michael..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Installer Flask si nécessaire
pip3 install flask --quiet

# Créer les dossiers nécessaires
mkdir -p data templates static/{css,js}

# Vérifier les fichiers essentiels
if [ ! -f "data/recettes.json" ]; then
    echo "❌ Fichier recettes.json manquant"
    exit 1
fi

if [ ! -f "data/produits_coop.json" ]; then
    echo "❌ Fichier produits_coop.json manquant" 
    exit 1
fi

if [ ! -f "app.py" ]; then
    echo "❌ Fichier app.py manquant"
    exit 1
fi

echo "✅ Tous les fichiers sont présents"

# Démarrer l'application
echo "🚀 Lancement de l'Assistant Courses..."
echo "📱 Accès: http://localhost:5000"
echo "⚡ Appuyez sur Ctrl+C pour arrêter"
echo ""

python3 app.py