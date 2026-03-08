# quantum_toolbox.py
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import math


def _run(qc):
    """Run a circuit (1 shot) and return the base parameter dict."""
    qc.measure_all()
    raw_bits = list(AerSimulator().run(qc, shots=1).result().get_counts().keys())[0]
    return {
        "growth_strategy":   int(raw_bits[0:2], 2),  # bits 0-1 → 0-3
        "style_code":        int(raw_bits[2:4], 2),  # bits 2-3 → 0-3
        "raw_quantum_state": raw_bits,
        "entangled_pairs":   None,
    }


# ── Gate circuits ─────────────────────────────────────────────────────────────

def get_h_superposition_blueprint():
    """
    H (Hadamard): All 4 qubits enter equal superposition.
    Every outcome is equally probable → maximum layout entropy.
    """
    qc = QuantumCircuit(4)
    qc.h(range(4))
    return _run(qc)


def get_x_flip_blueprint():
    """
    X (Pauli-X): Flips |0⟩ → |1⟩ on all qubits. Deterministic.
    Always produces |1111⟩ → growth strategy 3, style 3 every time.
    """
    qc = QuantumCircuit(4)
    qc.x(range(4))
    return _run(qc)


def get_cx_entangled_blueprint():
    """
    CX (CNOT): Qubits 0↔1 and 2↔3 are entangled.
    If qubit 0 collapses to |0⟩, qubit 1 MUST be |0⟩ — and vice versa.
    Only states |0000⟩, |0011⟩, |1100⟩, |1111⟩ can appear.
    In the blueprint, Kitchen↔Dining and Bedroom↔Bathroom are forced adjacent.
    """
    qc = QuantumCircuit(4)
    qc.h([0, 2])   # superpose control qubits
    qc.cx(0, 1)    # entangle pair 0 & 1
    qc.cx(2, 3)    # entangle pair 2 & 3
    params = _run(qc)
    params["entangled_pairs"] = [("KITCHEN", "DINING"), ("BEDROOM", "BATHROOM")]
    return params


def get_t_interference_blueprint():
    """
    T gate (H → T → H): Applies a 45° phase rotation e^(iπ/4) inside superposition.
    The second Hadamard converts this invisible phase into amplitude bias:
    each qubit is ~85% likely to collapse to |0⟩ → compact, low-numbered layouts.
    """
    qc = QuantumCircuit(4)
    qc.h(range(4))   # enter superposition
    qc.t(range(4))   # 45° phase rotation on |1⟩ component
    qc.h(range(4))   # interference: phase → amplitude bias
    return _run(qc)


def get_z_kickback_blueprint():
    """
    Z kickback (H → Z[0,2] → H): Z gate applied only to qubits 0 and 2.
    H·Z·H = X on those qubits → deterministic |1⟩.
    H·H = I on qubits 1 and 3 → deterministic |0⟩.
    Result is always |0101⟩. The invisible phase is revealed as a bit flip.
    """
    qc = QuantumCircuit(4)
    qc.h(range(4))   # enter superposition (Z is 'invisible' here)
    qc.z([0, 2])     # phase flip on qubits 0 and 2 only
    qc.h(range(4))   # second H: phase → observable bit flip on 0 & 2; identity on 1 & 3
    return _run(qc)


def get_ry_biased_blueprint():
    """
    RY(π/3): Rotates the Bloch vector 60° on the Y-axis.
    P(|1⟩) ≈ 25% per qubit — a continuous, tunable partial bias.
    """
    qc = QuantumCircuit(4)
    qc.ry(math.pi / 3, range(4))
    return _run(qc)