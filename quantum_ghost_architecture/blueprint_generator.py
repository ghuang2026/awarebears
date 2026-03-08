# blueprint_generator.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

# Room definitions: (label, width, height) in grid units (1 unit ≈ 1 meter)
ROOM_DEFINITIONS = [
    ("LIVING RM",  5, 4),
    ("KITCHEN",    4, 3),
    ("BEDROOM",    4, 4),
    ("DINING",     4, 3),
    ("BATHROOM",   2, 3),
    ("BEDROOM 2",  3, 4),
    ("STUDY",      3, 3),
    ("HALLWAY",    5, 1),
    ("LAUNDRY",    2, 2),
    ("ENTRY",      3, 2),
    ("GARAGE",     5, 4),
    ("PATIO",      4, 3),
]


# ── Geometry ──────────────────────────────────────────────────────────────────

def rects_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    """True if two rectangles strictly overlap (shared edge is allowed)."""
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def candidates_for(rx, ry, rw, rh, new_w, new_h):
    """All flush-adjacent candidate positions for a new room next to (rx,ry,rw,rh)."""
    cands = []
    for dy in range(-(new_h - 1), rh):
        cands.append((rx + rw,       ry + dy))  # right wall
        cands.append((rx - new_w,    ry + dy))  # left wall
    for dx in range(-(new_w - 1), rw):
        cands.append((rx + dx, ry + rh))        # top wall
        cands.append((rx + dx, ry - new_h))     # bottom wall
    return cands


def find_position(placed, new_w, new_h, rng, growth_strategy, forced_adjacent=None):
    """
    Return (x, y) for a new room flush against the existing layout.
    If forced_adjacent is a (x,y,w,h) tuple, candidates come only from that room.
    Collision detection always uses the full placed list.
    """
    no_overlap = lambda nx, ny: not any(
        rects_overlap(nx, ny, new_w, new_h, px, py, pw, ph) for px, py, pw, ph in placed
    )

    if forced_adjacent is not None:
        cands = candidates_for(*forced_adjacent, new_w, new_h)
        rng.shuffle(cands)
        for nx, ny in cands:
            if no_overlap(nx, ny):
                return (nx, ny)
        return None

    n = len(placed)
    if growth_strategy == 0:
        order = list(range(n)); rng.shuffle(order)   # Chaos: any room
    elif growth_strategy == 1:
        order = list(range(n - 1, -1, -1))           # Columnar: most recent first
    elif growth_strategy == 2:
        order = list(range(n))                        # Radial: earliest first
    else:
        order = [0] + list(range(n - 1, 0, -1))      # Clustered: first then latest

    seen = set()
    for i in order:
        for nx, ny in candidates_for(*placed[i], new_w, new_h):
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                if no_overlap(nx, ny):
                    return (nx, ny)
    return None


# ── Main entry ────────────────────────────────────────────────────────────────

def draw_blueprint(params):
    growth_strategy = params["growth_strategy"]
    style_code      = params["style_code"]
    raw_bits        = params["raw_quantum_state"]
    entangled_pairs = params.get("entangled_pairs") or []
    seed            = int(raw_bits, 2)
    rng             = random.Random(seed)

    styles = {
        0: {"name": "Crystal Quartz", "edge": "#00f5d4", "fill": "#001e2b", "bg": "#000d14", "text": "#7fffd4"},
        1: {"name": "React Steel",    "edge": "#5bc8fb", "fill": "#011627", "bg": "#010d1a", "text": "#aee9fb"},
        2: {"name": "Synth Amber",    "edge": "#fee440", "fill": "#15100a", "bg": "#0a0800", "text": "#ffe88a"},
        3: {"name": "Bio-Glow",       "edge": "#f15bb5", "fill": "#1a0010", "bg": "#0d0008", "text": "#f9a8d4"},
    }
    theme = styles[style_code]

    # Build partner lookup
    partner_map = {}
    for a, b in entangled_pairs:
        partner_map[a] = b
        partner_map[b] = a

    # Shuffle rooms, keeping entangled pairs consecutive so the partner
    # is placed immediately after its counterpart (enabling forced adjacency)
    room_defs = ROOM_DEFINITIONS[:]
    rng.shuffle(room_defs)
    reordered, seen_labels = [], set()
    for room in room_defs:
        label = room[0]
        if label in seen_labels:
            continue
        reordered.append(room)
        seen_labels.add(label)
        partner = partner_map.get(label)
        if partner:
            partner_room = next((r for r in room_defs if r[0] == partner), None)
            if partner_room and partner not in seen_labels:
                reordered.append(partner_room)
                seen_labels.add(partner)

    # Place rooms
    placed         = []   # (x, y, w, h)
    room_data      = []   # (label, x, y, w, h)
    placed_by_label = {}  # label → (x, y, w, h)

    for label, w, h in reordered:
        if not placed:
            placed.append((0, 0, w, h))
            room_data.append((label, 0, 0, w, h))
            placed_by_label[label] = (0, 0, w, h)
            continue

        partner_rect = placed_by_label.get(partner_map.get(label))

        if partner_rect is not None:
            # Force placement flush against the entangled partner
            pos = find_position(placed, w, h, rng, growth_strategy, forced_adjacent=partner_rect)
            if pos is None:   # try rotated
                pos = find_position(placed, h, w, rng, growth_strategy, forced_adjacent=partner_rect)
                if pos is not None:
                    w, h = h, w
            if pos is None:   # fallback: regular placement
                pos = find_position(placed, w, h, rng, growth_strategy)
        else:
            pos = find_position(placed, w, h, rng, growth_strategy)
            if pos is None:
                pos = find_position(placed, h, w, rng, growth_strategy)
                if pos is not None:
                    w, h = h, w

        if pos is not None:
            nx, ny = pos
            placed.append((nx, ny, w, h))
            room_data.append((label, nx, ny, w, h))
            placed_by_label[label] = (nx, ny, w, h)

    # ── Draw ─────────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 10), facecolor=theme["bg"])
    ax.set_facecolor(theme["bg"])
    ax.set_aspect("equal")
    ax.axis("off")

    all_xs, all_ys = [], []
    entangled_labels = set(partner_map.keys())

    for label, rx, ry, rw, rh in room_data:
        is_ent = label in entangled_labels

        # Outer glow
        ax.add_patch(patches.Rectangle(
            (rx, ry), rw, rh, facecolor="none",
            edgecolor=theme["edge"], linewidth=10, alpha=0.07, zorder=1
        ))
        # Mid glow (brighter for entangled rooms)
        ax.add_patch(patches.Rectangle(
            (rx, ry), rw, rh, facecolor="none",
            edgecolor=theme["edge"], linewidth=4, alpha=0.30 if is_ent else 0.15, zorder=2
        ))
        # Dark fill
        ax.add_patch(patches.Rectangle(
            (rx, ry), rw, rh, facecolor=theme["fill"], edgecolor="none", zorder=2
        ))
        # Neon border (slightly thicker for entangled)
        ax.add_patch(patches.Rectangle(
            (rx, ry), rw, rh, facecolor="none",
            edgecolor=theme["edge"], linewidth=2.5 if is_ent else 2.0, alpha=0.92, zorder=3
        ))

        # Labels
        cx, cy = rx + rw / 2, ry + rh / 2
        if rh < 1.5:
            ax.text(cx, cy, f"{label}  {rw}m×{rh}m",
                    ha="center", va="center", fontsize=7, weight="bold",
                    color=theme["text"], family="monospace", zorder=4)
        else:
            ax.text(cx, cy + 0.25, label,
                    ha="center", va="center", fontsize=8, weight="bold",
                    color=theme["text"], family="monospace", zorder=4)
            ax.text(cx, cy - 0.30, f"{rw}m × {rh}m",
                    ha="center", va="center", fontsize=6.5,
                    color=theme["text"], family="monospace", zorder=4, alpha=0.65)
            if is_ent:
                ax.text(cx, cy - 0.75, "⟨ψ⟩ ENT",
                        ha="center", va="center", fontsize=6,
                        color=theme["edge"], family="monospace", zorder=4, alpha=0.85)

        all_xs += [rx, rx + rw]
        all_ys += [ry, ry + rh]

    # Quantum bond lines between entangled room centers
    for a, b in entangled_pairs:
        ra = placed_by_label.get(a)
        rb = placed_by_label.get(b)
        if ra and rb:
            xa, ya = ra[0] + ra[2] / 2, ra[1] + ra[3] / 2
            xb, yb = rb[0] + rb[2] / 2, rb[1] + rb[3] / 2
            ax.plot([xa, xb], [ya, yb],
                    color=theme["edge"], lw=1.5, linestyle="--", alpha=0.5, zorder=5)

    # Auto-fit
    pad = 2.5
    ax.set_xlim(min(all_xs) - pad, max(all_xs) + pad)
    ax.set_ylim(min(all_ys) - pad, max(all_ys) + pad)

    strategy_names = {0: "Chaos", 1: "Columnar", 2: "Radial", 3: "Clustered"}
    plt.title(
        f"QUANTUM GHOST BLUEPRINT\n"
        f"Growth: {strategy_names[growth_strategy]}  ·  {theme['name'].upper()}  ·  |{raw_bits}⟩",
        color=theme["edge"], loc="center", pad=20,
        weight="bold", family="monospace", fontsize=12,
    )
    return fig