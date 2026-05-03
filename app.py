import streamlit as st
import numpy as np

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Optimiseur Logistique Déchets", layout="wide")

# Style CSS Premium (Thème Vert EMSI Optimisé)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    /* Global Styles */
    .main {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Palette de Couleurs & Variables */
    :root {
        --primary-green: #2e7d32;
        --vibrant-green: #4caf50;
        --soft-green: rgba(76, 175, 80, 0.1);
        --glass-bg: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.1);
    }

    /* Typography Improvements */
    h1 {
        color: var(--vibrant-green) !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px !important;
        margin-bottom: 1.5rem !important;
        text-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    h2, h3 {
        color: var(--vibrant-green) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--soft-green) !important;
        padding-bottom: 12px;
        margin-top: 2rem !important;
    }

    /* Widget Labels & Captions */
    label[data-testid="stWidgetLabel"] p {
        color: inherit !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        opacity: 0.9;
    }

    .stCaption {
        font-size: 0.9rem !important;
        opacity: 0.7;
        font-style: italic;
    }

    /* Containers & Cards (Glassmorphism) */
    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"] {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(12px) saturate(180%);
        -webkit-backdrop-filter: blur(12px) saturate(180%);
        border-radius: 20px !important;
        border: 1px solid var(--glass-border) !important;
        padding: 1.8rem !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    div[data-testid="stVerticalBlock"] > div[style*="border: 1px solid"]:hover {
        border-color: var(--vibrant-green) !important;
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }

    /* Inputs Aesthetics */
    .stNumberInput input, .stTextInput input {
        border-radius: 12px !important;
        border: 1px solid var(--glass-border) !important;
        padding: 0.6rem !important;
        transition: border-color 0.3s ease;
    }
    
    .stNumberInput input:focus {
        border-color: var(--vibrant-green) !important;
    }

    /* Premium Action Button */
    .stButton>button {
        background: linear-gradient(135deg, #1b5e20 0%, #4caf50 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 15px !important;
        border: none !important;
        height: 3.8rem !important;
        width: 100%;
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.3) !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-top: 1rem;
    }

    .stButton>button:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 30px rgba(46, 125, 50, 0.5) !important;
    }

    .stButton>button:active {
        transform: translateY(0) scale(0.98);
    }

    /* Metrics Appearance */
    [data-testid="stMetricValue"] {
        color: var(--vibrant-green) !important;
        font-weight: 800 !important;
        font-family: 'Outfit', sans-serif !important;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: var(--soft-green) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ALGORITHME DU SIMPLEXE (DÉVELOPPÉ DE ZÉRO) ---
class Simplex:
    def __init__(self, obj_coeffs, A_matrix, b_targets):
        # Conversion du Primal (Minimisation >=) en Dual (Maximisation <=)
        # Primal Min Z = cx avec Ax >= b
        # Dual Max W = by avec A^T y <= c
        self.c_dual = b_targets
        self.A_dual = np.array(A_matrix).T
        self.b_dual = obj_coeffs

        self.nb_vars = len(self.c_dual)
        self.nb_contraintes = len(self.b_dual)

        # Construction du Tableau Initial
        # [ A | I | b ]
        # [ -c | 0 | 0 ]
        self.tableau = np.zeros((self.nb_contraintes + 1, self.nb_vars + self.nb_contraintes + 1))
        self.tableau[:self.nb_contraintes, :self.nb_vars] = self.A_dual
        self.tableau[:self.nb_contraintes, self.nb_vars:self.nb_vars+self.nb_contraintes] = np.eye(self.nb_contraintes)
        self.tableau[:self.nb_contraintes, -1] = self.b_dual
        self.tableau[-1, :self.nb_vars] = -np.array(self.c_dual)

    def resoudre(self):
        iterations = 0
        while np.any(self.tableau[-1, :-1] < 0) and iterations < 100:
            # Colonne Pivot (Variable entrante)
            colonne_pivot = np.argmin(self.tableau[-1, :-1])

            # Ligne Pivot (Test du ratio minimum)
            ratios = []
            for i in range(self.nb_contraintes):
                val = self.tableau[i, colonne_pivot]
                if val > 0:
                    ratios.append(self.tableau[i, -1] / val)
                else:
                    ratios.append(np.inf)

            ligne_pivot = np.argmin(ratios)
            if ratios[ligne_pivot] == np.inf:
                return "Non borné"

            # Opération de pivotage
            valeur_pivot = self.tableau[ligne_pivot, colonne_pivot]
            self.tableau[ligne_pivot, :] /= valeur_pivot
            for i in range(len(self.tableau)):
                if i != ligne_pivot:
                    self.tableau[i, :] -= self.tableau[i, colonne_pivot] * self.tableau[ligne_pivot, :]
            iterations += 1

        return "Optimal"

    def obtenir_resultats_primaux(self):
        # D'après le théorème de dualité : 
        # Les variables primales (x) correspondent aux "shadow prices" en bas du tableau
        return self.tableau[-1, self.nb_vars:self.nb_vars+self.nb_contraintes]

    def obtenir_valeur_objectif(self):
        return self.tableau[-1, -1]

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("⚙️ Configuration")
    n_vars = st.number_input("Nombre de variables de décision (x)", min_value=1, max_value=6, value=3)
    n_constraints = st.number_input("Nombre de contraintes (C)", min_value=1, max_value=8, value=4)
    st.divider()
    st.success("**Algorithme:** Simplexe Natif\n\nRésolution via la théorie de la Dualité.")

# --- CONTENU PRINCIPAL ---
st.title("Optimiseur Logistique des Déchets - Ville de Marrakech")

with st.expander("📂 À propos du Projet", expanded=True):
    st.write("""
    **Description du Projet**  
    Cette application est un outil d'aide à la décision conçu pour optimiser la collecte des déchets à Marrakech. 
    Son objectif est de déterminer la configuration minimale de la flotte de camions nécessaire pour répondre aux besoins 
    logistiques, humains et sanitaires de la ville.

    **Fonctionnement Global**
    1. **Saisie des Besoins :** L'utilisateur définit les types de déchets (ménagers, industriels, hospitaliers) et les objectifs de la municipalité.
    2. **Calcul Optimisé :** Le système utilise un modèle mathématique de **Programmation Linéaire** pour identifier la solution la plus économique.
    3. **Résolution :** Le moteur de calcul intègre un algorithme **Simplexe** personnalisé, basé sur la théorie de la dualité, pour garantir un résultat précis sans dépendre de bibliothèques externes.

    **Solution Apportée :** Le projet permet d'assurer un service public de qualité (tonnage respecté, personnel mobilisé) tout en minimisant l'utilisation des ressources et le nombre de véhicules en circulation.
    """)

st.divider()

st.divider()

# --- SECTION DES ENTRÉES ---
col_var, col_cons = st.columns([1, 1], gap="large")

with col_var:
    st.subheader("1. Variables et Objectif (Min Z)")
    st.caption("Définissez le coût unitaire de chaque type de camion (Généralement Z = x1 + x2 + ...)")
    obj_coeffs = []
    descriptions = []
    for i in range(n_vars):
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 2, 2])
            c1.markdown(f"#### x{i+1}")
            desc = c2.text_input("Désignation", value=f"Type Déchet {i+1}", key=f"d{i}")
            coeff = c3.number_input("Poids (Coût Z)", value=1.0, key=f"z{i}")
            obj_coeffs.append(coeff)
            descriptions.append(desc)

with col_cons:
    st.subheader("2. Seuils et Contraintes (≥)")
    st.caption("Matrice des exigences logistiques de la ville")
    matrix = []
    targets = []
    for j in range(n_constraints):
        with st.container(border=True):
            st.markdown(f"**Contrainte C{j+1}**")
            cols = st.columns(n_vars + 1)
            row_coeffs = []
            for i in range(n_vars):
                val = cols[i].number_input(f"x{i+1} coeff", value=1.0, key=f"c{j}{i}", label_visibility="collapsed")
                row_coeffs.append(val)
            rhs = cols[-1].number_input("Cible (≥)", value=10.0, key=f"rhs{j}")
            matrix.append(row_coeffs)
            targets.append(rhs)

# --- CALCUL ---
if st.button("Calculer la Solution Optimale"):
    st.divider()

    solveur = Simplex(obj_coeffs, matrix, targets)
    statut = solveur.resoudre()

    if statut == "Optimal":
        with st.container(border=True):
            st.header("📊 Tableau de Bord des Résultats")
    
            # Récupération des valeurs
            valeur_z = solveur.obtenir_valeur_objectif()
            valeurs_x = solveur.obtenir_resultats_primaux()
    
            m1, m2 = st.columns(2)
            m1.metric("Valeur Calculée (Z min)", f"{valeur_z:.2f}")
            # Majoration (Rounding up comme dans le rapport Sec 2.6.3)
            majoration = int(np.ceil(round(valeur_z, 4)))
            m2.metric("Parc Automobile Opérationnel", f"{majoration} Camions")
    
            st.write("---")
            st.write("### Distribution recommandée par type:")
            res_cols = st.columns(n_vars)
            for idx in range(n_vars):
                with res_cols[idx]:
                    st.write(f"**Variable x{idx+1}**")
                    st.subheader(f"{valeurs_x[idx]:.2f}")
                    st.caption(descriptions[idx])    
    else:
        st.error(f"Erreur du solveur : Le problème est {statut}. Veuillez ajuster les contraintes.")

st.markdown("---")
st.markdown("""
<div style="text-align: center; margin-top: 5rem; padding: 2rem; border-top: 1px solid var(--glass-border);">
    <p style="opacity: 0.6; font-size: 0.85em; font-weight: 300; letter-spacing: 0.5px;"> 
        Optimiseur Logistique des Déchets • Ville de Marrakech - © 2026
    </p>
</div>
""", unsafe_allow_html=True)
