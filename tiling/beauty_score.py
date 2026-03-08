# beauty_score.py
import numpy as np

def calculate_cost(points, colors, vor_obj=None):
    cost = 0.0
    
    # 1. Spread Penalty (Keep the mosaic centered)
    center_of_mass = np.mean(points, axis=0)
    dist_from_center = np.linalg.norm(center_of_mass - np.array([0.5, 0.5]))
    cost += dist_from_center * 100 

    # 2. Minimum Distance (Avoid tiny slivers)
    dist_matrix = np.linalg.norm(points[:, np.newaxis] - points, axis=2)
    np.fill_diagonal(dist_matrix, np.inf)
    if np.any(np.min(dist_matrix, axis=1) < 0.02):
        cost += 150.0

    # 3. Adjacency Penalty (Avoid same-color neighbors)
    # We check the Voronoi ridge points to see which cells touch
    if vor_obj is not None:
        for point_indices in vor_obj.ridge_points:
            p1, p2 = point_indices
            # If both points are within our 50 generated points and have same color
            if p1 < len(colors) and p2 < len(colors):
                if colors[p1] == colors[p2]:
                    cost += 50.0 # Heavy penalty for color clumping
        
    return cost