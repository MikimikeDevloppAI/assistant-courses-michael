#!/usr/bin/env python3
"""
Assistant Courses Michael - Application Flask avec IA personnalisée
Version enrichie avec génération IA de nouvelles recettes
"""

from flask import Flask, render_template, request, jsonify
import json
import sqlite3
import random
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import os
from generateur_recettes import GenerateurRecettes

app = Flask(__name__)

# Configuration
DB_PATH = 'data/assistant.db'
RECETTES_PATH = 'data/recettes.json'
PRODUITS_PATH = 'data/produits_coop.json'

class AssistantCourses:
    def __init__(self):
        self.recettes = self.charger_recettes()
        self.produits = self.charger_produits()
        self.charger_base_enrichie()  # Charger avant init DB
        self.generateur = GenerateurRecettes(DB_PATH)
        self.init_database()
        
    def charger_recettes(self):
        with open(RECETTES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def charger_produits(self):
        with open(PRODUITS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def charger_base_enrichie(self):
        """Charge la base de recettes enrichie"""
        try:
            with open('data/recettes_enrichies.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.recettes_enrichies = data
                # Fusionner avec les recettes de base
                all_recettes = {}
                all_recettes.update(data.get('recettes_base', {}))
                all_recettes.update(data.get('banque_recettes', {}))
                self.toutes_recettes = all_recettes
        except FileNotFoundError:
            print("⚠️ Fichier recettes enrichies non trouvé, utilisation base standard")
            self.recettes_enrichies = {}
            self.toutes_recettes = self.recettes.get('recettes_recurrentes', {})
            
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
        """Initialise les préférences avec toutes les recettes disponibles"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Recettes de base (favoris Michael)
        for recette_id, recette_data in self.recettes.get('recettes_recurrentes', {}).items():
            cursor.execute('SELECT id FROM preferences_recettes WHERE recette_id = ?', (recette_id,))
            if not cursor.fetchone():
                # Score élevé pour les favoris
                frequence_map = {
                    'tres_frequent': 10,
                    'frequent': 8,
                    'occasionnel': 6,
                    'weekend': 5
                }
                freq_init = frequence_map.get(recette_data.get('frequence', 'frequent'), 7)
                
                cursor.execute('''
                    INSERT INTO preferences_recettes (recette_id, choisi, frequence_reelle)
                    VALUES (?, ?, ?)
                ''', (recette_id, freq_init, freq_init))
        
        # 2. Recettes enrichies (base + banque)
        for recette_id, recette_data in self.toutes_recettes.items():
            cursor.execute('SELECT id FROM preferences_recettes WHERE recette_id = ?', (recette_id,))
            if not cursor.fetchone():
                # Score selon la pertinence estimée
                score_base = recette_data.get('score_base', 5)
                
                cursor.execute('''
                    INSERT INTO preferences_recettes (recette_id, choisi, frequence_reelle)
                    VALUES (?, 0, ?)
                ''', (recette_id, score_base))
        
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
    
    def suggerer_recettes(self, nombre=6, forcer_nouvelles=False):
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
        
        # 1. SCORING DES RECETTES EXISTANTES (BASE + BANQUE)
        for recette_id, recette_data in self.toutes_recettes.items():
            score = recette_data.get('score_base', 5)  # Score de base
            
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
            else:
                score += 1  # Petit bonus pour recettes jamais essayées
            
            # Score basé sur les habitudes temporelles
            if recette_data.get('type') in habitudes.get('type_preferred', []):
                score += 3
            
            if recette_data.get('temps_prep', 30) <= habitudes.get('temps_autorise', 30):
                score += 2
            
            # Bonus cuisine préférée
            if recette_data.get('cuisine') in ['french', 'italian', 'fusion']:
                score += 1
            
            # Bonus pour recettes adaptées famille
            if recette_data.get('difficulte') in ['facile', 'moyen']:
                score += 1
            
            recettes_scores[recette_id] = score
        
        # 2. AJOUTER RECETTES GÉNÉRÉES IA SI DEMANDÉ
        if forcer_nouvelles or len(recettes_scores) < nombre:
            nouvelles_recettes = self.generateur.generer_suggestions_enrichies(2)
            for nouvelle in nouvelles_recettes:
                if nouvelle.get('nouveau'):  # Recette générée IA
                    recettes_scores[nouvelle['id']] = nouvelle['score_ia']
        
        # 3. SÉLECTION FINALE INTELLIGENTE
        if not recettes_scores:
            # Fallback si aucune recette
            return self._suggestions_fallback()
        
        # Trier par score
        recettes_triees = sorted(recettes_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Sélection avec variété
        suggestions_finales = []
        types_utilises = []
        cuisines_utilisees = []
        
        for recette_id, score in recettes_triees:
            if len(suggestions_finales) >= nombre:
                break
                
            # Récupérer les données de la recette
            recette_data = self.toutes_recettes.get(recette_id)
            if not recette_data:
                continue
            
            # Assurer la variété des types et cuisines
            type_recette = recette_data.get('type', 'autre')
            cuisine = recette_data.get('cuisine', 'autre')
            
            # Limiter répétition du même type (max 2)
            if types_utilises.count(type_recette) >= 2:
                continue
            
            # Limiter répétition de la même cuisine (max 3)
            if cuisines_utilisees.count(cuisine) >= 3:
                continue
            
            suggestions_finales.append({
                'id': recette_id,
                'nom': recette_data['nom'],
                'temps_prep': recette_data['temps_prep'],
                'difficulte': recette_data['difficulte'],
                'portions': recette_data['portions'],
                'tags': recette_data.get('tags', []),
                'score_ia': round(score, 1),
                'nouveau': recette_data.get('generee_ia', False)
            })
            
            types_utilises.append(type_recette)
            cuisines_utilisees.append(cuisine)
        
        # Si pas assez de suggestions, compléter avec le reste
        if len(suggestions_finales) < nombre:
            for recette_id, score in recettes_triees:
                if len(suggestions_finales) >= nombre:
                    break
                if recette_id in [s['id'] for s in suggestions_finales]:
                    continue
                    
                recette_data = self.toutes_recettes.get(recette_id)
                if recette_data:
                    suggestions_finales.append({
                        'id': recette_id,
                        'nom': recette_data['nom'],
                        'temps_prep': recette_data['temps_prep'],
                        'difficulte': recette_data['difficulte'],
                        'portions': recette_data['portions'],
                        'tags': recette_data.get('tags', []),
                        'score_ia': round(score, 1)
                    })
        
        return suggestions_finales
    
    def _suggestions_fallback(self):
        """Suggestions de secours si base vide"""
        return [{
            'id': 'fallback_1',
            'nom': 'Pâtes à la Sauce Tomate',
            'temps_prep': 20,
            'difficulte': 'facile',
            'portions': 4,
            'tags': ['italien', 'rapide', 'facile'],
            'score_ia': 8.0
        }]
    
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
    # Redirection vers la version finale
    from flask import redirect
    return redirect('http://69.62.121.46:5001/')

@app.route('/simple')
def simple():
    return render_template('simple.html')

@app.route('/advanced')
def advanced():
    return render_template('index.html')

@app.route('/backup')
def backup():
    return render_template('backup_statique.html')

@app.route('/test')
def test():
    return render_template('ultra_simple.html')

@app.route('/api/suggestions')
def get_suggestions():
    nombre = request.args.get('nombre', 6, type=int)
    nouvelles = request.args.get('nouvelles', False, type=bool)
    suggestions = assistant.suggerer_recettes(nombre, forcer_nouvelles=nouvelles)
    return jsonify(suggestions)

@app.route('/api/nouvelles-recettes')
def get_nouvelles_recettes():
    """Génère de nouvelles recettes IA"""
    nombre = request.args.get('nombre', 3, type=int)
    contexte = request.args.get('contexte', '')
    
    nouvelles = []
    for i in range(nombre):
        recette = assistant.generateur.generer_recette_contextuelle(contexte)
        recette_id = f"ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
        
        nouvelles.append({
            'id': recette_id,
            'nom': recette['nom'],
            'temps_prep': recette['temps_prep'],
            'difficulte': recette['difficulte'],
            'portions': recette['portions'],
            'tags': recette['tags'],
            'score_ia': recette['score_base'],
            'nouveau': True,
            'contexte': recette.get('contexte_generation', '')
        })
    
    return jsonify(nouvelles)

@app.route('/api/enrichir-base')
def enrichir_base():
    """Enrichit la base avec des recettes de la banque"""
    nombre = request.args.get('nombre', 5, type=int)
    ajoutees = assistant.generateur.ajouter_recettes_banque(nombre)
    return jsonify({
        'status': 'success',
        'recettes_ajoutees': ajoutees,
        'message': f'{len(ajoutees)} nouvelles recettes ajoutées à ta base !'
    })

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

@app.route('/api/simple-courses', methods=['POST'])
def generer_courses_simples():
    """API simplifiée pour l'interface simple"""
    data = request.json
    recettes_ids = data.get('recettes', [])
    nb_personnes = data.get('personnes', 2.5)
    stock_utilisateur = data.get('stock', {})
    
    # Mapping recettes simples vers ingrédients
    ingredients_par_recette = {
        'riz_saute': {
            'Riz long grain': {'quantite': '200g', 'rayon': 'Épicerie'},
            'Légumes surgelés': {'quantite': '300g', 'rayon': 'Surgelés'},
            'Œufs': {'quantite': '4 pièces', 'rayon': 'Produits Frais'},
            'Sauce soja': {'quantite': '1 bouteille', 'rayon': 'Épicerie Asiatique'}
        },
        'pates_carbo': {
            'Pâtes (spaghetti)': {'quantite': '400g', 'rayon': 'Épicerie'},
            'Lardons': {'quantite': '150g', 'rayon': 'Charcuterie'},
            'Crème fraîche': {'quantite': '200ml', 'rayon': 'Produits Frais'},
            'Parmesan râpé': {'quantite': '100g', 'rayon': 'Fromages'}
        },
        'poulet_grille': {
            'Filets de poulet': {'quantite': f'{int(150 * nb_personnes)}g', 'rayon': 'Viande & Poissons'},
            'Courgettes': {'quantite': '2 pièces', 'rayon': 'Fruits & Légumes'},
            'Tomates': {'quantite': '500g', 'rayon': 'Fruits & Légumes'},
            'Herbes de Provence': {'quantite': '1 sachet', 'rayon': 'Épices'}
        },
        'salade_cesar': {
            'Salade romaine': {'quantite': '1 pièce', 'rayon': 'Fruits & Légumes'},
            'Filets de poulet': {'quantite': '300g', 'rayon': 'Viande & Poissons'},
            'Croûtons': {'quantite': '1 sachet', 'rayon': 'Épicerie'},
            'Sauce César': {'quantite': '1 bouteille', 'rayon': 'Épicerie'}
        },
        'omelette': {
            'Œufs': {'quantite': f'{int(3 * nb_personnes)} pièces', 'rayon': 'Produits Frais'},
            'Herbes fraîches': {'quantite': '1 bouquet', 'rayon': 'Fruits & Légumes'},
            'Beurre': {'quantite': '250g', 'rayon': 'Produits Frais'}
        },
        'spaghetti_bolo': {
            'Pâtes (spaghetti)': {'quantite': '500g', 'rayon': 'Épicerie'},
            'Viande hachée': {'quantite': '400g', 'rayon': 'Viande & Poissons'},
            'Tomates concassées': {'quantite': '2 boîtes', 'rayon': 'Conserves'},
            'Oignons': {'quantite': '2 pièces', 'rayon': 'Fruits & Légumes'},
            'Carottes': {'quantite': '2 pièces', 'rayon': 'Fruits & Légumes'}
        },
        'curry_poulet': {
            'Filets de poulet': {'quantite': '500g', 'rayon': 'Viande & Poissons'},
            'Lait de coco': {'quantite': '1 boîte', 'rayon': 'Épicerie Exotique'},
            'Pâte de curry': {'quantite': '1 pot', 'rayon': 'Épices'},
            'Riz basmati': {'quantite': '300g', 'rayon': 'Épicerie'}
        },
        'ratatouille': {
            'Aubergines': {'quantite': '2 pièces', 'rayon': 'Fruits & Légumes'},
            'Courgettes': {'quantite': '3 pièces', 'rayon': 'Fruits & Légumes'},
            'Tomates': {'quantite': '1kg', 'rayon': 'Fruits & Légumes'},
            'Poivrons': {'quantite': '2 pièces', 'rayon': 'Fruits & Légumes'}
        }
    }
    
    # Collecter tous les ingrédients
    tous_ingredients = {}
    for recette_id in recettes_ids:
        if recette_id in ingredients_par_recette:
            for ingredient, details in ingredients_par_recette[recette_id].items():
                if ingredient not in tous_ingredients:
                    tous_ingredients[ingredient] = details
    
    # Filtrer selon le stock déclaré
    courses_par_rayon = {}
    total_prix = 0
    
    # Prix estimés Coop
    prix_produits = {
        'Riz long grain': 2.95, 'Légumes surgelés': 3.50, 'Œufs': 4.20,
        'Sauce soja': 3.50, 'Pâtes (spaghetti)': 1.95, 'Lardons': 3.50,
        'Crème fraîche': 2.40, 'Parmesan râpé': 4.95, 'Filets de poulet': 24.90,
        'Courgettes': 2.80, 'Tomates': 3.50, 'Herbes de Provence': 2.80,
        'Salade romaine': 2.20, 'Croûtons': 2.50, 'Sauce César': 3.80,
        'Herbes fraîches': 2.50, 'Beurre': 3.80, 'Viande hachée': 8.95,
        'Tomates concassées': 1.20, 'Oignons': 2.20, 'Carottes': 2.80,
        'Lait de coco': 2.95, 'Pâte de curry': 3.50, 'Riz basmati': 3.50,
        'Aubergines': 4.50, 'Poivrons': 6.90
    }
    
    for ingredient, details in tous_ingredients.items():
        # Vérifier si en stock
        if stock_utilisateur.get(ingredient, False):
            continue  # Skip si en stock
            
        rayon = details['rayon']
        if rayon not in courses_par_rayon:
            courses_par_rayon[rayon] = []
            
        prix = prix_produits.get(ingredient, 3.00)  # Prix par défaut
        total_prix += prix
        
        courses_par_rayon[rayon].append({
            'nom': ingredient,
            'quantite': details['quantite'],
            'prix': prix
        })
    
    return jsonify({
        'courses_par_rayon': courses_par_rayon,
        'total_estime': round(total_prix, 2),
        'nb_articles': sum(len(items) for items in courses_par_rayon.values()),
        'recettes': recettes_ids,
        'personnes': nb_personnes
    })

if __name__ == '__main__':
    # Créer le dossier data si nécessaire
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)