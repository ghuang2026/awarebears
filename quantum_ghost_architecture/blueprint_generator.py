# blueprint_generator.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math
import random

HEX_SIZE = 1.0

# Axial coordinate neighbor directions (pointy-top hexagons)
DIRECTIONS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]


def axial_to_pixel(q, r, size=HEX_SIZE):
    """Converts axial hex coordinates (q, r) to pixel (x, y) for pointy-top hexagons."""
    x = size * math.sqrt(3) * (q + r / 2.0)
    y = size * (3.0 / 2.0) * r
    return x, y


def hex_vertices(cx, cy, size=HEX_SIZE):
    """Returns the 6 corner vertices of a pointy-top hexagon centered at (cx, cy)."""
    return [
        (cx + size * math.cos(math.radians(60 * i + 30)), cy + size * math.sin(math.radians(60 * i + 30)))
        for i in range(6)
    ]


def grow_hex_cluster(seed, growth_strategy, num_rooms=14):
    """
    Grows a fully-connected cluster of hexagons with zero gaps or overlaps.
    Returns a list of (q, r) axial coordinates in growth order.

    Growth strategies (controlled by quantum bits 0-1):
      0 - Chaotic:   grow from any existing hex (sprawling)
      1 - Columnar:  always grow from the most recently added hex (snake-like branch)
      2 - Radial:    prefer growing from earlier hexes (star from center)
      3 - Clustered: alternate between first and latest (two-arm)
    """
    occupied = set()
    ordered = []

    start = (0, 0)
    occupied.add(start)
    ordered.append(start)

    rng = random.Random(seed)

    while len(ordered) < num_rooms:
        # Pick parent according to growth strategy
        if growth_strategy == 0:
            parent = rng.choice(ordered)
        elif growth_strategy == 1:
            parent = ordered[-1]
        elif growth_strategy == 2:
            parent = ordered[rng.randint(0, max(0, len(ordered) // 3))]
        else:
            parent = ordered[0] if len(ordered) % 2 == 0 else ordered[-1]

        # Try all 6 directions in random order until we find an empty cell
        dirs = DIRECTIONS[:]
        rng.shuffle(dirs)
        placed = False
        for dq, dr in dirs:
            neighbor = (parent[0] + dq, parent[1] + dr)
            if neighbor not in occupied:
                occupied.add(neighbor)
                ordered.append(neighbor)
                placed = True
                break

        # Safety fallback: if all neighbors of this parent are occupied,
        # pick any hex that still has a free neighbor
        if not placed:
            for candidate in ordered:
                for dq, dr in DIRECTIONS:
                    neighbor = (candidate[0] + dq, candidate[1] + dr)
                    if neighbor not in occupied:
                        occupied.add(neighbor)
                        ordered.append(neighbor)
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                break  # Cluster is fully surrounded (shouldn't happen for reasonable num_rooms)

    return ordered


def draw_blueprint(params):
    """Generates a cohesive neon hex-tile blueprint from quantum parameters."""
    growth_strategy = params["growth_strategy"]
    style_code = params["style_code"]
    raw_bits = params["raw_quantum_state"]
    seed = int(raw_bits, 2)

    styles = {
        0: {"name": "Crystal Quartz", "edge": "#00f5d4", "fill": "#001e2b", "bg": "#000d14"},
        1: {"name": "React Steel",    "edge": "#5bc8fb", "fill": "#011627", "bg": "#010d1a"},
        2: {"name": "Synth Amber",    "edge": "#fee440", "fill": "#15100a", "bg": "#0a0800"},
        3: {"name": "Bio-Glow",       "edge": "#f15bb5", "fill": "#1a0010", "bg": "#0d0008"},
    }
    theme = styles[style_code]

    # Broad architectural room labels
    room_labels = [
        "LIVING RM", "KITCHEN", "BATHROOM", "BEDROOM",
        "BEDROOM 2", "DINING", "STUDY", "HALLWAY",
        "LAUNDRY", "STORAGE", "GARAGE", "ENTRY",
        "PATIO", "LOFT",
    ]

    hex_positions = grow_hex_cluster(seed, growth_strategy, num_rooms=14)

    fig, ax = plt.subplots(figsize=(10, 10), facecolor=theme["bg"])
    ax.set_facecolor(theme["bg"])
    ax.set_aspect("equal")
    ax.axis("off")

    for i, (q, r) in enumerate(hex_positions):
        cx, cy = axial_to_pixel(q, r)
        verts = hex_vertices(cx, cy, size=HEX_SIZE * 0.96)  # tiny gap prevents edge bleeding

        # Dark fill
        fill = patches.Polygon(verts, closed=True, facecolor=theme["fill"], edgecolor="none", zorder=2)
        ax.add_patch(fill)

        # Outer glow (wide, very transparent)
        glow = patches.Polygon(verts, closed=True, facecolor="none",
                               edgecolor=theme["edge"], linewidth=10, alpha=0.10, zorder=1)
        ax.add_patch(glow)

        # Mid glow
        glow2 = patches.Polygon(verts, closed=True, facecolor="none",
                                edgecolor=theme["edge"], linewidth=5, alpha=0.18, zorder=2)
        ax.add_patch(glow2)

        # Sharp neon border
        border = patches.Polygon(verts, closed=True, facecolor="none",
                                 edgecolor=theme["edge"], linewidth=2.0, alpha=0.95, zorder=3)
        ax.add_patch(border)

        # Room label
        label = room_labels[i % len(room_labels)]
        ax.text(cx, cy, label, ha="center", va="center",
                fontsize=7.5, weight="bold", color=theme["edge"],
                family="monospace", zorder=4)

    # Faint quantum-bond lines between rooms in growth order
    for i in range(len(hex_positions) - 1):
        x1, y1 = axial_to_pixel(*hex_positions[i])
        x2, y2 = axial_to_pixel(*hex_positions[i + 1])
        ax.plot([x1, x2], [y1, y2],
                color=theme["edge"], alpha=0.18, linestyle="--", lw=0.8, zorder=1)

    # Auto-fit the view
    all_x = [axial_to_pixel(q, r)[0] for q, r in hex_positions]
    all_y = [axial_to_pixel(q, r)[1] for q, r in hex_positions]
    pad = HEX_SIZE * 2.5
    ax.set_xlim(min(all_x) - pad, max(all_x) + pad)
    ax.set_ylim(min(all_y) - pad, max(all_y) + pad)

    strategy_names = {0: "Chaos", 1: "Columnar", 2: "Radial", 3: "Clustered"}
    plt.title(
        f"QUANTUM GHOST BLUEPRINT\n"
        f"Growth: {strategy_names[growth_strategy]}  ·  Style: {theme['name'].upper()}  ·  |{raw_bits}⟩",
        color=theme["edge"], loc="center", pad=20,
        weight="bold", family="monospace", fontsize=12,
    )

    return fig