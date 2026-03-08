# app.py
import streamlit as st
from quantum_toolbox import (
    get_h_chaos_blueprint, 
    get_cx_entangled_blueprint, 
    get_ry_biased_blueprint
)
from blueprint_generator import draw_blueprint

# Styling
st.set_page_config(page_title="Quantum Ghost Architect", layout="centered")

st.title("🏗️ Quantum Ghost Architecture")
st.markdown("""
### Reconstructing the Blueprint
We took a step back from abstract randomness to focus on **Cohesive Structures**.
Select a quantum circuit below. The 4-qubit statevector (the *Invisible Architecture*) 
determines the growth strategy and aesthetic style of a **Gap-Free Hexagonal Tiling** (the *Visible Blueprint*).
""")

col1, col2, col3 = st.columns(3)
params = None

with col1:
    if st.button("H-Chaos Blueprint"):
        params = get_h_chaos_blueprint()
        
with col2:
    if st.button("CX-Entangled Blueprint"):
        params = get_cx_entangled_blueprint()
        
with col3:
    if st.button("RY-Biased Blueprint"):
        params = get_ry_biased_blueprint()

# Output Rendering
if params:
    st.divider()
    with st.spinner("Observing the collapsed architectural state..."):
        fig = draw_blueprint(params)
        st.pyplot(fig)
    
    st.caption("This cohesive schematic represents the observed spatial manifestation of the quantum circuit.")