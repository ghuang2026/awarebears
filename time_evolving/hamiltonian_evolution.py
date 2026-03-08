# hamiltonian_evolution.py
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
import numpy as np

def get_quantum_state_at_time(t):
    """
    Simulates a very slow, low-energy Hamiltonian for organic drifting.
    """
    # Using 6 qubits for a nice balance of complexity and speed
    qc = QuantumCircuit(6)
    
    # 1. Starting 'Seed' (Organized but not empty)
    qc.ry(np.pi/6, range(6))
    
    # 2. Ultra-Slow Evolution
    # We use very small coefficients (0.02) to keep the 'energy' low.
    energy_scale = 0.02
    for i in range(6):
        qc.rx(t * energy_scale * (1.0 + i*0.05), i)
        qc.rz(t * energy_scale * 0.3, i)
        
    # Gentle Entanglement (Slowly changes the shape of the cells)
    for i in range(5):
        qc.rzz(t * energy_scale * 0.1, i, i+1)
        
    probs = Statevector(qc).probabilities()
    
    # 3. Generating Organic Points
    points = []
    num_points = 45 # High density but clean
    
    for i in range(num_points):
        # We use the probability values as 'offsets' from a fixed grid.
        # This keeps the overall structure stable while the edges drift.
        grid_x = (i % 7) / 6.0
        grid_y = (i // 7) / 6.0
        
        # The 'Quantum Drift' factor
        # We pull from the 64-length probability vector (2^6 = 64)
        drift_x = probs[i % 64] * 2.5
        drift_y = probs[(i + 10) % 64] * 2.5
        
        # Combine grid + drift for a 'constrained' organic look
        x = (grid_x + drift_x) % 1.0
        y = (grid_y + drift_y) % 1.0
        points.append([x, y])
    
    # Smooth, slow color transitions
    color_indices = [(int((probs[i % 64] * 200) + (t * 0.1)) % 12) for i in range(num_points)]
    
    return np.array(points), color_indices