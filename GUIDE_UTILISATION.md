# 🛒 Guide d'Utilisation - Assistant Courses Michael

**Ton assistant IA personnalisé pour optimiser tes courses et repas**

## 🚀 Démarrage Rapide

### Lancer l'Assistant
```bash
cd /root/.openclaw/workspace/assistant-courses-michael
./start.sh
```

**Accès :** http://localhost:5000

## 🎯 Comment ça Marche

### 1. 🤖 Suggestions IA Personnalisées
- **Basées sur tes habitudes** : Riz sauté, brocolis vapeur, poulet mariné, etc.
- **Apprentissage continu** : Plus tu utilises, plus ça s'améliore
- **Contexte intelligent** : Weekend → plats mijotés, Semaine → plats rapides
- **Score IA** : Chaque suggestion a un score basé sur tes préférences

### 2. ✅ Workflow Optimisé
1. **Suggestions** : L'IA propose 6 recettes personnalisées
2. **Sélection** : Tu choisis celles qui te tentent
3. **Vérif Stock** : Tu indiques ce que tu as déjà
4. **Liste Coop** : Génération automatique par rayons

### 3. 🧠 Intelligence Artificielle

#### Ce que l'IA Apprend
- **Choix fréquents** : Recettes que tu sélectionnes souvent
- **Refus** : Ce que tu ne veux jamais
- **Timing** : Habitudes selon le jour de la semaine
- **Préférences famille** : Plats adaptés enfants, portions, etc.

#### Facteurs de Suggestion
- **Historique personnel** : +2 points par choix précédent
- **Pénalité refus** : -3 points par refus
- **Nouveauté** : +2 points si pas préparé récemment
- **Contexte temporel** : Weekend/semaine, saison
- **Variété** : Évite la répétition des mêmes types

## 🏪 Intégration Coop

### Liste Optimisée
- **Organisée par rayons** : Fruits & Légumes → Viande → Frais → etc.
- **Prix estimés** : Budget approximatif avant les courses  
- **Stock intelligent** : Ne propose que ce qui manque
- **Parcours optimisé** : Ordre des rayons Coop respecté

### Rayons Intégrés
1. Fruits & Légumes
2. Viande & Poissons  
3. Charcuterie
4. Produits Frais
5. Fromages
6. Pâtes, Riz & Féculents
7. Conserves
8. Surgelés
9. Boulangerie
10. Huiles & Vinaigres
11. Épices & Condiments
12. Et plus...

## 👨‍👩‍👧‍👦 Adaptation Famille

### Profil Intégré
- **2 adultes + 2 enfants** (10 mois + 2,5 ans)
- **Portions adaptées** : Calcul automatique
- **Plats enfants** : Bonus pour recettes adaptées
- **Purées bébé** : Gestion spéciale 10 mois

### Recettes de Base
- **Gestion restes** : Riz sauté intelligent
- **Plats rapides** : Brocolis vapeur, poulet mariné  
- **Weekend** : Bœuf bourguignon, chili con carne
- **Classiques** : Bolognese, fajitas

## 📊 Fonctionnalités Avancées

### Apprentissage Continu
- **Base de données SQLite** : Stockage local sécurisé
- **Historique complet** : Toutes tes courses archivées
- **Patterns temporels** : Analyse jours/saisons
- **Optimisation budget** : Tracking des dépenses

### API Complète
- **GET /api/suggestions** : Nouvelles suggestions
- **POST /api/liste-courses** : Génération liste
- **GET/POST /api/stock** : Gestion stock maison
- **POST /api/choix** : Enregistrement apprentissage

## 🎯 Tips d'Utilisation

### Maximiser l'IA
- **Utilise régulièrement** : Plus de données = meilleures suggestions
- **Varie tes choix** : L'IA apprend de la diversité
- **Feedback honnête** : Indique ton stock réel
- **Saisons** : L'IA s'adapte aux périodes

### Optimiser les Courses
- **Screenshot la liste** : Pour le magasin
- **Ordre des rayons** : Suit l'organisation Coop
- **Budget prévisionnel** : Planifie tes dépenses
- **Stock régulier** : Met à jour ton inventaire

## 🔧 Dépannage

### Problèmes Courants
- **Port 5000 occupé** : Change le port dans app.py
- **Base de données** : Supprime data/assistant.db pour reset
- **Suggestions vides** : L'IA apprend, utilise plus
- **Erreur Flask** : Vérifie python3-flask installé

### Reset Complet
```bash
rm data/assistant.db
python3 app.py
```

## 📈 Évolution Future

### Prochaines Fonctionnalités
- **Import recettes externes** : De tes sites préférés
- **Notifications push** : Rappels courses/stock
- **Analyse nutritionnelle** : Équilibre des repas
- **Synchronisation famille** : Partage avec ta conjointe

---

**🎉 Profite de ton Assistant Courses Intelligent !**

*Développé spécialement pour la famille Michael avec amour et IA* 💙