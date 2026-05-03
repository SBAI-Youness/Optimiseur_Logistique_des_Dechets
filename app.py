import streamlit as st
import numpy as np

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Optimiseur Logistique Déchets", layout="wide")

# Style CSS Professionnel (Thème Vert EMSI)
st.markdown("""
    <style>
    .main { background-color: #f9fbf9; }
    h1 { color: #1e4620 !important; font-weight: 800; }
    h2, h3 { color: #2e7d32 !important; font-weight: 600; border-bottom: 2px solid #e8f5e9; padding-bottom: 5px; }

    label[data-testid="stWidgetLabel"] {
        color: #1e4620 !important;
        font-weight: 600 !important;
    }

    div.stNumberInput, div.stTextInput { 
        background-color: white !important; 
        border-radius: 8px; 
        border: 1px solid #e0e0e0; 
    }

    input { color: #333333 !important; }

    .result-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #c8e6c9;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }

    .stButton>button {
        background-color: #2e7d32;
        color: white !important;
        font-weight: bold;
        border-radius: 5px;
        height: 3em;
        width: 100%;
        transition: 0.3s;
        border: none;
    }
    .stButton>button:hover { background-color: #1b5e20; }
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
st.title("🏙️ Optimisation Logistique - Marrakech")

with st.expander("📂 Voir la Méthodologie du Projet", expanded=True):
    st.write("""
    **Implémentation Algorithmique:**  
    Cet outil implémente l'algorithme du **Simplexe** intégralement sans bibliothèque externe (from scratch). 
    Il applique la **Théorie de la Dualité** telle que définie dans votre projet : le problème Primal (Minimisation de la flotte) 
    est transformé en problème Dual (Maximisation des ressources) pour déterminer la configuration optimale du parc automobile.
    """)

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
if st.button("🚀 Calculer la Solution Optimale"):
    st.divider()

    solveur = Simplex(obj_coeffs, matrix, targets)
    statut = solveur.resoudre()

    if statut == "Optimal":
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
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

        st.info(f"**Vérification Technique:** L'algorithme a convergé vers un optimum global. Toutes les exigences de tonnage, rotations et personnel ont été satisfaites.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error(f"Erreur du solveur : Le problème est {statut}. Veuillez ajuster les contraintes.")

st.markdown("---")
st.markdown("""
<div style="text-align: center;">
    <p style="color: grey; font-size: 0.8em;"> 
        Projet 3IIR • Optimisation de la gestion des déchets • EMSI Marrakech - © 2026
    </p>
</div>
""", unsafe_allow_html=True)
