# tiling_generator.py
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import numpy as np

def render_frame(points, color_indices, frame_number, t):
    """Renders a single organic frame with no labels and soft colors."""
    
    # Soft Jewel Palette: Deep, calming, and varied
    palette = [
        '#264653', '#2a9d8f', '#e9c46a', '#f4a261', '#e76f51', 
        '#6d597a', '#b56576', '#e56b6f', '#355070', '#5f0f40',
        '#9a8c98', '#4a4e69'
    ]
    
    # Anchors ensure the mosaic stays filled to the edges
    border = np.array([[-1, -1], [-1, 2], [2, -1], [2, 2], [0.5, -1], [0.5, 2], [-1, 0.5], [2, 0.5]])
    full_points = np.vstack([points, border])
    
    try:
        vor = Voronoi(full_points)
    except:
        return None
        
    fig, ax = plt.subplots(figsize=(8, 8), facecolor='#0d1b2a')
    ax.set_facecolor('#0d1b2a')
    
    # Draw the Voronoi Cells
    for i in range(len(points)):
        region_idx = vor.point_region[i]
        region = vor.regions[region_idx]
        
        if not -1 in region and len(region) > 0:
            polygon = [vor.vertices[idx] for idx in region]
            color = palette[color_indices[i] % len(palette)]
            
            # Use lower alpha and thinner edges for a 'gentle' look
            ax.fill(*zip(*polygon), color=color, alpha=0.8, edgecolor='#1b263b', linewidth=0.5)
            # Faint highlight
            ax.plot(*zip(*polygon), color='white', alpha=0.05, linewidth=0.2)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    filename = f"frame_{frame_number:03d}.png"
    plt.savefig(filename, dpi=120, bbox_inches='tight', pad_inches=0, facecolor='#0d1b2a')
    plt.close(fig)
    return filename