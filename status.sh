#!/bin/bash

echo "========================================================================"
echo "🛒 ASSISTANT COURSES MICHAEL - STATUS"
echo "========================================================================"
echo "Date: $(date '+%d/%m/%Y %H:%M:%S')"
echo "Répertoire: $(pwd)"
echo "========================================================================"
echo

# Vérification des composants
echo "🔍 VÉRIFICATION COMPOSANTS"
echo "────────────────────────────────────────────────────────────────────────"

# Flask App
if pgrep -f "python3 app.py" > /dev/null; then
    echo "✅ Assistant Courses   : ACTIF (http://localhost:5000)"
    PORT_STATUS="ACTIF"
else
    echo "❌ Assistant Courses   : ARRÊTÉ"
    PORT_STATUS="ARRÊTÉ"
fi

# Fichiers essentiels
if [ -f "app.py" ]; then
    APP_SIZE=$(stat -c%s app.py)
    echo "✅ Application Flask   : PRÉSENT (${APP_SIZE}B)"
else
    echo "❌ Application Flask   : MANQUANT"
fi

if [ -f "data/recettes.json" ]; then
    echo "✅ Base Recettes      : PRÉSENT ($(jq '.recettes_recurrentes | length' data/recettes.json) recettes)"
else
    echo "❌ Base Recettes      : MANQUANT"
fi

if [ -f "data/produits_coop.json" ]; then
    RAYONS_COUNT=$(jq '.rayons | length' data/produits_coop.json)
    echo "✅ Catalogue Coop     : PRÉSENT (${RAYONS_COUNT} rayons)"
else
    echo "❌ Catalogue Coop     : MANQUANT"
fi

if [ -f "templates/index.html" ]; then
    echo "✅ Interface Web      : PRÉSENT ($(stat -c%s templates/index.html)B)"
else
    echo "❌ Interface Web      : MANQUANT"
fi

if [ -f "data/assistant.db" ]; then
    echo "✅ Base IA Apprentissage: PRÉSENT"
else
    echo "⚠️  Base IA Apprentissage: SERA CRÉÉE AU 1ER LANCEMENT"
fi

echo

# Test API si l'app tourne
if [ "$PORT_STATUS" = "ACTIF" ]; then
    echo "🧪 TESTS API"
    echo "────────────────────────────────────────────────────────────────────────"
    
    # Test suggestions
    SUGGESTIONS=$(curl -s http://localhost:5000/api/suggestions | jq -r 'length' 2>/dev/null)
    if [ "$SUGGESTIONS" != "" ] && [ "$SUGGESTIONS" != "null" ]; then
        echo "✅ API Suggestions    : OK (${SUGGESTIONS} recettes)"
    else
        echo "❌ API Suggestions    : ERREUR"
    fi
    
    # Test status HTTP
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ Interface Web      : OK (HTTP 200)"
    else
        echo "❌ Interface Web      : ERREUR (HTTP $HTTP_CODE)"
    fi
fi

echo

# Profil utilisateur intégré
echo "👨‍👩‍👧‍👦 PROFIL FAMILLE MICHAEL"
echo "────────────────────────────────────────────────────────────────────────"
echo "Famille              : 2 adultes + 2 enfants (10 mois + 2,5 ans)"
echo "Magasin              : Coop (livraison 1x/semaine)"
echo "Style cuisine        : Varié, jour le jour, pas trop long"
echo "Recettes récurrentes : 7 plats intégrés + apprentissage IA"
echo "Budget               : Flexible, optimisé par l'IA"
echo

# Fonctionnalités
echo "🤖 FONCTIONNALITÉS IA"
echo "────────────────────────────────────────────────────────────────────────"
echo "Suggestions personnalisées : Basées sur historique + contexte temporel"
echo "Apprentissage continu      : Mémorise choix/refus pour améliorer"
echo "Gestion stock intelligent  : Évite achats inutiles"
echo "Liste Coop optimisée       : Organisée par rayons du magasin"
echo "Adaptation famille         : Portions et plats adaptés enfants"
echo

# Actions rapides
echo "⚡ ACTIONS RAPIDES"
echo "────────────────────────────────────────────────────────────────────────"
if [ "$PORT_STATUS" = "ACTIF" ]; then
    echo "Interface           : http://localhost:5000"
    echo "Arrêter             : Ctrl+C ou kill $(pgrep -f 'python3 app.py')"
else
    echo "Démarrer            : ./start.sh"
    echo "Manuel              : python3 app.py"
fi
echo "Documentation       : cat GUIDE_UTILISATION.md"
echo "Reset IA            : rm data/assistant.db"
echo

# Status final
if [ "$PORT_STATUS" = "ACTIF" ] && [ -f "data/recettes.json" ] && [ -f "templates/index.html" ]; then
    echo "🎉 ASSISTANT PRÊT : Toutes les fonctionnalités sont opérationnelles !"
    echo "🛒 Accède à http://localhost:5000 pour commencer tes courses intelligentes"
else
    echo "⚠️  SETUP PARTIEL : Certains composants nécessitent attention"
fi

echo
echo "========================================================================"
echo "✨ Assistant Courses Michael - IA personnalisée pour optimiser tes repas"
echo "========================================================================"