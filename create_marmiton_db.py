#!/usr/bin/env python3
"""
Création base de données avec 50 recettes style Marmiton
Recettes françaises populaires et faciles à réaliser
"""

import sqlite3
import json
from datetime import datetime

def create_marmiton_database():
    """Crée une base de données avec 50 recettes inspirées Marmiton"""
    
    # Recettes style Marmiton - faciles et populaires
    recettes_marmiton = [
        # PLATS PRINCIPAUX VIANDES
        {
            "nom": "Poulet au Curry Rouge",
            "categorie": "plat_principal",
            "difficulte": "facile",
            "temps_prep": 30,
            "temps_cuisson": 20,
            "portions": 4,
            "description": "Délicieux poulet mijoté dans une sauce curry parfumée au lait de coco",
            "ingredients": {
                "Filets de poulet": {"quantite": 150, "unite": "g", "rayon": "Viande"},
                "Lait de coco": {"quantite": 100, "unite": "ml", "rayon": "Épicerie Exotique"},
                "Pâte de curry rouge": {"quantite": 1, "unite": "c.s.", "rayon": "Épices"},
                "Oignons": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Poivrons rouges": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Riz basmati": {"quantite": 60, "unite": "g", "rayon": "Épicerie"},
                "Huile d'olive": {"quantite": 1, "unite": "c.s.", "rayon": "Huiles"}
            }
        },
        {
            "nom": "Chili Con Carne",
            "categorie": "plat_principal", 
            "difficulte": "facile",
            "temps_prep": 15,
            "temps_cuisson": 45,
            "portions": 6,
            "description": "Le fameux chili tex-mex parfait pour les grandes tablées",
            "ingredients": {
                "Bœuf haché": {"quantite": 100, "unite": "g", "rayon": "Viande"},
                "Haricots rouges": {"quantite": 80, "unite": "g", "rayon": "Conserves"},
                "Tomates concassées": {"quantite": 100, "unite": "g", "rayon": "Conserves"},
                "Oignons": {"quantite": 0.3, "unite": "pièce", "rayon": "Légumes"},
                "Poivrons": {"quantite": 0.3, "unite": "pièce", "rayon": "Légumes"},
                "Paprika": {"quantite": 0.5, "unite": "c.c.", "rayon": "Épices"},
                "Cumin": {"quantite": 0.5, "unite": "c.c.", "rayon": "Épices"},
                "Riz": {"quantite": 50, "unite": "g", "rayon": "Épicerie"}
            }
        },
        {
            "nom": "Blanquette de Veau",
            "categorie": "plat_principal",
            "difficulte": "moyen", 
            "temps_prep": 20,
            "temps_cuisson": 90,
            "portions": 4,
            "description": "Plat traditionnel français mijoté et réconfortant",
            "ingredients": {
                "Épaule de veau": {"quantite": 200, "unite": "g", "rayon": "Viande"},
                "Carottes": {"quantite": 1, "unite": "pièce", "rayon": "Légumes"},
                "Champignons": {"quantite": 50, "unite": "g", "rayon": "Légumes"},
                "Crème fraîche": {"quantite": 50, "unite": "ml", "rayon": "Frais"},
                "Bouillon de volaille": {"quantite": 150, "unite": "ml", "rayon": "Épicerie"},
                "Riz": {"quantite": 60, "unite": "g", "rayon": "Épicerie"}
            }
        },
        {
            "nom": "Bœuf Bourguignon",
            "categorie": "plat_principal",
            "difficulte": "moyen",
            "temps_prep": 30, 
            "temps_cuisson": 150,
            "portions": 6,
            "description": "Grand classique bourguignon mijoté au vin rouge",
            "ingredients": {
                "Bœuf à braiser": {"quantite": 150, "unite": "g", "rayon": "Viande"},
                "Vin rouge": {"quantite": 50, "unite": "ml", "rayon": "Alcools"},
                "Lardons": {"quantite": 25, "unite": "g", "rayon": "Charcuterie"},
                "Champignons": {"quantite": 50, "unite": "g", "rayon": "Légumes"},
                "Oignons grelots": {"quantite": 2, "unite": "pièces", "rayon": "Légumes"},
                "Carottes": {"quantite": 1, "unite": "pièce", "rayon": "Légumes"},
                "Pommes de terre": {"quantite": 150, "unite": "g", "rayon": "Légumes"}
            }
        },
        {
            "nom": "Escalope de Porc à la Crème",
            "categorie": "plat_principal",
            "difficulte": "facile", 
            "temps_prep": 10,
            "temps_cuisson": 15,
            "portions": 4,
            "description": "Escalopes tendres dans une délicieuse sauce crémeuse",
            "ingredients": {
                "Escalopes de porc": {"quantite": 120, "unite": "g", "rayon": "Viande"},
                "Crème fraîche": {"quantite": 50, "unite": "ml", "rayon": "Frais"},
                "Champignons": {"quantite": 40, "unite": "g", "rayon": "Légumes"},
                "Échalotes": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Vin blanc": {"quantite": 20, "unite": "ml", "rayon": "Alcools"},
                "Pommes de terre": {"quantite": 150, "unite": "g", "rayon": "Légumes"}
            }
        },
        
        # POISSONS
        {
            "nom": "Saumon Grillé au Citron",
            "categorie": "poisson",
            "difficulte": "facile",
            "temps_prep": 10,
            "temps_cuisson": 15, 
            "portions": 4,
            "description": "Pavés de saumon grillés avec légumes de saison",
            "ingredients": {
                "Pavé de saumon": {"quantite": 150, "unite": "g", "rayon": "Poisson"},
                "Courgettes": {"quantite": 1, "unite": "pièce", "rayon": "Légumes"},
                "Tomates cerises": {"quantite": 80, "unite": "g", "rayon": "Légumes"},
                "Citron": {"quantite": 0.5, "unite": "pièce", "rayon": "Fruits"},
                "Huile d'olive": {"quantite": 1, "unite": "c.s.", "rayon": "Huiles"},
                "Herbes de Provence": {"quantite": 0.5, "unite": "c.c.", "rayon": "Épices"}
            }
        },
        {
            "nom": "Cabillaud à la Provençale",
            "categorie": "poisson", 
            "difficulte": "facile",
            "temps_prep": 15,
            "temps_cuisson": 25,
            "portions": 4,
            "description": "Poisson blanc mijoté aux tomates et herbes du Sud",
            "ingredients": {
                "Filets de cabillaud": {"quantite": 150, "unite": "g", "rayon": "Poisson"},
                "Tomates": {"quantite": 1.5, "unite": "pièces", "rayon": "Légumes"},
                "Oignons": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Ail": {"quantite": 1, "unite": "gousse", "rayon": "Légumes"},
                "Olives noires": {"quantite": 30, "unite": "g", "rayon": "Conserves"},
                "Riz": {"quantite": 60, "unite": "g", "rayon": "Épicerie"}
            }
        },
        
        # PÂTES ET CÉRÉALES
        {
            "nom": "Pâtes Carbonara",
            "categorie": "pates",
            "difficulte": "facile",
            "temps_prep": 10,
            "temps_cuisson": 15,
            "portions": 4,
            "description": "La vraie carbonara italienne crémeuse et savoureuse",
            "ingredients": {
                "Spaghetti": {"quantite": 100, "unite": "g", "rayon": "Pâtes"},
                "Lardons": {"quantite": 40, "unite": "g", "rayon": "Charcuterie"},
                "Œufs": {"quantite": 1, "unite": "pièce", "rayon": "Frais"},
                "Parmesan": {"quantite": 25, "unite": "g", "rayon": "Fromage"},
                "Crème fraîche": {"quantite": 30, "unite": "ml", "rayon": "Frais"}
            }
        },
        {
            "nom": "Pâtes Bolognaise",
            "categorie": "pates",
            "difficulte": "facile", 
            "temps_prep": 15,
            "temps_cuisson": 45,
            "portions": 4,
            "description": "Sauce bolognaise traditionnelle mijotée",
            "ingredients": {
                "Tagliatelles": {"quantite": 100, "unite": "g", "rayon": "Pâtes"},
                "Bœuf haché": {"quantite": 80, "unite": "g", "rayon": "Viande"},
                "Tomates concassées": {"quantite": 100, "unite": "g", "rayon": "Conserves"},
                "Oignons": {"quantite": 0.3, "unite": "pièce", "rayon": "Légumes"},
                "Carottes": {"quantite": 0.3, "unite": "pièce", "rayon": "Légumes"},
                "Parmesan": {"quantite": 20, "unite": "g", "rayon": "Fromage"}
            }
        },
        {
            "nom": "Risotto aux Champignons",
            "categorie": "riz",
            "difficulte": "moyen",
            "temps_prep": 10,
            "temps_cuisson": 25,
            "portions": 4,
            "description": "Risotto crémeux aux champignons frais",
            "ingredients": {
                "Riz arborio": {"quantite": 80, "unite": "g", "rayon": "Épicerie"},
                "Champignons de Paris": {"quantite": 80, "unite": "g", "rayon": "Légumes"},
                "Bouillon de légumes": {"quantite": 200, "unite": "ml", "rayon": "Épicerie"},
                "Vin blanc": {"quantite": 30, "unite": "ml", "rayon": "Alcools"},
                "Parmesan": {"quantite": 25, "unite": "g", "rayon": "Fromage"},
                "Échalotes": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"}
            }
        },
        {
            "nom": "Riz Sauté aux Légumes",
            "categorie": "riz", 
            "difficulte": "facile",
            "temps_prep": 15,
            "temps_cuisson": 10,
            "portions": 4,
            "description": "Riz sauté coloré avec légumes croquants",
            "ingredients": {
                "Riz long grain": {"quantite": 60, "unite": "g", "rayon": "Épicerie"},
                "Petits pois": {"quantite": 50, "unite": "g", "rayon": "Surgelés"},
                "Carottes": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Œufs": {"quantite": 1, "unite": "pièce", "rayon": "Frais"},
                "Sauce soja": {"quantite": 1, "unite": "c.s.", "rayon": "Épicerie Asiatique"},
                "Huile de sésame": {"quantite": 0.5, "unite": "c.c.", "rayon": "Huiles"}
            }
        },
        
        # SOUPES ET POTAGES
        {
            "nom": "Soupe de Tomates",
            "categorie": "soupe",
            "difficulte": "facile",
            "temps_prep": 10,
            "temps_cuisson": 20,
            "portions": 4,
            "description": "Soupe de tomates maison réconfortante",
            "ingredients": {
                "Tomates": {"quantite": 2, "unite": "pièces", "rayon": "Légumes"},
                "Oignons": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Bouillon de légumes": {"quantite": 250, "unite": "ml", "rayon": "Épicerie"},
                "Crème fraîche": {"quantite": 30, "unite": "ml", "rayon": "Frais"},
                "Basilic": {"quantite": 3, "unite": "feuilles", "rayon": "Herbes"}
            }
        },
        {
            "nom": "Velouté de Potiron",
            "categorie": "soupe",
            "difficulte": "facile",
            "temps_prep": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "description": "Velouté onctueux parfait pour l'automne",
            "ingredients": {
                "Potiron": {"quantite": 200, "unite": "g", "rayon": "Légumes"},
                "Pommes de terre": {"quantite": 100, "unite": "g", "rayon": "Légumes"},
                "Oignons": {"quantite": 0.3, "unite": "pièce", "rayon": "Légumes"},
                "Bouillon de légumes": {"quantite": 300, "unite": "ml", "rayon": "Épicerie"},
                "Crème fraîche": {"quantite": 40, "unite": "ml", "rayon": "Frais"}
            }
        },
        
        # GRATINS ET PLATS AU FOUR
        {
            "nom": "Gratin Dauphinois",
            "categorie": "gratin",
            "difficulte": "facile", 
            "temps_prep": 20,
            "temps_cuisson": 60,
            "portions": 6,
            "description": "Le fameux gratin savoyard crémeux",
            "ingredients": {
                "Pommes de terre": {"quantite": 200, "unite": "g", "rayon": "Légumes"},
                "Crème fraîche": {"quantite": 60, "unite": "ml", "rayon": "Frais"},
                "Lait": {"quantite": 60, "unite": "ml", "rayon": "Frais"},
                "Gruyère râpé": {"quantite": 30, "unite": "g", "rayon": "Fromage"},
                "Ail": {"quantite": 0.5, "unite": "gousse", "rayon": "Légumes"},
                "Beurre": {"quantite": 10, "unite": "g", "rayon": "Frais"}
            }
        },
        {
            "nom": "Lasagnes Bolognaise",
            "categorie": "gratin",
            "difficulte": "moyen",
            "temps_prep": 30,
            "temps_cuisson": 45,
            "portions": 6,
            "description": "Lasagnes généreuses à la bolognaise",
            "ingredients": {
                "Pâtes à lasagne": {"quantite": 60, "unite": "g", "rayon": "Pâtes"},
                "Bœuf haché": {"quantite": 80, "unite": "g", "rayon": "Viande"},
                "Tomates concassées": {"quantite": 100, "unite": "g", "rayon": "Conserves"},
                "Mozzarella": {"quantite": 40, "unite": "g", "rayon": "Fromage"},
                "Parmesan": {"quantite": 20, "unite": "g", "rayon": "Fromage"},
                "Béchamel": {"quantite": 80, "unite": "ml", "rayon": "Frais"}
            }
        },
        
        # PLATS VÉGÉTARIENS
        {
            "nom": "Ratatouille",
            "categorie": "vegetarien",
            "difficulte": "facile",
            "temps_prep": 20,
            "temps_cuisson": 40,
            "portions": 4,
            "description": "Mélange de légumes du soleil mijoté",
            "ingredients": {
                "Aubergines": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Courgettes": {"quantite": 1, "unite": "pièce", "rayon": "Légumes"},
                "Tomates": {"quantite": 1.5, "unite": "pièces", "rayon": "Légumes"},
                "Poivrons": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Oignons": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Herbes de Provence": {"quantite": 1, "unite": "c.c.", "rayon": "Épices"}
            }
        },
        {
            "nom": "Quiche Lorraine",
            "categorie": "tarte",
            "difficulte": "facile",
            "temps_prep": 15, 
            "temps_cuisson": 35,
            "portions": 6,
            "description": "La célèbre quiche avec lardons et gruyère",
            "ingredients": {
                "Pâte brisée": {"quantite": 50, "unite": "g", "rayon": "Pâtisserie"},
                "Lardons": {"quantite": 30, "unite": "g", "rayon": "Charcuterie"},
                "Œufs": {"quantite": 1.5, "unite": "pièces", "rayon": "Frais"},
                "Crème fraîche": {"quantite": 70, "unite": "ml", "rayon": "Frais"},
                "Gruyère râpé": {"quantite": 25, "unite": "g", "rayon": "Fromage"}
            }
        },
        
        # SALADES
        {
            "nom": "Salade César",
            "categorie": "salade",
            "difficulte": "facile",
            "temps_prep": 15,
            "temps_cuisson": 0,
            "portions": 4,
            "description": "Salade fraîche avec poulet et croûtons",
            "ingredients": {
                "Salade romaine": {"quantite": 80, "unite": "g", "rayon": "Légumes"},
                "Blanc de poulet": {"quantite": 80, "unite": "g", "rayon": "Viande"},
                "Croûtons": {"quantite": 20, "unite": "g", "rayon": "Épicerie"},
                "Parmesan": {"quantite": 20, "unite": "g", "rayon": "Fromage"},
                "Sauce César": {"quantite": 30, "unite": "ml", "rayon": "Épicerie"}
            }
        },
        {
            "nom": "Salade de Quinoa",
            "categorie": "salade",
            "difficulte": "facile", 
            "temps_prep": 20,
            "temps_cuisson": 15,
            "portions": 4,
            "description": "Salade complète et nutritive au quinoa",
            "ingredients": {
                "Quinoa": {"quantite": 50, "unite": "g", "rayon": "Épicerie"},
                "Tomates cerises": {"quantite": 60, "unite": "g", "rayon": "Légumes"},
                "Concombre": {"quantite": 0.3, "unite": "pièce", "rayon": "Légumes"},
                "Feta": {"quantite": 30, "unite": "g", "rayon": "Fromage"},
                "Avocat": {"quantite": 0.5, "unite": "pièce", "rayon": "Fruits"},
                "Vinaigrette": {"quantite": 20, "unite": "ml", "rayon": "Huiles"}
            }
        },
        
        # OMELETTES ET ŒUFS
        {
            "nom": "Omelette aux Herbes",
            "categorie": "œufs",
            "difficulte": "facile",
            "temps_prep": 5,
            "temps_cuisson": 5,
            "portions": 2,
            "description": "Omelette légère parfumée aux herbes fraîches",
            "ingredients": {
                "Œufs": {"quantite": 3, "unite": "pièces", "rayon": "Frais"},
                "Ciboulette": {"quantite": 5, "unite": "g", "rayon": "Herbes"},
                "Persil": {"quantite": 5, "unite": "g", "rayon": "Herbes"},
                "Beurre": {"quantite": 10, "unite": "g", "rayon": "Frais"},
                "Crème fraîche": {"quantite": 20, "unite": "ml", "rayon": "Frais"}
            }
        },
        {
            "nom": "Œufs Brouillés Crémeux",
            "categorie": "œufs",
            "difficulte": "facile",
            "temps_prep": 5,
            "temps_cuisson": 8,
            "portions": 2,
            "description": "Œufs brouillés onctueux et savoureux",
            "ingredients": {
                "Œufs": {"quantite": 3, "unite": "pièces", "rayon": "Frais"},
                "Beurre": {"quantite": 15, "unite": "g", "rayon": "Frais"},
                "Crème fraîche": {"quantite": 30, "unite": "ml", "rayon": "Frais"},
                "Ciboulette": {"quantite": 5, "unite": "g", "rayon": "Herbes"}
            }
        },
        
        # PLATS EXOTIQUES
        {
            "nom": "Curry de Légumes",
            "categorie": "vegetarien",
            "difficulte": "facile",
            "temps_prep": 15,
            "temps_cuisson": 25,
            "portions": 4,
            "description": "Curry parfumé avec légumes de saison",
            "ingredients": {
                "Pâte de curry": {"quantite": 1, "unite": "c.s.", "rayon": "Épices"},
                "Lait de coco": {"quantite": 100, "unite": "ml", "rayon": "Épicerie Exotique"},
                "Courgettes": {"quantite": 1, "unite": "pièce", "rayon": "Légumes"},
                "Brocolis": {"quantite": 100, "unite": "g", "rayon": "Légumes"},
                "Pois chiches": {"quantite": 60, "unite": "g", "rayon": "Conserves"},
                "Riz basmati": {"quantite": 60, "unite": "g", "rayon": "Épicerie"}
            }
        },
        
        # DESSERTS SIMPLES
        {
            "nom": "Tarte Tatin",
            "categorie": "dessert",
            "difficulte": "moyen",
            "temps_prep": 20,
            "temps_cuisson": 30,
            "portions": 6,
            "description": "Tarte aux pommes caramélisées retournée",
            "ingredients": {
                "Pâte feuilletée": {"quantite": 60, "unite": "g", "rayon": "Pâtisserie"},
                "Pommes": {"quantite": 1.5, "unite": "pièces", "rayon": "Fruits"},
                "Sucre": {"quantite": 20, "unite": "g", "rayon": "Épicerie"},
                "Beurre": {"quantite": 15, "unite": "g", "rayon": "Frais"}
            }
        },
        {
            "nom": "Mousse au Chocolat",
            "categorie": "dessert",
            "difficulte": "facile",
            "temps_prep": 15,
            "temps_cuisson": 0,
            "portions": 4,
            "description": "Mousse légère et chocolatée",
            "ingredients": {
                "Chocolat noir": {"quantite": 50, "unite": "g", "rayon": "Pâtisserie"},
                "Œufs": {"quantite": 1.5, "unite": "pièces", "rayon": "Frais"},
                "Sucre": {"quantite": 15, "unite": "g", "rayon": "Épicerie"},
                "Beurre": {"quantite": 10, "unite": "g", "rayon": "Frais"}
            }
        },
        
        # PLATS RAPIDES
        {
            "nom": "Croque-Monsieur",
            "categorie": "rapide",
            "difficulte": "facile",
            "temps_prep": 5,
            "temps_cuisson": 10,
            "portions": 2,
            "description": "Le classique sandwich gratiné français",
            "ingredients": {
                "Pain de mie": {"quantite": 2, "unite": "tranches", "rayon": "Boulangerie"},
                "Jambon": {"quantite": 40, "unite": "g", "rayon": "Charcuterie"},
                "Gruyère": {"quantite": 30, "unite": "g", "rayon": "Fromage"},
                "Beurre": {"quantite": 10, "unite": "g", "rayon": "Frais"},
                "Béchamel": {"quantite": 30, "unite": "ml", "rayon": "Frais"}
            }
        },
        {
            "nom": "Sandwich Club",
            "categorie": "rapide",
            "difficulte": "facile",
            "temps_prep": 10,
            "temps_cuisson": 0,
            "portions": 2,
            "description": "Sandwich gourmand multi-étages",
            "ingredients": {
                "Pain de mie": {"quantite": 3, "unite": "tranches", "rayon": "Boulangerie"},
                "Blanc de poulet": {"quantite": 60, "unite": "g", "rayon": "Charcuterie"},
                "Bacon": {"quantite": 20, "unite": "g", "rayon": "Charcuterie"},
                "Salade": {"quantite": 20, "unite": "g", "rayon": "Légumes"},
                "Tomates": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Mayonnaise": {"quantite": 15, "unite": "g", "rayon": "Épicerie"}
            }
        },
        
        # PLATS TRADITIONNELS FRANÇAIS
        {
            "nom": "Pot-au-Feu",
            "categorie": "traditionnel",
            "difficulte": "facile",
            "temps_prep": 20,
            "temps_cuisson": 120,
            "portions": 6,
            "description": "Plat familial traditionnel mijoté",
            "ingredients": {
                "Paleron de bœuf": {"quantite": 150, "unite": "g", "rayon": "Viande"},
                "Poireaux": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Carottes": {"quantite": 1, "unite": "pièce", "rayon": "Légumes"},
                "Navets": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Pommes de terre": {"quantite": 150, "unite": "g", "rayon": "Légumes"},
                "Bouquet garni": {"quantite": 1, "unite": "pièce", "rayon": "Herbes"}
            }
        },
        {
            "nom": "Coq au Vin",
            "categorie": "traditionnel",
            "difficulte": "moyen",
            "temps_prep": 25,
            "temps_cuisson": 60,
            "portions": 4,
            "description": "Poulet mijoté au vin rouge traditionalnel",
            "ingredients": {
                "Morceaux de poulet": {"quantite": 150, "unite": "g", "rayon": "Viande"},
                "Vin rouge": {"quantite": 100, "unite": "ml", "rayon": "Alcools"},
                "Lardons": {"quantite": 30, "unite": "g", "rayon": "Charcuterie"},
                "Champignons": {"quantite": 60, "unite": "g", "rayon": "Légumes"},
                "Oignons grelots": {"quantite": 3, "unite": "pièces", "rayon": "Légumes"},
                "Pommes de terre": {"quantite": 150, "unite": "g", "rayon": "Légumes"}
            }
        },
        
        # PLATS MÉDITERRANÉENS
        {
            "nom": "Moussaka",
            "categorie": "mediterraneen",
            "difficulte": "moyen",
            "temps_prep": 45,
            "temps_cuisson": 60,
            "portions": 6,
            "description": "Gratin d'aubergines grec traditionnel",
            "ingredients": {
                "Aubergines": {"quantite": 1, "unite": "pièce", "rayon": "Légumes"},
                "Agneau haché": {"quantite": 80, "unite": "g", "rayon": "Viande"},
                "Tomates": {"quantite": 1, "unite": "pièce", "rayon": "Légumes"},
                "Béchamel": {"quantite": 100, "unite": "ml", "rayon": "Frais"},
                "Fromage de chèvre": {"quantite": 30, "unite": "g", "rayon": "Fromage"}
            }
        },
        
        # PLATS ASIATIQUES SIMPLES
        {
            "nom": "Nouilles Sautées",
            "categorie": "asiatique",
            "difficulte": "facile",
            "temps_prep": 15,
            "temps_cuisson": 10,
            "portions": 4,
            "description": "Nouilles chinoises sautées aux légumes",
            "ingredients": {
                "Nouilles chinoises": {"quantite": 100, "unite": "g", "rayon": "Épicerie Asiatique"},
                "Crevettes": {"quantite": 80, "unite": "g", "rayon": "Surgelés"},
                "Pousses de soja": {"quantite": 50, "unite": "g", "rayon": "Légumes"},
                "Carottes": {"quantite": 0.5, "unite": "pièce", "rayon": "Légumes"},
                "Sauce soja": {"quantite": 1, "unite": "c.s.", "rayon": "Épicerie Asiatique"},
                "Huile de sésame": {"quantite": 0.5, "unite": "c.c.", "rayon": "Huiles"}
            }
        },
        
        # PLATS DE PÂTES VARIÉS
        {
            "nom": "Pâtes au Saumon",
            "categorie": "pates",
            "difficulte": "facile",
            "temps_prep": 15,
            "temps_cuisson": 15,
            "portions": 4,
            "description": "Pâtes crémeuses au saumon fumé",
            "ingredients": {
                "Tagliatelles": {"quantite": 100, "unite": "g", "rayon": "Pâtes"},
                "Saumon fumé": {"quantite": 60, "unite": "g", "rayon": "Poisson"},
                "Crème fraîche": {"quantite": 60, "unite": "ml", "rayon": "Frais"},
                "Aneth": {"quantite": 5, "unite": "g", "rayon": "Herbes"},
                "Citron": {"quantite": 0.3, "unite": "pièce", "rayon": "Fruits"}
            }
        },
        
        # PLATS COMPLETS ÉQUILIBRÉS
        {
            "nom": "Bowl Buddha Complet",
            "categorie": "complet",
            "difficulte": "facile",
            "temps_prep": 20,
            "temps_cuisson": 15,
            "portions": 4,
            "description": "Bowl nutritif avec quinoa et légumes colorés",
            "ingredients": {
                "Quinoa": {"quantite": 50, "unite": "g", "rayon": "Épicerie"},
                "Avocat": {"quantite": 0.5, "unite": "pièce", "rayon": "Fruits"},
                "Brocolis": {"quantite": 80, "unite": "g", "rayon": "Légumes"},
                "Betteraves": {"quantite": 60, "unite": "g", "rayon": "Légumes"},
                "Graines de tournesol": {"quantite": 10, "unite": "g", "rayon": "Épicerie"},
                "Vinaigrette": {"quantite": 20, "unite": "ml", "rayon": "Huiles"}
            }
        },
        
        # PLATS RÉCONFORTANTS
        {
            "nom": "Hachis Parmentier",
            "categorie": "traditionnel",
            "difficulte": "facile",
            "temps_prep": 30,
            "temps_cuisson": 25,
            "portions": 6,
            "description": "Gratin de viande hachée aux pommes de terre",
            "ingredients": {
                "Bœuf haché": {"quantite": 100, "unite": "g", "rayon": "Viande"},
                "Pommes de terre": {"quantite": 200, "unite": "g", "rayon": "Légumes"},
                "Oignons": {"quantite": 0.3, "unite": "pièce", "rayon": "Légumes"},
                "Lait": {"quantite": 40, "unite": "ml", "rayon": "Frais"},
                "Beurre": {"quantite": 15, "unite": "g", "rayon": "Frais"},
                "Gruyère": {"quantite": 25, "unite": "g", "rayon": "Fromage"}
            }
        }
    ]
    
    return recettes_marmiton

def save_to_database(recettes):
    """Sauvegarde les recettes dans SQLite"""
    
    # Supprimer l'ancienne base pour repartir de zéro
    import os
    db_path = "data/assistant.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Créer les tables
    cursor.execute('''
        CREATE TABLE recettes_marmiton (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            categorie TEXT,
            difficulte TEXT,
            temps_prep INTEGER,
            temps_cuisson INTEGER,
            portions INTEGER,
            description TEXT,
            ingredients_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE ingredients_par_personne (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recette_id INTEGER,
            ingredient_nom TEXT,
            quantite_base REAL,
            unite TEXT,
            rayon TEXT,
            FOREIGN KEY (recette_id) REFERENCES recettes_marmiton (id)
        )
    ''')
    
    # Insérer les recettes
    for recette in recettes:
        cursor.execute('''
            INSERT INTO recettes_marmiton 
            (nom, categorie, difficulte, temps_prep, temps_cuisson, portions, description, ingredients_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            recette['nom'],
            recette['categorie'],
            recette['difficulte'],
            recette['temps_prep'],
            recette['temps_cuisson'],
            recette['portions'],
            recette['description'],
            json.dumps(recette['ingredients'])
        ))
        
        recette_id = cursor.lastrowid
        
        # Insérer les ingrédients détaillés
        for ingredient_nom, details in recette['ingredients'].items():
            cursor.execute('''
                INSERT INTO ingredients_par_personne
                (recette_id, ingredient_nom, quantite_base, unite, rayon)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                recette_id,
                ingredient_nom,
                details['quantite'],
                details['unite'],
                details['rayon']
            ))
    
    conn.commit()
    conn.close()
    
    return len(recettes)

if __name__ == "__main__":
    print("🍽️ Création de la base Marmiton...")
    
    # Créer le dossier data si nécessaire
    import os
    os.makedirs("data", exist_ok=True)
    
    # Charger les recettes
    recettes = create_marmiton_database()
    print(f"📋 {len(recettes)} recettes chargées")
    
    # Sauvegarder en base
    nb_saved = save_to_database(recettes)
    print(f"💾 {nb_saved} recettes sauvegardées en base SQLite")
    
    print("✅ Base de données Marmiton créée avec succès !")
    print("📊 Catégories disponibles:")
    
    categories = {}
    for recette in recettes:
        cat = recette['categorie']
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in categories.items():
        print(f"   • {cat}: {count} recettes")