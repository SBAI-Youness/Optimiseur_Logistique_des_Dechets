# 🏙️ Optimiseur Logistique des Déchets - Ville de Marrakech

Un outil d'aide à la décision conçu pour optimiser l'allocation de la flotte de collecte des déchets. Cette application utilise la programmation linéaire pour minimiser les ressources nécessaires tout en garantissant une couverture logistique complète.

## 📖 Présentation du Projet

La planification de la collecte des déchets urbains nécessite une gestion rigoureuse des contraintes de tonnage, de personnel et de rotations quotidiennes. Cet outil modélise ces variables pour déterminer le nombre optimal de véhicules à déployer, permettant ainsi de réduire les coûts opérationnels et l'empreinte carbone.

### Fonctionnalités Clés
*   **Minimisation de Flotte:** Détermination du nombre minimal de véhicules par type (Ménagers, Industriels, Hospitaliers).
*   **Respect des Seuils:** Prise en compte automatique des exigences minimales de tonnage et de sécurité sanitaire.
*   **Aide à la Décision:** Calcul précis de la répartition avec application d'une logique de majoration pour un déploiement réel.

---

## ⚙️ Moteur Mathématique

L'outil intègre un algorithme spécialisé développé sans bibliothèques d'optimisation externes:

1.  **Simplexe Natif:** Implémentation complète du moteur de résolution linéaire.
2.  **Théorie de la Dualité:** Conversion du problème de minimisation pour une résolution plus efficace et une analyse précise des ressources.
3.  **Analyse de Convergence:** Validation automatique des résultats pour garantir l'atteinte d'un optimum global.

---

## 🚀 Installation et Lancement

### 1. Configuration de l'environnement
Clonez le projet et configurez l'environnement virtuel pour isoler les dépendances.

```bash
# Accéder au dossier du projet
cd optimisation-dechets-marrakech

# Création de l'environnement virtuel
python3 -m venv venv
```

### 2. Activation de l'environnement
Sur Linux / macOS:
```bash
source venv/bin/activate
```

Sur Windows:
```bash
.\venv\Scripts\activate
```

### 3. Installation et Lancement
```bash
# Installation des dépendances via le fichier requirements.txt
pip install -r requirements.txt

# Lancement du tableau de bord
streamlit run app.py
```

---

## 🛠️ Utilisation
1. Configuration: Ajustez le nombre de variables et de contraintes via la barre latérale.
2. Définition: Identifiez les types de camions et leurs coefficients de coût.
3. Contraintes: Saisissez les exigences logistiques (ex: tonnes minimum par jour).
4. Résolution: Exécutez le calcul pour obtenir la répartition optimale de la flotte.