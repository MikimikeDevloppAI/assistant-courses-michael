#!/usr/bin/env python3
"""
Assistant Courses Michael - Version FINALE
Utilise vraie base de données Marmiton avec calculs par personne
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
DB_PATH = 'data/assistant.db'

class AssistantCoursesMarmiton:
    def __init__(self):
        self.db_path = DB_PATH
    
    def get_toutes_recettes(self):
        """Récupère toutes les recettes de la base Marmiton"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nom, categorie, difficulte, temps_prep, temps_cuisson, 
                   portions, description
            FROM recettes_marmiton
            ORDER BY categorie, nom
        ''')
        
        recettes = []
        for row in cursor.fetchall():
            recettes.append({
                'id': row[0],
                'nom': row[1],
                'categorie': row[2],
                'difficulte': row[3],
                'temps_prep': row[4],
                'temps_cuisson': row[5],
                'portions': row[6],
                'description': row[7],
                'temps_total': row[4] + row[5]
            })
        
        conn.close()
        return recettes
    
    def get_ingredients_recette(self, recette_id, nb_personnes=2.5):
        """Récupère les ingrédients d'une recette calculés pour nb_personnes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupérer la recette et ses portions de base
        cursor.execute('SELECT nom, portions FROM recettes_marmiton WHERE id = ?', (recette_id,))
        recette_info = cursor.fetchone()
        if not recette_info:
            return None, []
        
        nom_recette, portions_base = recette_info
        
        # Calculer le ratio
        ratio = nb_personnes / portions_base
        
        # Récupérer les ingrédients
        cursor.execute('''
            SELECT ingredient_nom, quantite_base, unite, rayon
            FROM ingredients_par_personne 
            WHERE recette_id = ?
        ''', (recette_id,))
        
        ingredients = []
        for row in cursor.fetchall():
            nom, quantite_base, unite, rayon = row
            quantite_calculee = quantite_base * ratio
            
            # Arrondir intelligemment selon l'unité
            if unite == 'pièce' or unite == 'pièces':
                quantite_finale = max(1, round(quantite_calculee))
                quantite_display = f"{int(quantite_finale)} {unite}"
            elif unite in ['gousse', 'gousses', 'feuilles']:
                quantite_finale = max(1, round(quantite_calculee))
                quantite_display = f"{int(quantite_finale)} {unite}"
            elif unite in ['c.s.', 'c.c.']:
                quantite_finale = round(quantite_calculee, 1)
                quantite_display = f"{quantite_finale} {unite}"
            else:
                quantite_finale = round(quantite_calculee)
                quantite_display = f"{int(quantite_finale)}{unite}"
            
            ingredients.append({
                'nom': nom,
                'quantite': quantite_finale,
                'quantite_display': quantite_display,
                'unite': unite,
                'rayon': rayon
            })
        
        conn.close()
        return nom_recette, ingredients
    
    def generer_liste_courses_complete(self, recettes_selectionnees, nb_personnes=2.5, stock_existant=None):
        """Génère une liste de courses complète pour plusieurs recettes"""
        if stock_existant is None:
            stock_existant = {}
        
        # Collecter tous les ingrédients
        tous_ingredients = {}
        recettes_noms = []
        
        for recette_id in recettes_selectionnees:
            nom_recette, ingredients = self.get_ingredients_recette(recette_id, nb_personnes)
            if nom_recette:
                recettes_noms.append(nom_recette)
                
                for ingredient in ingredients:
                    nom = ingredient['nom']
                    if nom in tous_ingredients:
                        # Additionner les quantités
                        tous_ingredients[nom]['quantite'] += ingredient['quantite']
                    else:
                        tous_ingredients[nom] = ingredient.copy()
        
        # Recalculer les quantités display après addition
        for nom, ingredient in tous_ingredients.items():
            unite = ingredient['unite']
            quantite = ingredient['quantite']
            
            if unite in ['pièce', 'pièces', 'gousse', 'gousses', 'feuilles']:
                ingredient['quantite_display'] = f"{int(quantite)} {unite}"
            elif unite in ['c.s.', 'c.c.']:
                ingredient['quantite_display'] = f"{round(quantite, 1)} {unite}"
            else:
                ingredient['quantite_display'] = f"{int(quantite)}{unite}"
        
        # Filtrer selon le stock existant
        liste_finale = {}
        total_articles = 0
        
        for nom, ingredient in tous_ingredients.items():
            if not stock_existant.get(nom, False):  # Si pas en stock
                rayon = ingredient['rayon']
                if rayon not in liste_finale:
                    liste_finale[rayon] = []
                
                liste_finale[rayon].append({
                    'nom': nom,
                    'quantite': ingredient['quantite_display'],
                    'rayon': rayon
                })
                total_articles += 1
        
        # Trier les rayons dans un ordre logique
        ordre_rayons = [
            'Fruits', 'Légumes', 'Viande', 'Poisson', 'Charcuterie',
            'Frais', 'Fromage', 'Pâtes', 'Épicerie', 'Surgelés',
            'Boulangerie', 'Pâtisserie', 'Huiles', 'Épices', 'Herbes',
            'Épicerie Asiatique', 'Épicerie Exotique', 'Conserves', 'Alcools'
        ]
        
        liste_ordonnee = {}
        for rayon in ordre_rayons:
            if rayon in liste_finale:
                liste_ordonnee[rayon] = sorted(liste_finale[rayon], key=lambda x: x['nom'])
        
        # Ajouter rayons restants
        for rayon, articles in liste_finale.items():
            if rayon not in liste_ordonnee:
                liste_ordonnee[rayon] = sorted(articles, key=lambda x: x['nom'])
        
        return {
            'recettes': recettes_noms,
            'nb_personnes': nb_personnes,
            'liste_par_rayon': liste_ordonnee,
            'total_articles': total_articles,
            'stock_utilise': stock_existant
        }

# Instance globale
assistant = AssistantCoursesMarmiton()

# Routes Flask
@app.route('/')
def index():
    return render_template('final.html')

@app.route('/api/recettes')
def get_recettes():
    """API pour récupérer toutes les recettes"""
    recettes = assistant.get_toutes_recettes()
    return jsonify(recettes)

@app.route('/api/ingredients/<int:recette_id>')
def get_ingredients(recette_id):
    """API pour récupérer les ingrédients d'une recette"""
    nb_personnes = request.args.get('personnes', 2.5, type=float)
    nom_recette, ingredients = assistant.get_ingredients_recette(recette_id, nb_personnes)
    
    if nom_recette:
        return jsonify({
            'nom': nom_recette,
            'nb_personnes': nb_personnes,
            'ingredients': ingredients
        })
    else:
        return jsonify({'error': 'Recette non trouvée'}), 404

@app.route('/api/liste-courses-finale', methods=['POST'])
def generer_liste_finale():
    """API pour générer la liste de courses finale"""
    data = request.json
    recettes_ids = data.get('recettes', [])
    nb_personnes = data.get('personnes', 2.5)
    stock_existant = data.get('stock', {})
    
    # Convertir les IDs en entiers
    recettes_ids = [int(id) for id in recettes_ids]
    
    liste = assistant.generer_liste_courses_complete(
        recettes_ids, 
        nb_personnes, 
        stock_existant
    )
    
    return jsonify(liste)

@app.route('/api/export-whatsapp', methods=['POST'])
def export_whatsapp():
    """API pour exporter la liste au format WhatsApp"""
    data = request.json
    liste = data.get('liste', {})
    
    # Formatter pour WhatsApp
    message = "🛒 *LISTE DE COURSES*\n\n"
    
    if 'recettes' in data:
        message += f"📝 *Recettes :* {', '.join(data['recettes'])}\n"
        message += f"👥 *Personnes :* {data.get('nb_personnes', 2.5)}\n\n"
    
    for rayon, articles in liste.items():
        message += f"📦 *{rayon}*\n"
        for article in articles:
            message += f"• {article['nom']} ({article['quantite']})\n"
        message += "\n"
    
    if 'total_articles' in data:
        message += f"📊 *Total :* {data['total_articles']} articles"
    
    return jsonify({
        'message': message,
        'success': True
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)