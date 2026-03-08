# quantum_toolbox.py
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator # The reliable simulator
import math

def run_quantum_growth(qc):
    """The engine that translates quantum gates into blueprint logic."""
    # Build the required gates (invisible architecture)
    qc.measure_all()
    
    # We only need 1 shot to get one collapsed growth strategy.
    # SHARED_BACKEND logic from earlier can be here if pre-loaded for speed!
    result = AerSimulator().run(qc, shots=1).result()
    counts = result.get_counts()
    
    # Get the raw 4-bit string (e.g., '1011')
    raw_bits = list(counts.keys())[0]
    
    # PARAMETER MAPPING:
    # We use the bits to influence the geometric growth
    # Bits 0-1 determine 'Chaos factor' / growth vector strategy
    growth_strategy = int(raw_bits[0:2], 2)
    # Bits 2-3 determine 'Aesthetic style' / colors
    style_code = int(raw_bits[2:4], 2)
    
    return {
        "growth_strategy": growth_strategy,
        "style_code": style_code,
        "raw_quantum_state": raw_bits
    }

# The 'Synth' / Toolbox of choices
def get_h_chaos_blueprint():
    """Chaos: Pure superposition of all strategies."""
    qc = QuantumCircuit(4)
    qc.h(range(4))
    return run_quantum_growth(qc)

def get_cx_entangled_blueprint():
    """Entanglement: Growth vector is entangled with color choice."""
    qc = QuantumCircuit(4)
    qc.h([0, 2])
    qc.cx(0, 1) # Entangle 0 and 1
    qc.cx(2, 3) # Entangle 2 and 3
    return run_quantum_growth(qc)

def get_ry_biased_blueprint():
    """Rotation: Favors one specific strategy and color scheme."""
    qc = QuantumCircuit(4)
    qc.ry(math.pi / 3, range(4))
    return run_quantum_growth(qc)