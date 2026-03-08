# quantum_optimizer.py
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize
from scipy.spatial import Voronoi
import numpy as np
from beauty_score import calculate_cost

def get_quantum_parameters(theta):
    qc = QuantumCircuit(8)
    for i in range(8):
        qc.ry(theta[i], i)
    for i in range(7):
        qc.cx(i, i+1)
    
    probs = Statevector(qc).probabilities()
    
    points = []
    for i in range(50):
        x = (probs[i] * 777) % 1.0
        y = (probs[i + 50] * 777) % 1.0
        points.append([x, y])
    
    # 12 discrete color options
    color_indices = [(int(p * 5000) % 12) for p in probs[:50]]
    
    return np.array(points), color_indices

def objective(theta):
    points, colors = get_quantum_parameters(theta)
    
    # Generate a temporary Voronoi to check for neighbor conflicts
    try:
        vor = Voronoi(points)
        return calculate_cost(points, colors, vor)
    except:
        return 1000 # Return high cost if geometry fails

def run_vqa():
    print("Optimizing for Color Diversity and Adjacency...")
    init_theta = np.random.rand(8) * np.pi
    res = minimize(objective, init_theta, method='COBYLA', options={'maxiter': 40})
    return get_quantum_parameters(res.x)