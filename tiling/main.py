# main.py
from quantum_optimizer import run_vqa
from tiling_generator import generate_and_save_tiling

def main():
    print("=== QUANTUM SEAMLESS MOSAIC GENERATOR ===")
    
    # 1. Optimize
    best_points, best_colors = run_vqa()
    
    # 2. Render
    generate_and_save_tiling(best_points, best_colors)
    
    print("\nCheck 'quantum_mosaic.png' for your unique, gapless tiling pattern!")

if __name__ == "__main__":
    main()