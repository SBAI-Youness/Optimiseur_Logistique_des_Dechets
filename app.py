import streamlit as st
from pulp import LpProblem, LpMinimize, LpMaximize, LpVariable, lpSum, value, LpStatus

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Waste Logistics Optimizer | Marrakesh", layout="wide")

# Professional CSS Styling
st.markdown("""
    <style>
    /* Global styles */
    .main { background-color: #f9fbf9; }
    h1 { color: #1e4620; font-weight: 800; }
    h2, h3 { color: #2e7d32; font-weight: 600; border-bottom: 2px solid #e8f5e9; padding-bottom: 5px; }
    
    /* Input containers */
    div.stNumberInput, div.stTextInput { 
        background-color: white; 
        border-radius: 8px; 
        border: 1px solid #e0e0e0; 
    }
    
    /* Result card */
    .result-card {
        background-color: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #c8e6c9;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content { background-color: #ffffff; }
    
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        height: 3em;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1b5e20;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SYSTEM SETTINGS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    n_vars = st.number_input("Number of Decision Variables", min_value=1, max_value=6, value=3)
    n_constraints = st.number_input("Number of Constraints (Targets)", min_value=1, max_value=8, value=4)
    st.divider()
    st.info("The system uses the **Dual Simplex** logic to find the optimal minimization point for the fleet.")

# --- MAIN CONTENT ---
st.title("🏙️ Marrakesh Waste Logistics Optimizer")

# --- PROJECT OVERVIEW (From PDF) ---
with st.expander("📂 View Project Background & Methodology", expanded=True):
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.write("""
        **Introduction:**
        In the context of rapid urbanization in Marrakesh, traditional waste collection planning leads to resource sub-optimization. 
        This project implements **Linear Programming** to minimize the environmental and economic footprint of the city's vehicle fleet.
        
        **Methodology:**
        1. **Variable Definition:** Mapping collection types to $x_1, x_2, ... x_n$.
        2. **Optimization Model:** Minimization of the total fleet cost ($Z$).
        3. **Constraint Management:** Ensuring mandatory thresholds for Tonnage, Personnel, and Logistics rotations ($\ge$).
        4. **Resolution via Duality:** For complex models with 3+ variables, we use the Theory of Duality to solve for the primal minimum via the dual maximum.
        """)
    with col_b:
        st.success("""
        **Operational Target:**
        Optimize the allocation of Household, Industrial, and Hospital waste trucks to satisfy 100% of municipal requirements at the lowest cost.
        """)

st.divider()

# --- INPUT SECTION ---
col_var, col_cons = st.columns([1, 1], gap="large")

with col_var:
    st.subheader("1. Variables & Objective (Min Z)")
    st.caption("Define the meaning of each $x$ variable and its coefficient in the Z function.")
    
    obj_coeffs = []
    descriptions = []
    
    for i in range(n_vars):
        v_box = st.container(border=True)
        with v_box:
            c1, c2, c3 = st.columns([1, 2, 2])
            c1.markdown(f"#### x{i+1}")
            desc = c2.text_input("Meaning", placeholder="e.g. Household Truck", key=f"d{i}")
            coeff = c3.number_input("Z Coeff", value=1.0, key=f"z{i}")
            obj_coeffs.append(coeff)
            descriptions.append(desc)

with col_cons:
    st.subheader("2. Target Constraints (≥)")
    st.caption("Input technical requirements and target values for the city.")
    
    matrix = []
    targets = []
    
    for j in range(n_constraints):
        c_box = st.container(border=True)
        with c_box:
            st.markdown(f"**Constraint C{j+1}**")
            cols = st.columns(n_vars + 1)
            row_coeffs = []
            for i in range(n_vars):
                val = cols[i].number_input(f"x{i+1}", value=1.0, key=f"c{j}{i}")
                row_coeffs.append(val)
            rhs = cols[-1].number_input("Target", value=10.0, key=f"rhs{j}")
            matrix.append(row_coeffs)
            targets.append(rhs)

# --- SOLVER LOGIC ---
if st.button("🚀 Calculate Optimization Results"):
    st.divider()
    
    # Mathematical Solver
    prob = LpProblem("Waste_Management_Problem", LpMinimize)
    x_vars = [LpVariable(f"x{i+1}", lowBound=0) for i in range(n_vars)]
    
    # Primal Objective
    prob += lpSum([obj_coeffs[i] * x_vars[i] for i in range(n_vars)])
    
    # Primal Constraints
    for j in range(n_constraints):
        prob += lpSum([matrix[j][i] * x_vars[i] for i in range(n_vars)]) >= targets[j]
    
    prob.solve()

    if LpStatus[prob.status] == 'Optimal':
        # UI RESULTS
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        res_header, res_status = st.columns([2, 1])
        res_header.header("🏁 Results Analysis")
        res_status.success(f"STATUS: {LpStatus[prob.status]}")
        
        opt_val = value(prob.objective)
        
        metric_col1, metric_col2 = st.columns(2)
        metric_col1.metric("Optimal Total Fleet (Z min)", f"{opt_val:.3f}")
        # Mathematical Majorant Decision
        metric_col2.metric("Operational Fleet (Recommended)", f"{int(-(-opt_val // 1))} Trucks")
        
        st.write("### Resource Allocation Strategy:")
        res_cols = st.columns(n_vars)
        for idx, v in enumerate(x_vars):
            with res_cols[idx]:
                st.write(f"**Variable x{idx+1}**")
                st.markdown(f"`{value(v):.2f}` units")
                st.caption(f"{descriptions[idx] if descriptions[idx] else 'No desc provided'}")
        
        # Dual Summary explanation
        st.info(f"**Optimization Summary:** The most constrained target determines the fleet size. Based on your inputs, the city requires a minimum deployment of {int(-(-opt_val // 1))} units across all waste categories to satisfy logistical safety thresholds.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.error("❌ The model is infeasible with current constraints. Please adjust your target values.")

# --- FOOTER ---
st.markdown("---")
st.caption("3IIR Project • Optimization de la gestion des déchets à Marrakech • EMSI © 2026")
