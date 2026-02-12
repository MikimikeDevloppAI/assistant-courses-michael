#!/usr/bin/env python3
"""
Assistant Courses Michael - Application Flask avec IA personnalisée
"""

from flask import Flask, render_template, request, jsonify
import json
import sqlite3
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os

app = Flask(__name__)

# Configuration
DB_PATH = 'data/assistant.db'
RECETTES_PATH = 'data/recettes.json'
PRODUITS_PATH = 'data/produits_coop.json'

class AssistantCourses:
    def __init__(self):
        self.recettes = self.charger_recettes()
        self.produits = self.charger_produits()
        self.init_database()
        
    def charger_recettes(self):
        with open(RECETTES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def charger_produits(self):
        with open(PRODUITS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def init_database(self):
        """Initialise la base de données SQLite pour l'apprentissage"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Table des préférences utilisateur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences_recettes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recette_id TEXT,
                choisi INTEGER DEFAULT 0,
                refuse INTEGER DEFAULT 0,
                date_derniere_suggestion DATE,
                date_derniere_preparation DATE,
                note_utilisateur INTEGER,
                frequence_reelle INTEGER DEFAULT 0
            )
        ''')
        
        # Table des stocks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_maison (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient TEXT UNIQUE,
                quantite REAL,
                unite TEXT,
                date_achat DATE,
                date_peremption DATE,
                niveau_stock TEXT DEFAULT 'moyen'
            )
        ''')
        
        # Table historique des courses
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historique_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_courses DATE,
                recettes_choisies TEXT,
                liste_courses TEXT,
                total_estime REAL,
                commentaires TEXT
            )
        ''')
        
        # Table apprentissage habitudes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS habitudes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT,
                pattern_data TEXT,
                frequence INTEGER DEFAULT 1,
                derniere_occurrence DATE
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Initialiser les préférences pour toutes les recettes
        self.initialiser_preferences()
    
    def initialiser_preferences(self):
        """Initialise les préférences avec les recettes de base de Michael"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for recette_id, recette_data in self.recettes['recettes_recurrentes'].items():
            # Vérifier si déjà en DB
            cursor.execute('SELECT id FROM preferences_recettes WHERE recette_id = ?', (recette_id,))
            if not cursor.fetchone():
                # Initialiser selon la fréquence connue
                frequence_map = {
                    'tres_frequent': 10,
                    'frequent': 7,
                    'occasionnel': 3,
                    'weekend': 2
                }
                freq_init = frequence_map.get(recette_data.get('frequence', 'occasionnel'), 5)
                
                cursor.execute('''
                    INSERT INTO preferences_recettes (recette_id, choisi, frequence_reelle)
                    VALUES (?, ?, ?)
                ''', (recette_id, freq_init, freq_init))
        
        conn.commit()
        conn.close()
    
    def analyser_habitudes_temporelles(self):
        """Analyse les habitudes selon le jour de la semaine, saison, etc."""
        aujourd_hui = datetime.now()
        jour_semaine = aujourd_hui.weekday()  # 0 = Lundi
        
        preferences = {}
        
        # Weekend (vendredi soir, samedi, dimanche)
        if jour_semaine >= 4:
            preferences['type_preferred'] = ['plat_weekend', 'plat_mijote']
            preferences['temps_autorise'] = 180
        else:
            preferences['type_preferred'] = ['plats_rapides']
            preferences['temps_autorise'] = 30
            
        # Gestion enfants (plus de plats adaptés enfants en semaine)
        if jour_semaine < 5:  # Semaine
            preferences['enfants_priorite'] = True
        
        return preferences
    
    def suggerer_recettes(self, nombre=5):
        """Suggère des recettes basées sur les habitudes et l'apprentissage"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Récupérer les préférences actuelles
        cursor.execute('''
            SELECT recette_id, choisi, refuse, date_derniere_preparation, frequence_reelle
            FROM preferences_recettes
        ''')
        preferences_data = cursor.fetchall()
        conn.close()
        
        # Analyser les habitudes temporelles
        habitudes = self.analyser_habitudes_temporelles()
        
        suggestions = []
        recettes_scores = {}
        
        for recette_id, recette_data in self.recettes['recettes_recurrentes'].items():
            score = 0
            
            # Score basé sur les préférences historiques
            pref = next((p for p in preferences_data if p[0] == recette_id), None)
            if pref:
                choisi, refuse, derniere_prep, freq = pref[1], pref[2], pref[3], pref[4]
                score += choisi * 2  # Points pour les choix positifs
                score -= refuse * 3  # Pénalité pour les refus
                
                # Bonus si pas préparée récemment
                if derniere_prep:
                    jours_depuis = (datetime.now() - datetime.strptime(derniere_prep, '%Y-%m-%d')).days
                    score += min(jours_depuis / 7, 3)  # Max 3 points bonus après 3 semaines
                else:
                    score += 2  # Bonus pour nouveauté
            
            # Score basé sur les habitudes temporelles
            if recette_data.get('type') in habitudes.get('type_preferred', []):
                score += 3
            
            if recette_data.get('temps_prep', 30) <= habitudes.get('temps_autorise', 30):
                score += 2
            
            # Bonus pour recettes adaptées enfants en semaine
            if habitudes.get('enfants_priorite') and recette_id in self.recettes['categories'].get('plats_enfants', []):
                score += 2
            
            # Variété : éviter de suggérer toujours les mêmes types
            type_recette = recette_data.get('type', 'autre')
            if len([s for s in suggestions if self.recettes['recettes_recurrentes'][s]['type'] == type_recette]) < 2:
                score += 1
            
            recettes_scores[recette_id] = score
        
        # Sélectionner les meilleures avec un peu d'aléatoire
        recettes_triees = sorted(recettes_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Top candidats avec pondération aléatoire
        top_candidats = recettes_triees[:min(nombre * 2, len(recettes_triees))]
        
        for recette_id, score in top_candidats[:nombre]:
            recette_data = self.recettes['recettes_recurrentes'][recette_id]
            suggestions.append({
                'id': recette_id,
                'nom': recette_data['nom'],
                'temps_prep': recette_data['temps_prep'],
                'difficulte': recette_data['difficulte'],
                'portions': recette_data['portions'],
                'tags': recette_data.get('tags', []),
                'score_ia': round(score, 1)
            })
        
        return suggestions
    
    def verifier_stock(self, ingredients_requis):
        """Vérifie le stock actuel et demande ce qui manque"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT ingredient, quantite, niveau_stock FROM stock_maison')
        stock_actuel = {row[0]: {'quantite': row[1], 'niveau': row[2]} for row in cursor.fetchall()}
        conn.close()
        
        ingredients_a_acheter = []
        ingredients_en_stock = []
        
        for ingredient, details in ingredients_requis.items():
            if ingredient in stock_actuel:
                niveau = stock_actuel[ingredient]['niveau']
                if niveau in ['bas', 'vide']:
                    ingredients_a_acheter.append({
                        'ingredient': ingredient,
                        'quantite': details['quantite'],
                        'rayon': details['rayon'],
                        'obligatoire': details['obligatoire'],
                        'status': 'stock_bas'
                    })
                else:
                    ingredients_en_stock.append(ingredient)
            else:
                ingredients_a_acheter.append({
                    'ingredient': ingredient,
                    'quantite': details['quantite'], 
                    'rayon': details['rayon'],
                    'obligatoire': details['obligatoire'],
                    'status': 'pas_en_stock'
                })
        
        return {
            'a_acheter': ingredients_a_acheter,
            'en_stock': ingredients_en_stock
        }
    
    def generer_liste_courses(self, recettes_choisies):
        """Génère la liste de courses optimisée par rayon Coop"""
        tous_ingredients = {}
        
        # Collecter tous les ingrédients des recettes choisies
        for recette_id in recettes_choisies:
            recette = self.recettes['recettes_recurrentes'].get(recette_id)
            if recette:
                for ingredient, details in recette['ingredients'].items():
                    if ingredient in tous_ingredients:
                        # Combiner les quantités si même ingrédient
                        continue  # Pour l'instant, on garde la première occurrence
                    tous_ingredients[ingredient] = details
        
        # Vérifier le stock
        verification_stock = self.verifier_stock(tous_ingredients)
        
        # Organiser par rayons Coop
        liste_par_rayon = defaultdict(list)
        total_estime = 0
        
        for ingredient in verification_stock['a_acheter']:
            nom_ingredient = ingredient['ingredient']
            rayon = ingredient['rayon']
            
            # Trouver le produit Coop correspondant
            if rayon in self.produits['rayons']:
                produits_rayon = self.produits['rayons'][rayon]['produits']
                if nom_ingredient in produits_rayon:
                    produit = produits_rayon[nom_ingredient]
                    liste_par_rayon[rayon].append({
                        'nom': produit['nom'],
                        'quantite': ingredient['quantite'],
                        'unite': produit['unite'],
                        'prix_estime': produit['prix_moyen'],
                        'obligatoire': ingredient['obligatoire'],
                        'status': ingredient['status']
                    })
                    total_estime += produit['prix_moyen']
        
        # Trier par ordre des rayons Coop
        liste_optimisee = {}
        for rayon in sorted(self.produits['rayons'].keys(), 
                           key=lambda x: self.produits['rayons'][x]['ordre']):
            if rayon in liste_par_rayon:
                liste_optimisee[self.produits['rayons'][rayon]['nom']] = liste_par_rayon[rayon]
        
        return {
            'liste_par_rayon': liste_optimisee,
            'ingredients_en_stock': verification_stock['en_stock'],
            'total_estime': round(total_estime, 2),
            'nombre_articles': sum(len(articles) for articles in liste_optimisee.values())
        }
    
    def enregistrer_choix(self, recette_id, choix_type):
        """Enregistre les choix de l'utilisateur pour l'apprentissage"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        if choix_type == 'choisi':
            cursor.execute('''
                UPDATE preferences_recettes 
                SET choisi = choisi + 1, date_derniere_suggestion = ?
                WHERE recette_id = ?
            ''', (datetime.now().date(), recette_id))
        elif choix_type == 'refuse':
            cursor.execute('''
                UPDATE preferences_recettes 
                SET refuse = refuse + 1, date_derniere_suggestion = ?
                WHERE recette_id = ?
            ''', (datetime.now().date(), recette_id))
        
        conn.commit()
        conn.close()

# Instance globale
assistant = AssistantCourses()

# Routes Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/suggestions')
def get_suggestions():
    nombre = request.args.get('nombre', 5, type=int)
    suggestions = assistant.suggerer_recettes(nombre)
    return jsonify(suggestions)

@app.route('/api/liste-courses', methods=['POST'])
def generer_liste():
    recettes_choisies = request.json.get('recettes', [])
    liste = assistant.generer_liste_courses(recettes_choisies)
    
    # Enregistrer l'historique
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO historique_courses (date_courses, recettes_choisies, liste_courses, total_estime)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now().date(), json.dumps(recettes_choisies), json.dumps(liste), liste['total_estime']))
    conn.commit()
    conn.close()
    
    return jsonify(liste)

@app.route('/api/stock', methods=['GET', 'POST'])
def gerer_stock():
    if request.method == 'GET':
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT ingredient, quantite, unite, niveau_stock FROM stock_maison ORDER BY ingredient')
        stock = [{'ingredient': row[0], 'quantite': row[1], 'unite': row[2], 'niveau': row[3]} 
                for row in cursor.fetchall()]
        conn.close()
        return jsonify(stock)
    
    elif request.method == 'POST':
        updates = request.json.get('updates', [])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for update in updates:
            cursor.execute('''
                INSERT OR REPLACE INTO stock_maison (ingredient, quantite, unite, niveau_stock, date_achat)
                VALUES (?, ?, ?, ?, ?)
            ''', (update['ingredient'], update['quantite'], update['unite'], 
                 update['niveau'], datetime.now().date()))
        
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})

@app.route('/api/choix', methods=['POST'])
def enregistrer_choix():
    recette_id = request.json.get('recette_id')
    choix = request.json.get('choix')  # 'choisi' ou 'refuse'
    
    assistant.enregistrer_choix(recette_id, choix)
    return jsonify({'status': 'success'})

@app.route('/api/historique')
def get_historique():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date_courses, recettes_choisies, total_estime 
        FROM historique_courses 
        ORDER BY date_courses DESC 
        LIMIT 10
    ''')
    historique = []
    for row in cursor.fetchall():
        recettes = json.loads(row[1]) if row[1] else []
        historique.append({
            'date': row[0],
            'recettes': recettes,
            'total': row[2]
        })
    conn.close()
    return jsonify(historique)

if __name__ == '__main__':
    # Créer le dossier data si nécessaire
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)