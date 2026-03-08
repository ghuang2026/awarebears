# app.py
import streamlit as st
from quantum_toolbox import (
    get_h_superposition_blueprint,
    get_x_flip_blueprint,
    get_cx_entangled_blueprint,
    get_t_interference_blueprint,
    get_z_kickback_blueprint,
    get_ry_biased_blueprint,
)
from blueprint_generator import draw_blueprint

st.set_page_config(page_title="Quantum Ghost Architect", layout="wide")

# ── Sidebar: gate glossary ────────────────────────────────────────────────────
with st.sidebar:
    st.title("⟨ Gate Glossary ⟩")
    st.divider()
    st.markdown("""
**H — Hadamard**
Places each qubit in equal superposition of |0⟩ and |1⟩.
Every layout is equally probable — maximum entropy.

---
**X — Pauli-X**
Flips |0⟩ → |1⟩ on every qubit. Fully deterministic.
Always collapses to the same high-energy layout (|1111⟩).

---
**CX — CNOT**
Entangles qubit pairs. If qubit A = 0, qubit B *must* be 0.
Only correlated states can appear: |0000⟩, |0011⟩, |1100⟩, |1111⟩.
In the blueprint, **Kitchen↔Dining** and **Bedroom↔Bathroom**
are structurally forced adjacent.

---
**T — T-Gate**
Applies a 45° phase rotation e^(iπ/4) inside superposition.
A second Hadamard converts this invisible phase into amplitude bias:
each qubit collapses to |0⟩ with ~85% probability.

---
**Z — Phase Kickback**
Z gate applied only to qubits 0 and 2 inside superposition.
H·Z·H = X on those qubits → deterministic |1⟩.
H·H = I on qubits 1 and 3 → deterministic |0⟩.
Always |0101⟩. The invisible phase is made visible through interference.

---
**RY — Y-Rotation**
Rotates the Bloch sphere by π/3 (60°).
P(|1⟩) ≈ 25% per qubit — a tunable, continuous bias.
""")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("Quantum Ghost Architecture")
st.markdown(
    "Select a quantum gate circuit. The 4-qubit measurement collapse encodes the "
    "**growth strategy** (bits 0–1) and **aesthetic theme** (bits 2–3) of the generated floor plan. "
    "Each gate shapes the *invisible probability architecture* behind the blueprint."
)
st.divider()

params = None

row1 = st.columns(3)
with row1[0]:
    if st.button("H  ·  Hadamard Superposition", use_container_width=True):
        params = get_h_superposition_blueprint()
with row1[1]:
    if st.button("X  ·  Pauli-X Flip", use_container_width=True):
        params = get_x_flip_blueprint()
with row1[2]:
    if st.button("CX  ·  CNOT Entangle", use_container_width=True):
        params = get_cx_entangled_blueprint()

row2 = st.columns(3)
with row2[0]:
    if st.button("T  ·  T-Gate Interference", use_container_width=True):
        params = get_t_interference_blueprint()
with row2[1]:
    if st.button("Z  ·  Phase Kickback", use_container_width=True):
        params = get_z_kickback_blueprint()
with row2[2]:
    if st.button("RY  ·  Biased Rotation", use_container_width=True):
        params = get_ry_biased_blueprint()

# ── Output ────────────────────────────────────────────────────────────────────
if params:
    st.divider()
    with st.spinner("Collapsing quantum state into architecture..."):
        fig = draw_blueprint(params)

    meta_col, fig_col = st.columns([1, 3])
    with meta_col:
        st.markdown("### Measurement")
        st.metric("Quantum State",    f"|{params['raw_quantum_state']}⟩")
        st.metric("Growth Strategy",  params["growth_strategy"])
        st.metric("Style Code",       params["style_code"])
        if params.get("entangled_pairs"):
            st.divider()
            st.markdown("**Entangled Room Pairs**")
            for a, b in params["entangled_pairs"]:
                st.markdown(f"- `{a}` ⟷ `{b}`")
    with fig_col:
        st.pyplot(fig)
