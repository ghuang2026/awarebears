# main.py
import numpy as np
from PIL import Image
import os
from hamiltonian_evolution import get_quantum_state_at_time
from tiling_generator import render_frame

def main():
    print("--- GENERATING ORGANIC QUANTUM DRIFT ---")
    
    frames = 100 # More frames = smoother movement
    max_time = 20.0 # Total time simulated
    time_steps = np.linspace(0, max_time, frames)
    
    image_filenames = []
    
    for i, t in enumerate(time_steps):
        if i % 10 == 0:
            print(f"Status: {i}/{frames} frames rendered...")
            
        points, colors = get_quantum_state_at_time(t)
        filename = render_frame(points, colors, i, t)
        
        if filename:
            image_filenames.append(filename)
            
    print("\nAssembling high-fidelity animation...")
    images = [Image.open(f) for f in image_filenames]
    
    # duration=120 is about 8 frames per second; very smooth and slow
    images[0].save('organic_quantum_drift.gif',
                   save_all=True,
                   append_images=images[1:],
                   duration=120,
                   loop=0)
                   
    for f in image_filenames:
        os.remove(f)
        
    print("✅ Complete! Open 'organic_quantum_drift.gif' to see the calm evolution.")

if __name__ == "__main__":
    main()