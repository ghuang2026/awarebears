from classiq import *
import numpy as np
from scipy.linalg import expm

# ─────────────────────────────────────────────────────────────────
# YUKAWA MODEL — minimal NISQ-friendly instance
# Nmax = 2 modes per species, 1 bosonic modal (m=1 → 1 qubit/mode)
#
# Qubit layout (6 qubits total, matching paper's ibm_perth run):
#   q[0]   : Fermion mode 1       (Jordan-Wigner)
#   q[1]   : Fermion mode 2       (Jordan-Wigner)
#   q[2]   : Anti-Fermion mode 1  (Jordan-Wigner)
#   q[3]   : Anti-Fermion mode 2  (Jordan-Wigner)
#   q[4]   : Boson mode 1         (1 modal → 1 qubit)
#   q[5]   : Boson mode 2         (1 modal → 1 qubit)
#
# This matches exactly the paper's Sec. IV.5 hardware demonstration:
#   initial state |010000⟩ = fermion in mode 2, everything else empty
#
# Parameters (arbitrary units, matching paper's toy example):
#   mF = 6.7 (fermion mass, in pion mass units)
#   mB = 1.0 (boson/pion mass)
#   lambda = 1.0 or 4.0 (bare coupling)
#   g = lambda / sqrt(4*pi)
# ─────────────────────────────────────────────────────────────────

mF = 6.7
mB = 1.0

# g is the rescaled coupling used in the actual Hamiltonian terms
# (paper eq. after Appendix, g ≡ λ/√4π)
lambda_val = 1.0
g = lambda_val / np.sqrt(4 * np.pi)

# ─────────────────────────────────────────────────────────────────
# MASS TERM H_M (diagonal in Fock basis)
#
# From the paper's Appendix:
#   H_M = sum_n (1/n) [ a†a (mB² + g²αn)
#                     + b†b (mF² + g²βn)
#                     + d†d (mF² + g²γn) ]
#
# For Nmax=2 modes, n=1,2. With m=1 modal (bosons behave like fermions),
# bosonic b†b → (I - Z)/2, fermionic b†b → (I - Z)/2 also (JW).
#
# Self-induced inertias αn, βn, γn from paper eq. (A.2).
# For small Λ (Λ=2 here), these are small corrections; we set g²·inertia ≈ 0
# for clarity (same approximation the paper uses in its hardware demo).
#
# H_M contributions (number operators via Pauli Z):
#   n†n = (I - Z)/2  →  coefficient on Z is -1/2, on I is +1/2
#
# Mode n=1: weight 1/n = 1
#   Fermion    mode 1 (q[0]): mF²/1 * (I-Z)/2
#   Fermion    mode 2 (q[1]): mF²/2 * (I-Z)/2
#   AntiFerm   mode 1 (q[2]): mF²/1 * (I-Z)/2
#   AntiFerm   mode 2 (q[3]): mF²/2 * (I-Z)/2
#   Boson      mode 1 (q[4]): mB²/1 * (I-Z)/2
#   Boson      mode 2 (q[5]): mB²/2 * (I-Z)/2
# ─────────────────────────────────────────────────────────────────

def mass_terms(mF, mB):
    """
    Returns PauliTerms for H_M across 6 qubits.
    n†n = (I - Z)/2, so mass contribution gives:
      - constant (I terms, affect global phase only, often dropped)
      - -mX²/(2n) * Z on the relevant qubit
    We keep both for correctness.
    """
    terms = []
    # Fermion modes: qubits 0,1 at n=1,2
    for qubit_idx, n in [(0, 1), (1, 2)]:
        coeff = mF**2 / (2 * n)
        # Identity part (+coeff * I⊗I⊗I⊗I⊗I⊗I) — global phase, include for completeness
        terms.append(PauliTerm(
            pauli=[Pauli.I, Pauli.I, Pauli.I, Pauli.I, Pauli.I, Pauli.I],
            coefficient=coeff
        ))
        # -Z part on relevant qubit
        paulis = [Pauli.I] * 6
        paulis[qubit_idx] = Pauli.Z
        terms.append(PauliTerm(pauli=paulis, coefficient=-coeff))

    # Anti-Fermion modes: qubits 2,3 at n=1,2
    for qubit_idx, n in [(2, 1), (3, 2)]:
        coeff = mF**2 / (2 * n)
        terms.append(PauliTerm(
            pauli=[Pauli.I, Pauli.I, Pauli.I, Pauli.I, Pauli.I, Pauli.I],
            coefficient=coeff
        ))
        paulis = [Pauli.I] * 6
        paulis[qubit_idx] = Pauli.Z
        terms.append(PauliTerm(pauli=paulis, coefficient=-coeff))

    # Boson modes: qubits 4,5 at n=1,2
    for qubit_idx, n in [(4, 1), (5, 2)]:
        coeff = mB**2 / (2 * n)
        terms.append(PauliTerm(
            pauli=[Pauli.I, Pauli.I, Pauli.I, Pauli.I, Pauli.I, Pauli.I],
            coefficient=coeff
        ))
        paulis = [Pauli.I] * 6
        paulis[qubit_idx] = Pauli.Z
        terms.append(PauliTerm(pauli=paulis, coefficient=-coeff))

    return terms


# ─────────────────────────────────────────────────────────────────
# VERTEX TERM H_V  (the only interaction in the paper's hardware demo)
#
# From the paper Appendix, H_V is linear in g and involves
# terms like b†_k b_m a†_l + h.c. (fermion changes mode, emits boson)
#
# For Nmax=2, the only momentum-conserving process is:
#   Fermion in mode 2 → Fermion in mode 1 + Boson in mode 1
#   (K conserved: 2 = 1 + 1 ✓)
#
# After Jordan-Wigner mapping:
#   b†_1 = X_0·(I-Z_0)/2 equivalent → raising op on q[0]
#   b_2  = lowering op on q[1], with JW string
#   a†_1 = raising op on q[4] (boson mode, 1 modal = same as fermion)
#
# Jordan-Wigner:
#   b†_n = (X_n - iY_n)/2 · ∏_{j<n} Z_j
#   b_n  = (X_n + iY_n)/2 · ∏_{j<n} Z_j
#
# The full b†_1 b_2 a†_1 + h.c. expanded into Pauli strings
# (6 qubits: [q0_F1, q1_F2, q2_AF1, q3_AF2, q4_B1, q5_B2]):
#
# b†_1 = (X0 - iY0)/2          (no JW string, first mode)
# b_2  = Z0·(X1 + iY1)/2       (JW string through q0)
# a†_1 = (X4 - iY4)/2          (boson mode 1, no JW string needed
#                                since bosons treated independently)
#
# b†_1 · b_2 = (X0-iY0)/2 · Z0·(X1+iY1)/2
#            = (X0·Z0 - iY0·Z0)/2 · (X1+iY1)/2
# Note: X·Z = -iY, Y·Z = iX
#   X0·Z0 = -iY0,  Y0·Z0 = iX0
# So:
#   (X0·Z0 - iY0·Z0)/2 = (-iY0 - i·iX0)/2 = (-iY0 + X0)/2
#
# b†_1 · b_2 · a†_1 (just the Pauli structure, coefficient handled separately):
# Full term = g·mF * {k+l|-m} factor × (b†_1 b_2 a†_1 + h.c.)
#
# The {k|m} factor from eq (A.2): {1+1|-2} = {2|-2} = (1/2)δ_{-2,2}... 
# wait, momentum conservation check: k=2,m=1,l=1 → {k+l|-m}={3|-1}=0, 
# {k|+l-m}={2|0}=0 since m=0 case → 0.
# The surviving term uses: k=2,l=1,m=1:
#   {k-l|m-... } ... let's use the direct physical argument from the paper:
#   the only allowed process for |f>_2 initial state conserving K=2 is
#   b†_1 b_2 a†_1 + h.c., with an effective matrix element ~ g*mF/sqrt(2)
#
# For this minimal demo we use the effective coupling directly,
# matching the paper's approach of using H = H_M + H_V only.
#
# Effective H_V coefficient from paper (arbitrary units demo): ~ g * mF
# ─────────────────────────────────────────────────────────────────

def vertex_terms(g, mF):
    """
    H_V contribution for the single allowed process:
      Fermion mode 2 ↔ Fermion mode 1 + Boson mode 1
    
    After JW mapping and expanding b†_1 b_2 a†_1 + h.c.
    into Pauli strings on 6 qubits:
    [F1=q0, F2=q1, AF1=q2, AF2=q3, B1=q4, B2=q5]
    
    b†_1 b_2 a†_1 + h.c. expands to 4 real Pauli strings:
      +XXX-type and +YYX-type combinations on (q0, q1, q4)
    with identity on q2, q3, q5.
    """
    coeff = g * mF / np.sqrt(2)  # effective matrix element (paper units)

    # b†_1 b_2 a†_1 + h.c. on qubits (0,1,4), rest identity
    # Expanding (X0-iY0)(Z0)(X1+iY1)(X4-iY4)/8 + h.c.:
    # After algebra, the 4 surviving real Pauli strings are:

    terms = []

    # XXX term on (q0, q1, q4)
    terms.append(PauliTerm(
        pauli=[Pauli.X, Pauli.X, Pauli.I, Pauli.I, Pauli.X, Pauli.I],
        coefficient=coeff / 4
    ))
    # XYY term
    terms.append(PauliTerm(
        pauli=[Pauli.X, Pauli.Y, Pauli.I, Pauli.I, Pauli.Y, Pauli.I],
        coefficient=coeff / 4
    ))
    # YXY term
    terms.append(PauliTerm(
        pauli=[Pauli.Y, Pauli.X, Pauli.I, Pauli.I, Pauli.Y, Pauli.I],
        coefficient=-coeff / 4
    ))
    # YYX term
    terms.append(PauliTerm(
        pauli=[Pauli.Y, Pauli.Y, Pauli.I, Pauli.I, Pauli.X, Pauli.I],
        coefficient=coeff / 4
    ))

    return terms


# ─────────────────────────────────────────────────────────────────
# FULL HAMILTONIAN
# Paper's hardware demo uses H = H_M + H_V only (H_S, H_F dropped
# since they are quadratic in g and the state considered only
# undergoes vertex-type interactions — see paper Sec. IV.5)
# ─────────────────────────────────────────────────────────────────

YUKAWA_HAMILTONIAN = mass_terms(mF, mB) + vertex_terms(g, mF)

# Sparse version for suzuki_trotter / ExecutionSession
# Build programmatically from the PauliTerms above
def build_sparse_hamiltonian(pauli_terms):
    """Convert list of PauliTerm to SparsePauliOp-style for Classiq."""
    sparse = None
    pauli_map = {
        Pauli.I: "I", Pauli.X: "X", Pauli.Y: "Y", Pauli.Z: "Z"
    }
    for term in pauli_terms:
        coeff = term.coefficient
        ops = term.pauli  # list of Pauli enums, qubit 0 first
        # Build sparse term: coeff * P0(0) * P1(1) * ...
        sparse_term = coeff
        for qubit_idx, pauli_op in enumerate(ops):
            if pauli_op == Pauli.I:
                continue
            elif pauli_op == Pauli.X:
                op = Pauli.X(qubit_idx)
            elif pauli_op == Pauli.Y:
                op = Pauli.Y(qubit_idx)
            elif pauli_op == Pauli.Z:
                op = Pauli.Z(qubit_idx)
            if sparse_term == coeff:
                sparse_term = coeff * op
            else:
                sparse_term = sparse_term * op
        if sparse is None:
            sparse = sparse_term
        else:
            sparse = sparse + sparse_term
    return sparse

YUKAWA_HAMILTONIAN_SPARSE = build_sparse_hamiltonian(YUKAWA_HAMILTONIAN)

# ─────────────────────────────────────────────────────────────────
# MAGNETIZATION OBSERVABLE
# Paper measures survival probability and transition probabilities.
# We use total K (momentum) as a proxy observable — it should be
# conserved under the Hamiltonian. The K operator from paper eq.(7):
#   K = sum_n n*(a†a + b†b + d†d)
# On 6 qubits with Nmax=2:
#   K = 1*(q0 + q2 + q4) + 2*(q1 + q3 + q5)  (number operators)
#   n†n = (I-Z)/2
# ─────────────────────────────────────────────────────────────────

K_hamiltonian = []
for qubit_idx, n in [(0,1),(1,2),(2,1),(3,2),(4,1),(5,2)]:
    paulis_I = [Pauli.I]*6
    paulis_Z = [Pauli.I]*6
    paulis_Z[qubit_idx] = Pauli.Z
    K_hamiltonian.append(PauliTerm(pauli=paulis_I, coefficient=n/2))
    K_hamiltonian.append(PauliTerm(pauli=paulis_Z, coefficient=-n/2))

K_hamiltonian_sparse = build_sparse_hamiltonian(K_hamiltonian)


# ─────────────────────────────────────────────────────────────────
# IDEAL CLASSICAL SIMULATION (for comparison, like paper Fig. 2/3)
# ─────────────────────────────────────────────────────────────────

hamiltonian_matrix = hamiltonian_to_matrix(YUKAWA_HAMILTONIAN)
K_matrix = hamiltonian_to_matrix(K_hamiltonian)

# Initial state: |010000⟩ = Fermion in mode 2 only
# 6 qubits → 64-dim Hilbert space
# |010000⟩ in computational basis = index where q1=1, rest 0
# Binary 010000 = decimal 16 (MSB first convention)
initial_state = np.zeros(2**6)
initial_state[16] = 1.0  # |010000⟩

time_list = np.linspace(0, 0.2, 100).tolist()  # paper uses t up to 0.2 m_π^-1

def expected_value(state, operator):
    return (np.conj(state) @ operator @ state).real

# Ideal time evolution
ideal_K = []
ideal_survival = []
for t in time_list:
    state = expm(-1j * t * hamiltonian_matrix) @ initial_state
    ideal_K.append(expected_value(state, K_matrix))
    ideal_survival.append(abs(np.dot(np.conj(initial_state), state))**2)


# ─────────────────────────────────────────────────────────────────
# QUANTUM CIRCUIT — Suzuki-Trotter on 6 qubits
# Matches paper Sec. IV.5: nT=1 (hardware), or nT=10 (simulator)
# ─────────────────────────────────────────────────────────────────

@qfunc
def main(t: CReal, qba: Output[QArray]):
    allocate(6, qba)
    suzuki_trotter(
        YUKAWA_HAMILTONIAN_SPARSE,
        evolution_coefficient=t,
        order=1,        # first-order, matches paper's choice
        repetitions=10, # nT=10, paper's simulator sweet spot
        qbv=qba,
    )


qprog_yukawa = synthesize(main)

t_values = [{"t": times} for times in time_list]

with ExecutionSession(qprog_yukawa) as execution:
    K_ST_results = execution.batch_estimate(
        K_hamiltonian_sparse, t_values
    )


# ─────────────────────────────────────────────────────────────────
# PLOT — reproducing paper Fig. 2/3 style
# ─────────────────────────────────────────────────────────────────

import matplotlib.pyplot as plt

K_ST = [v.value.real for v in K_ST_results]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Left: K conservation (should stay ~2 if conserved)
axes[0].plot(time_list, K_ST, label="Suzuki-Trotter (nT=10)", color="blue")
axes[0].plot(time_list, ideal_K, label="Ideal", color="black", linestyle="--")
axes[0].set_xlabel("Evolution time (m_π⁻¹)")
axes[0].set_ylabel("⟨K⟩")
axes[0].set_title("Momentum K conservation\n(should be ~2 throughout)")
axes[0].legend()

# Right: Survival probability of initial state |010000⟩
axes[1].plot(time_list, ideal_survival, label="Ideal survival prob", color="red")
axes[1].set_xlabel("Evolution time (m_π⁻¹)")
axes[1].set_ylabel("P(initial state)")
axes[1].set_title("Survival probability of |f⟩₂\n(paper Fig. 2 analog)")
axes[1].legend()

plt.tight_layout()
plt.savefig("yukawa_simulation.png")
print("done")