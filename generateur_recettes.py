#!/usr/bin/env python3
"""
Générateur IA de Nouvelles Recettes
Crée de nouvelles recettes basées sur les préférences de Michael
"""

import json
import random
from datetime import datetime
import sqlite3

class GenerateurRecettes:
    def __init__(self, db_path='data/assistant.db'):
        self.db_path = db_path
        self.charger_patterns()
        self.cuisines_preferees = ['french', 'italian', 'fusion']
        self.niveau_famille = 'facile_moyen'  # Adapté famille avec enfants
        
    def charger_patterns(self):
        """Charge les patterns de génération"""
        try:
            with open('data/recettes_enrichies.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.patterns = data.get('generateur_patterns', {})
                self.banque_recettes = data.get('banque_recettes', {})
        except:
            # Patterns de base si fichier manquant
            self.patterns = {
                "cuisines": ["french", "italian", "fusion"],
                "types": ["plat_principal", "accompagnement", "plat_complet"],
                "difficultes": ["facile", "moyen"],
                "temps": [15, 20, 25, 30, 35, 40, 45],
                "ingredients_base": {
                    "proteines": ["poulet", "bœuf", "poisson", "œufs"],
                    "feculents": ["riz", "pâtes", "pommes terre"],
                    "legumes": ["courgettes", "brocolis", "carottes", "oignons"],
                    "condiments": ["herbes", "épices", "ail"]
                }
            }
    
    def analyser_preferences(self):
        """Analyse les préférences actuelles depuis la DB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        preferences = {
            'cuisines_aimees': [],
            'temps_prefere': 30,
            'difficulte_preferee': 'moyen',
            'ingredients_favoris': [],
            'types_preferes': []
        }
        
        try:
            # Analyser les recettes souvent choisies
            cursor.execute('''
                SELECT recette_id, choisi FROM preferences_recettes 
                WHERE choisi > refuse ORDER BY choisi DESC LIMIT 5
            ''')
            
            recettes_populaires = cursor.fetchall()
            
            # Analyser les patterns des recettes aimées
            # (Pour l'instant on utilise des valeurs par défaut)
            preferences['cuisines_aimees'] = ['french', 'italian', 'fusion']
            preferences['temps_prefere'] = random.choice([20, 25, 30, 35])
            preferences['difficulte_preferee'] = random.choice(['facile', 'moyen'])
            
        except Exception as e:
            print(f"Erreur analyse preferences: {e}")
        
        conn.close()
        return preferences
    
    def generer_recette_contextuelle(self, contexte=""):
        """Génère une recette selon le contexte actuel"""
        preferences = self.analyser_preferences()
        
        # Analyser le contexte pour adapter la génération
        jour_semaine = datetime.now().weekday()
        is_weekend = jour_semaine >= 5
        
        # Sélection intelligente des paramètres
        if is_weekend:
            temps_max = 60
            difficulte = random.choice(['moyen', 'difficile'])
            types_possibles = ['plat_weekend', 'plat_complet', 'plat_principal']
        else:
            temps_max = 35
            difficulte = random.choice(['facile', 'moyen'])
            types_possibles = ['plat_principal', 'plat_rapide', 'plat_complet']
        
        # Construire la nouvelle recette
        nouvelle_recette = self._construire_recette(
            temps_max=temps_max,
            difficulte=difficulte,
            types_possibles=types_possibles,
            contexte=contexte
        )
        
        return nouvelle_recette
    
    def _construire_recette(self, temps_max, difficulte, types_possibles, contexte=""):
        """Construit une recette complète"""
        
        # Sélection aléatoire guidée
        cuisine = random.choice(self.cuisines_preferees)
        type_recette = random.choice(types_possibles)
        temps_prep = random.choice([t for t in self.patterns["temps"] if t <= temps_max])
        
        # Génération du nom créatif
        noms_base = {
            'french': ['Mijoté de', 'Sauté de', 'Gratin de', 'Poêlée de'],
            'italian': ['Risotto aux', 'Pasta aux', 'Antipasti de', 'Osso bucco de'],
            'fusion': ['Curry de', 'Wok de', 'Bowl de', 'Fusion de']
        }
        
        # Sélection ingrédients
        proteine = random.choice(self.patterns["ingredients_base"]["proteines"])
        feculent = random.choice(self.patterns["ingredients_base"]["feculents"])
        legume1 = random.choice(self.patterns["ingredients_base"]["legumes"])
        legume2 = random.choice([l for l in self.patterns["ingredients_base"]["legumes"] if l != legume1])
        condiment = random.choice(self.patterns["ingredients_base"]["condiments"])
        
        # Construction du nom
        prefix = random.choice(noms_base[cuisine])
        nom = f"{prefix} {proteine} aux {legume1} et {legume2}"
        
        # Calcul du score de base selon la familiarité
        score_familiarite = self._calculer_score_familiarite(proteine, [legume1, legume2])
        
        # Tags intelligents
        tags = self._generer_tags(cuisine, type_recette, difficulte, temps_prep)
        
        recette = {
            'nom': nom,
            'difficulte': difficulte,
            'temps_prep': temps_prep,
            'portions': 4,  # Adapté famille Michael
            'type': type_recette,
            'cuisine': cuisine,
            'ingredients': [proteine, feculent, legume1, legume2, condiment],
            'tags': tags,
            'score_base': score_familiarite,
            'generee_ia': True,
            'date_generation': datetime.now().isoformat(),
            'contexte_generation': contexte
        }
        
        return recette
    
    def _calculer_score_familiarite(self, proteine, legumes):
        """Calcule un score basé sur la familiarité des ingrédients"""
        ingredients_familiers = ['poulet', 'bœuf', 'riz', 'pâtes', 'courgettes', 'carottes', 'oignons']
        
        score = 3  # Score de base
        
        if proteine in ingredients_familiers:
            score += 2
        
        for legume in legumes:
            if legume in ingredients_familiers:
                score += 1
        
        return min(score, 8)  # Max 8 pour éviter de surpasser les favoris
    
    def _generer_tags(self, cuisine, type_recette, difficulte, temps_prep):
        """Génère des tags pertinents"""
        tags = [cuisine]
        
        if temps_prep <= 20:
            tags.append('rapide')
        elif temps_prep >= 45:
            tags.append('mijote')
        
        if difficulte == 'facile':
            tags.append('facile')
        elif difficulte == 'difficile':
            tags.append('festif')
        
        if type_recette in ['plat_weekend', 'plat_complet']:
            tags.append('convivial')
        
        # Tags spéciaux
        if cuisine == 'fusion':
            tags.append('original')
        
        if 'poulet' in tags or 'bœuf' in tags:
            tags.append('proteine')
        
        tags.append('ia_generee')
        
        return tags[:4]  # Limiter à 4 tags
    
    def ajouter_recettes_banque(self, nombre=5):
        """Ajoute des recettes de la banque à la base principale"""
        recettes_ajoutees = []
        
        # Sélectionner des recettes de la banque
        banque_keys = list(self.banque_recettes.keys())
        random.shuffle(banque_keys)
        
        for i in range(min(nombre, len(banque_keys))):
            recette_id = banque_keys[i]
            recette = self.banque_recettes[recette_id].copy()
            
            # Ajuster le score selon les préférences
            recette['score_base'] = self._ajuster_score_banque(recette)
            
            # L'ajouter à la DB
            self._sauvegarder_recette_db(recette_id, recette)
            recettes_ajoutees.append({
                'id': recette_id,
                'nom': recette['nom'],
                'score': recette['score_base']
            })
        
        return recettes_ajoutees
    
    def _ajuster_score_banque(self, recette):
        """Ajuste le score d'une recette de la banque selon les préférences"""
        score = 5  # Score de base
        
        # Bonus selon cuisine
        if recette['cuisine'] in self.cuisines_preferees:
            score += 2
        
        # Bonus temps adapté famille
        if recette['temps_prep'] <= 35:
            score += 1
        
        # Bonus difficulté adaptée
        if recette['difficulte'] in ['facile', 'moyen']:
            score += 1
        
        return score
    
    def _sauvegarder_recette_db(self, recette_id, recette):
        """Sauvegarde une nouvelle recette en DB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO preferences_recettes 
                (recette_id, choisi, frequence_reelle, date_derniere_suggestion)
                VALUES (?, 0, ?, ?)
            ''', (recette_id, recette['score_base'], datetime.now().date()))
            
            conn.commit()
        except Exception as e:
            print(f"Erreur sauvegarde recette {recette_id}: {e}")
        
        conn.close()
    
    def generer_suggestions_enrichies(self, nombre=6):
        """Génère des suggestions enrichies (base + nouvelles + banque)"""
        suggestions = []
        
        # 1. Ajouter quelques recettes de la banque si base faible
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM preferences_recettes WHERE choisi > 0')
        nb_recettes_utilisees = cursor.fetchone()[0]
        conn.close()
        
        if nb_recettes_utilisees < 10:  # Si peu de données
            self.ajouter_recettes_banque(3)
        
        # 2. Générer 1-2 nouvelles recettes IA
        for i in range(2):
            nouvelle_recette = self.generer_recette_contextuelle()
            recette_id = f"ia_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}"
            
            # L'ajouter temporairement pour les suggestions
            suggestions.append({
                'id': recette_id,
                'nom': nouvelle_recette['nom'],
                'temps_prep': nouvelle_recette['temps_prep'],
                'difficulte': nouvelle_recette['difficulte'],
                'portions': nouvelle_recette['portions'],
                'tags': nouvelle_recette['tags'],
                'score_ia': nouvelle_recette['score_base'] + 5,  # Bonus nouveauté
                'nouveau': True
            })
        
        return suggestions

if __name__ == "__main__":
    # Test du générateur
    gen = GenerateurRecettes()
    
    print("🤖 Test Générateur de Recettes IA")
    print("═" * 50)
    
    # Test génération contextuelle
    recette = gen.generer_recette_contextuelle("j'ai envie de quelque chose de nouveau")
    print(f"📝 Nouvelle recette générée:")
    print(f"   Nom: {recette['nom']}")
    print(f"   Difficulté: {recette['difficulte']}")
    print(f"   Temps: {recette['temps_prep']}min")
    print(f"   Tags: {', '.join(recette['tags'])}")
    print(f"   Score: {recette['score_base']}")
    print()
    
    # Test ajout banque
    print("📚 Test ajout recettes banque:")
    ajoutees = gen.ajouter_recettes_banque(3)
    for recette in ajoutees:
        print(f"   + {recette['nom']} (score: {recette['score']})")
    print()
    
    # Test suggestions enrichies
    print("🎯 Test suggestions enrichies:")
    suggestions = gen.generer_suggestions_enrichies(4)
    for suggestion in suggestions:
        nouveau_badge = " 🆕" if suggestion.get('nouveau') else ""
        print(f"   • {suggestion['nom']}{nouveau_badge}")
        print(f"     {suggestion['temps_prep']}min, {suggestion['difficulte']}, score: {suggestion['score_ia']}")
    
    print("\n✅ Générateur IA opérationnel !")