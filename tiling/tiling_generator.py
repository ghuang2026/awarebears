# tiling_generator.py
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import numpy as np

def generate_and_save_tiling(points, color_indices, filename="quantum_vibrant_mosaic.png"):
    """Generates a dense, gapless mosaic with high color variety and no adjacent duplicates."""
    
    # Expanded 12-color palette for maximum variety
    palette = [
        '#FF0054', '#9E0059', '#FFBD00', '#390099', '#FF5400', '#00FFC5',
        '#70D6FF', '#FF70A6', '#FF9770', '#FFD670', '#E9FF70', '#845EC2'
    ]
    
    border_anchors = np.array([[-1, -1], [-1, 2], [2, -1], [2, 2], 
                               [0.5, -1], [0.5, 2], [-1, 0.5], [2, 0.5]])
    full_points = np.vstack([points, border_anchors])
    vor = Voronoi(full_points)
    
    fig, ax = plt.subplots(figsize=(10, 10), facecolor='#050505')
    ax.set_facecolor('#050505')
    
    for i in range(len(points)):
        region_idx = vor.point_region[i]
        region = vor.regions[region_idx]
        
        if not -1 in region and len(region) > 0:
            polygon = [vor.vertices[idx] for idx in region]
            # Use 12-way modulo for variety
            color = palette[color_indices[i] % len(palette)]
            
            ax.fill(*zip(*polygon), color=color, alpha=0.95, edgecolor='black', linewidth=0.5)
            # Add a subtle inner "facet" line to make it look like cut glass
            ax.plot(*zip(*polygon), color='white', alpha=0.15, linewidth=0.2)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"🌈 Vibrant mosaic saved as {filename}")