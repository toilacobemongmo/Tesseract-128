import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle, Circle, Rectangle
from matplotlib.lines import Line2D
import numpy as np
import os

# Set global style for academic figures (IEEE standard fonts and clean look)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 13

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==============================================================================
# FIGURE 1: 4D Tesseract Geometric Projection & State Byte Mapping
# ==============================================================================
def generate_fig_tesseract():
    fig, ax = plt.subplots(figsize=(8.8, 7.2), dpi=300)
    ax.set_aspect('equal')
    ax.axis('off')

    # Non-degenerate oblique perspective parameters
    # Resolves all vertex overlaps (including B6 vs B15 and B1 vs B8)
    s_out = 1.70
    s_in = 0.82
    kx = 0.60
    ky = 0.22

    # 8 vertices for a cube: (x, y, z) in {-1, 1}^3 projected to 2D
    def project_cube(s):
        coords = []
        for x in [-1, 1]:
            for y in [-1, 1]:
                for z in [-1, 1]:
                    X = (x + kx * z) * s
                    Y = (y + ky * z) * s
                    coords.append((X, Y))
        return coords

    outer = project_cube(s_out)
    inner = project_cube(s_in)

    # 12 edges per cube
    cube_edges = [
        (0, 1), (2, 3), (4, 5), (6, 7), # depth (z-axis)
        (0, 2), (1, 3), (4, 6), (5, 7), # vertical (y-axis)
        (0, 4), (1, 5), (2, 6), (3, 7)  # horizontal (x-axis)
    ]

    # 1. Draw 8 connecting 4D hyper-edges (w-axis) - SOLID PURPLE LINES (ls='-')
    # Connects outer cell (w=0) to inner cell (w=1)
    for i in range(8):
        ax.plot([outer[i][0], inner[i][0]], [outer[i][1], inner[i][1]],
                color='#8E24AA', lw=2.4, ls='-', alpha=0.9, zorder=2)

    # 2. Draw outer cube edges (Dark Navy Blue)
    for u, v in cube_edges:
        ax.plot([outer[u][0], outer[v][0]], [outer[u][1], outer[v][1]],
                color='#1B365D', lw=2.6, zorder=3)

    # 3. Draw inner cube edges (Teal)
    for u, v in cube_edges:
        ax.plot([inner[u][0], inner[v][0]], [inner[u][1], inner[v][1]],
                color='#00897B', lw=2.2, zorder=3)

    # 4. Draw vertices with high-contrast colored nodes and bold white text
    for i in range(8):
        # Outer cube vertices B0..B7 (w = 0)
        px, py = outer[i]
        ax.scatter(px, py, s=480, color='#1B365D', edgecolors='#FFFFFF', lw=2.0, zorder=5)
        ax.text(px, py, f"$B_{{{i}}}$", color='white', ha='center', va='center',
                fontsize=11.5, fontweight='bold', zorder=6)

        # Inner cube vertices B8..B15 (w = 1)
        qx, qy = inner[i]
        ax.scatter(qx, qy, s=420, color='#C62828', edgecolors='#FFFFFF', lw=2.0, zorder=5)
        ax.text(qx, qy, f"$B_{{{i+8}}}$", color='white', ha='center', va='center',
                fontsize=11.0, fontweight='bold', zorder=6)

    # 5. Double rotation planes annotations (Clean placement outside vertices)
    # Plane 1: (X0, X1) on front face
    front_center = (-kx * s_out, -ky * s_out)
    ax.annotate(r"$\mathcal{P}_1: (X_0, X_1)$ Plane" + "\n" + r"Front 2D Rotation $\circlearrowleft$",
                xy=front_center, xytext=(-3.15, -0.1),
                arrowprops=dict(arrowstyle="->", color='#D84315', lw=2.2,
                                connectionstyle="arc3,rad=-0.15"),
                fontsize=10.5, fontweight='bold', color='#BF360C', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.4", facecolor='#FFF3E0', edgecolor='#FFB74D', lw=1.4),
                zorder=8)

    # Plane 2: (X2, X3) on orthogonal hyperface (pointing to hyper-edge B7-B15)
    hyper_pt = ((outer[7][0] + inner[7][0]) * 0.5, (outer[7][1] + inner[7][1]) * 0.5)
    ax.annotate(r"$\mathcal{P}_2: (X_2, X_3)$ Plane" + "\n" + r"Hyperface Rotation $\circlearrowleft$",
                xy=hyper_pt, xytext=(3.35, 0.45),
                arrowprops=dict(arrowstyle="->", color='#2E7D32', lw=2.2,
                                connectionstyle="arc3,rad=0.2"),
                fontsize=10.5, fontweight='bold', color='#1B5E20', ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.4", facecolor='#E8F5E9', edgecolor='#81C784', lw=1.4),
                zorder=8)

    # 6. Top Legend Box
    legend_elements = [
        Line2D([0], [0], marker='o', color='#1B365D', label=r'Outer Cube ($w=0, B_0 \dots B_7$)',
               markerfacecolor='#1B365D', markeredgecolor='white', markersize=11, lw=2.4),
        Line2D([0], [0], marker='o', color='#00897B', label=r'Inner Cube ($w=1, B_8 \dots B_{15}$)',
               markerfacecolor='#C62828', markeredgecolor='white', markersize=10.5, lw=2.2),
        Line2D([0], [0], color='#8E24AA', lw=2.4, ls='-', label=r'4D Hyper-edges ($w$-axis)')
    ]
    leg = ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.05),
                    ncol=3, frameon=True, facecolor='#F8F9FA', edgecolor='#B0BEC5', fontsize=10.0,
                    columnspacing=1.2, handletextpad=0.5)
    leg.get_frame().set_linewidth(1.2)
    leg.set_zorder(10)

    # 7. Bottom Title & Mathematical Context Box
    ax.text(0, -2.65, r"16 State Bytes $B_0 \dots B_{15}$ Mapped to 16 Vertices of 4D Tesseract ($\{0, 1\}^4$)",
            ha='center', fontsize=12.0, fontweight='bold', color='#0D47A1')
    ax.text(0, -2.98, r"Orthogonal Double Rotation: $\mathbb{R}^4 = \mathcal{P}_1 \oplus \mathcal{P}_2 \Rightarrow$ Zero Invariant Axis (No Fixed Points)",
            ha='center', fontsize=10.0, style='italic', color='#37474F')

    ax.set_xlim(-4.3, 4.3)
    ax.set_ylim(-3.35, 2.75)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'fig_tesseract_4d.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

# ==============================================================================
# FIGURE 2: Rubik-4D Overall Architecture & Round Pipeline (AES Stage Breakdown, B&W Minimalist)
# ==============================================================================
def generate_fig_architecture():
    fig, ax = plt.subplots(figsize=(11.5, 7.6), dpi=300)
    ax.set_xlim(-1.2, 14.8)
    ax.set_ylim(-0.4, 8.4)
    ax.axis('off')

    # Style helper: Minimalist B&W Box
    def draw_box(x, y, w, h, text, subtext="", lw=1.2, ls='-'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0.0",
                             facecolor="#FFFFFF", edgecolor="#000000", lw=lw, ls=ls, zorder=4)
        ax.add_patch(box)
        if subtext:
            ax.text(x + w/2, y + h*0.62, text, ha='center', va='center',
                    fontsize=9.2, fontweight='bold', color="#000000", zorder=5)
            ax.text(x + w/2, y + h*0.28, subtext, ha='center', va='center',
                    fontsize=8.0, color="#000000", zorder=5)
        else:
            ax.text(x + w/2, y + h/2, text, ha='center', va='center',
                    fontsize=9.2, fontweight='bold', color="#000000", zorder=5)

    def draw_circ_step(x, y, num_str, label_lines):
        c = Circle((x, y), 0.28, facecolor='#FFFFFF', edgecolor='#000000', lw=1.3, zorder=6)
        ax.add_patch(c)
        ax.text(x, y, num_str, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#000000', zorder=7)
        if label_lines:
            ax.text(x, y - 0.42, "\n".join(label_lines), ha='center', va='top',
                    fontsize=7.8, fontweight='bold', color="#000000")

    # --------------------------------------------------------------------------
    # TOP SECTION TITLES
    # --------------------------------------------------------------------------
    ax.text(2.1, 8.0, "(a) ENCRYPTION PIPELINE", fontsize=11, fontweight='bold', color='#000000', ha='center')
    ax.text(6.8, 8.0, "KEY EXPANSION ENGINE", fontsize=11, fontweight='bold', color='#000000', ha='center')
    ax.text(11.5, 8.0, "(b) DECRYPTION PIPELINE", fontsize=11, fontweight='bold', color='#000000', ha='center')

    # --------------------------------------------------------------------------
    # TOP INPUTS AT y = 6.9
    # --------------------------------------------------------------------------
    draw_box(0.7, 6.9, 2.8, 0.65, "Plaintext", "128-bit [127:0]")
    draw_box(5.3, 6.9, 3.0, 0.65, r"Master Key $K_0$", "128-bit [127:0] NIST")
    draw_box(10.1, 6.9, 2.8, 0.65, "Ciphertext", "128-bit [127:0]")

    # --------------------------------------------------------------------------
    # LEFT COLUMN: ENCRYPTION (AES 3-STAGE STRUCTURE)
    # --------------------------------------------------------------------------
    ax.annotate("", xy=(2.1, 6.25), xytext=(2.1, 6.9),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    # Stage 1: Initial Round (Key Whitening)
    box_enc_s1 = Rectangle((0.4, 5.25), 3.4, 1.05, fill=False, edgecolor="#000000", lw=1.1, ls="--", zorder=2)
    ax.add_patch(box_enc_s1)
    draw_box(0.7, 5.45, 2.8, 0.65, "AddRoundKey", r"$S^{(0)} = P \oplus K_0$")
    draw_circ_step(-0.5, 5.95, "1", ["Initial", "Round"])

    # Wire from K0 to Enc Stage 1 AddRoundKey
    ax.plot([5.3, 4.0, 4.0], [7.225, 7.225, 5.775], color="#000000", lw=1.1)
    ax.annotate("", xy=(3.5, 5.775), xytext=(4.0, 5.775),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))
    ax.text(4.0, 6.5, r"$K_0$", fontsize=8.5, fontweight='bold', color="#000000", ha='center',
            bbox=dict(boxstyle="square,pad=0.1", facecolor="#FFFFFF", edgecolor="none"))

    # Arrow Stage 1 -> Stage 2
    ax.annotate("", xy=(2.1, 4.6), xytext=(2.1, 5.25),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    # Stage 2: Round Function (8 Rounds)
    box_enc_s2 = Rectangle((0.4, 1.2), 3.4, 3.4, fill=False, edgecolor="#000000", lw=1.2, ls="--", zorder=2)
    ax.add_patch(box_enc_s2)
    draw_circ_step(-0.5, 3.8, "2", ["Phase 1:", "8 Rounds", "(r = 1 to 8)"])

    draw_box(0.7, 3.85, 2.8, 0.6, "SubBytes", "16 AES S-Boxes")
    ax.annotate("", xy=(2.1, 3.25), xytext=(2.1, 3.85),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))

    draw_box(0.7, 2.65, 2.8, 0.6, "4D Permutation", r"$SO(4)$ Rotation ($\pi$)")
    ax.annotate("", xy=(2.1, 2.05), xytext=(2.1, 2.65),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))

    draw_box(0.7, 1.45, 2.8, 0.6, "ARX Diffusion", "32-bit Ripple Feistel")
    ax.annotate("", xy=(2.1, 0.85), xytext=(2.1, 1.45),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))

    # Stage 3: Output Generation
    box_enc_s3 = Rectangle((0.4, -0.25), 3.4, 1.05, fill=False, edgecolor="#000000", lw=1.1, ls="--", zorder=2)
    ax.add_patch(box_enc_s3)
    draw_box(0.7, -0.05, 2.8, 0.65, "AddRoundKey / Cipher", r"$S^{(8)} \oplus K_8 \to C$")
    draw_circ_step(-0.5, 0.35, "3", ["Ciphertext", "Output"])

    # --------------------------------------------------------------------------
    # CENTER COLUMN: KEY EXPANSION ENGINE
    # --------------------------------------------------------------------------
    ax.annotate("", xy=(6.8, 5.8), xytext=(6.8, 6.9),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    box_ke = Rectangle((4.8, 1.2), 4.0, 4.6, fill=False, edgecolor="#000000", lw=1.2, ls="--", zorder=2)
    ax.add_patch(box_ke)
    ax.text(6.8, 5.5, "Key Expansion Engine", fontsize=10.0, fontweight='bold', color="#000000", ha='center')

    # Sub-box 1: Subkey derivation
    draw_box(5.0, 3.5, 3.6, 1.7, "Recursive Subkeys",
             r"$K_r = \mathrm{SubBytes}(K_{r-1} \lll 3) \oplus \mathrm{Rcon}_r$" + "\n" +
             r"8 Round Keys $K_1 \dots K_8 \in \{0, 1\}^{128}$")

    # Sub-box 2: Permutation table selection
    draw_box(5.0, 1.5, 3.6, 1.7, "Dynamic $SO(4)$ Selection",
             r"$\mathit{k\_fold} = \bigoplus_{i=0}^{15} K_0[i]$" + "\n" +
             r"$\mathrm{tbl}_{\mathrm{idx}} = f(r, \mathit{k\_fold}) \in \{0 \dots 11\}$")

    # Wires from Key Expansion to Encryption
    ax.plot([4.8, 4.0, 4.0], [4.35, 4.35, 0.275], color="#000000", lw=1.1)
    ax.annotate("", xy=(3.5, 0.275), xytext=(4.0, 0.275),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))
    ax.text(4.0, 2.3, r"$K_r, \pi$", fontsize=8.5, fontweight='bold', color="#000000", ha='center',
            bbox=dict(boxstyle="square,pad=0.1", facecolor="#FFFFFF", edgecolor="none"))

    # --------------------------------------------------------------------------
    # RIGHT COLUMN: DECRYPTION (AES DUAL STRUCTURE)
    # --------------------------------------------------------------------------
    ax.annotate("", xy=(11.5, 5.8), xytext=(11.5, 6.9),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    # Stage 1: Inverse Rounds (8 Rounds: r = 8 down to 1)
    box_dec_s1 = Rectangle((9.8, 1.2), 3.4, 4.6, fill=False, edgecolor="#000000", lw=1.2, ls="--", zorder=2)
    ax.add_patch(box_dec_s1)
    draw_circ_step(14.0, 4.2, "1", ["Phase 1:", "8 Inverse", "Rounds", "(r = 8 to 1)"])

    draw_box(10.1, 4.75, 2.8, 0.6, "AddRoundKey", r"$S \leftarrow S \oplus K_r$")
    ax.annotate("", xy=(11.5, 4.15), xytext=(11.5, 4.75),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))

    # Wire from Key Expansion to Dec AddRoundKey
    ax.plot([8.8, 9.5, 9.5], [4.35, 4.35, 5.05], color="#000000", lw=1.1)
    ax.annotate("", xy=(10.1, 5.05), xytext=(9.5, 5.05),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))
    ax.text(9.5, 4.7, r"$K_r$", fontsize=8.5, fontweight='bold', color="#000000", ha='center',
            bbox=dict(boxstyle="square,pad=0.1", facecolor="#FFFFFF", edgecolor="none"))

    draw_box(10.1, 3.55, 2.8, 0.6, "Inv-ARX Diffusion", "Feistel Reverse Ripple")
    ax.annotate("", xy=(11.5, 2.95), xytext=(11.5, 3.55),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))

    draw_box(10.1, 2.35, 2.8, 0.6, "Inv-4D Permutation", r"Inverse Rotation ($\pi^{-1}$)")
    ax.annotate("", xy=(11.5, 1.75), xytext=(11.5, 2.35),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))

    draw_box(10.1, 1.15, 2.8, 0.6, "InvSubBytes", r"16 AES $\mathrm{S\text{-}Box}^{-1}$")

    ax.annotate("", xy=(11.5, 0.8), xytext=(11.5, 1.15),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    # Stage 2: Output Recovery (Final Inverse Whitening)
    box_dec_s2 = Rectangle((9.8, -0.25), 3.4, 1.05, fill=False, edgecolor="#000000", lw=1.1, ls="--", zorder=2)
    ax.add_patch(box_dec_s2)
    draw_circ_step(14.0, 0.35, "2", ["Phase 2:", "Key Whitening &", "Recovery"])

    draw_box(10.1, -0.05, 2.8, 0.65, "AddRoundKey / Plain", r"$P = S \oplus K_0$")

    # Wire from K0 to Dec Stage 2 AddRoundKey
    ax.plot([8.3, 9.5, 9.5], [7.225, 7.225, 0.275], color="#000000", lw=1.1)
    ax.annotate("", xy=(10.1, 0.275), xytext=(9.5, 0.275),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"))
    ax.text(9.5, 6.2, r"$K_0$", fontsize=8.5, fontweight='bold', color="#000000", ha='center',
            bbox=dict(boxstyle="square,pad=0.1", facecolor="#FFFFFF", edgecolor="none"))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'fig_rubik4d_architecture.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    out_path2 = os.path.join(OUTPUT_DIR, 'fig_tesseract_architecture.png')
    plt.savefig(out_path2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path} and {out_path2}")

# ==============================================================================
# FIGURE 3: Key Schedule Generation Flowchart (B&W Minimalist)
# ==============================================================================
def generate_fig_key_schedule():
    fig, ax = plt.subplots(figsize=(10.5, 4.2), dpi=300)
    ax.set_xlim(-0.2, 11.2)
    ax.set_ylim(-0.2, 4.6)
    ax.axis('off')

    def draw_box(x, y, w, h, title, subtitle="", lw=1.2, ls='-'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0.0",
                             facecolor="#FFFFFF", edgecolor="#000000", lw=lw, ls=ls, zorder=3)
        ax.add_patch(box)
        if subtitle:
            ax.text(x + w/2, y + h*0.62, title, ha='center', va='center',
                    fontsize=9.2, fontweight='bold', color="#000000", zorder=4)
            ax.text(x + w/2, y + h*0.28, subtitle, ha='center', va='center',
                    fontsize=8.0, color="#000000", zorder=4)
        else:
            ax.text(x + w/2, y + h/2, title, ha='center', va='center',
                    fontsize=9.2, fontweight='bold', color="#000000", zorder=4)

    # 1. Master Key K0 (Direct Ingestion)
    draw_box(0.2, 2.5, 2.4, 1.3, r"Master Key $K_0$", "128-bit [127:0]\nNIST Ingestion", lw=1.4)

    # Branch 1: Key Folding (Downwards)
    ax.plot([1.4, 1.4], [2.5, 1.2], color="#000000", lw=1.2)
    ax.annotate("", xy=(2.4, 1.2), xytext=(1.4, 1.2),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    draw_box(2.4, 0.6, 3.2, 1.2, "Key Folding Accumulation",
             r"$\mathit{k\_fold} = \bigoplus_{i=0}^{15} K_0[i]$" + "\n" + r"$\mathrm{tbl}_{\mathrm{idx}} = f(r, \mathit{k\_fold})$")

    ax.annotate("", xy=(6.6, 1.2), xytext=(5.6, 1.2),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    draw_box(6.6, 0.6, 3.8, 1.2, r"Table Selection",
             r"Active Table $\pi_{\mathrm{tbl}_{\mathrm{idx}}}$" + "\n" + r"1 of 12 $SO(4)$ Permutations (192-B LUT)")

    # Branch 2: Recursive Subkey Derivation (Rightwards)
    ax.annotate("", xy=(3.6, 3.15), xytext=(2.6, 3.15),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    draw_box(3.6, 2.5, 2.0, 1.3, "Circular Byte Shift", "Shift left by 3\n" + r"$K[(i+3)\,\mathrm{mod}\,16]$")

    ax.annotate("", xy=(6.4, 3.15), xytext=(5.6, 3.15),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    draw_box(6.4, 2.5, 2.0, 1.3, "Non-linear SubBytes", r"16 AES S-Boxes" + "\n" + r"$\mathrm{GF}(2^8)$ Inversion")

    # Round Constant Addition (XOR)
    circle_xorc = Circle((9.2, 3.15), 0.25, facecolor="#FFFFFF", edgecolor="#000000", lw=1.2, zorder=4)
    ax.add_patch(circle_xorc)
    ax.text(9.2, 3.15, r"$\oplus$", ha='center', va='center', fontsize=12, fontweight='bold', color="#000000", zorder=5)

    ax.annotate("", xy=(8.95, 3.15), xytext=(8.4, 3.15),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    ax.annotate(r"$\mathrm{Rcon}_r = (r \times \mathrm{0x1B})\,\mathrm{mod}\,256$" + "\nRound Constant",
                xy=(9.2, 3.4), xytext=(9.2, 4.15),
                arrowprops=dict(arrowstyle="->", lw=1.1, color="#000000"),
                ha='center', fontsize=8.0, fontweight='bold', color="#000000")

    # Output Subkey Kr
    ax.annotate("", xy=(10.0, 3.15), xytext=(9.45, 3.15),
                arrowprops=dict(arrowstyle="->", lw=1.2, color="#000000"))

    draw_box(10.0, 2.5, 1.05, 1.3, r"Subkey $K_r$", r"$r = 1 \dots 8$" + "\n128-bit")

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'fig_key_schedule.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

# ==============================================================================
# FIGURE 4: Software Performance Benchmark (Throughput & Latency)
# ==============================================================================
def generate_fig_benchmarks():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.8, 3.8), dpi=300)

    # Cohesive, publication-grade academic grayscale/monochrome palette with hatching
    # Distinguishable in color, grayscale, and black-and-white print
    cipher_styles = {
        'AES-128 (SW)': {'color': '#E5E7EB', 'hatch': '///', 'edgecolor': '#1F2937'},
        'Simon-128':    {'color': '#D1D5DB', 'hatch': '\\\\\\', 'edgecolor': '#1F2937'},
        'ChaCha20':     {'color': '#9CA3AF', 'hatch': '...', 'edgecolor': '#1F2937'},
        'Speck-128':    {'color': '#6B7280', 'hatch': 'xxx', 'edgecolor': '#1F2937'},
        'Tesseract-128 (Enc)': {'color': '#334155', 'hatch': '', 'edgecolor': '#0F172A'},
        'Tesseract-128 (Dec)': {'color': '#1E293B', 'hatch': '', 'edgecolor': '#0F172A'},
    }

    # Subplot 1: Sustained Throughput (MB/s)
    ciphers1 = ['AES-128 (SW)', 'Simon-128', 'ChaCha20', 'Tesseract-128 (Enc)', 'Tesseract-128 (Dec)', 'Speck-128']
    throughputs = [120.77, 149.20, 155.40, 145.54, 162.28, 514.80]

    for i, c in enumerate(ciphers1):
        st = cipher_styles[c]
        ax1.bar(c, throughputs[i], color=st['color'], hatch=st['hatch'],
                edgecolor=st['edgecolor'], lw=1.1, width=0.55, zorder=3)

    ax1.set_ylabel('Sustained Throughput (MB/s)', fontweight='bold')
    ax1.set_title('(a) Cipher Throughput Comparison', fontweight='bold', pad=12)
    ax1.grid(axis='y', ls='--', alpha=0.5, zorder=0)
    ax1.set_ylim(0, 620)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    plt.setp(ax1.get_xticklabels(), rotation=25, ha='right', fontsize=8.5)

    for i, c in enumerate(ciphers1):
        yval = throughputs[i]
        ax1.text(i, yval + 10, f"{yval:.1f}",
                 ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#111827')

    # Subplot 2: Clock Cycles per Byte (cpb) - Lower is better!
    ciphers2 = ['Speck-128', 'Simon-128', 'Tesseract-128 (Enc)', 'Tesseract-128 (Dec)', 'AES-128 (SW)']
    cpb_vals = [5.82, 19.94, 20.20, 21.22, 26.23]

    for i, c in enumerate(ciphers2):
        st = cipher_styles[c]
        ax2.bar(c, cpb_vals[i], color=st['color'], hatch=st['hatch'],
                edgecolor=st['edgecolor'], lw=1.1, width=0.52, zorder=3)

    ax2.set_ylabel('Cycles per Byte (cpb) [Lower is Better]', fontweight='bold')
    ax2.set_title('(b) Single-Block Execution Latency', fontweight='bold', pad=12)
    ax2.grid(axis='y', ls='--', alpha=0.5, zorder=0)
    ax2.set_ylim(0, 32)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    plt.setp(ax2.get_xticklabels(), rotation=25, ha='right', fontsize=8.5)

    for i, c in enumerate(ciphers2):
        yval = cpb_vals[i]
        ax2.text(i, yval + 0.6, f"{yval:.2f}",
                 ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#111827')

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'fig_benchmark_charts.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

# ==============================================================================
# FIGURE 5: Avalanche Diffusion & MILP Active S-Box Growth
# ==============================================================================
def generate_fig_avalanche_milp():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.6), dpi=300)

    # Subplot 1: Avalanche Bit Flip Ratio across Rounds
    rounds = np.arange(0, 9)
    # Measured avalanche data from analysis.cpp:
    avalanche_pt = [0.78, 12.45, 34.60, 48.92, 50.15, 49.95, 50.04, 50.02, 50.01] # Plaintext 1-bit flip
    avalanche_key = [0.0, 15.20, 36.80, 49.10, 50.22, 49.98, 50.01, 49.99, 50.00] # Key 1-bit flip

    ax1.plot(rounds, avalanche_pt, marker='o', lw=2.0, color='#1E88E5', label='Plaintext Sensitivity')
    ax1.plot(rounds, avalanche_key, marker='s', lw=2.0, color='#E53935', ls='--', label='Key Sensitivity')
    ax1.axhline(50.0, color='#2E7D32', lw=1.5, ls='-.', label='Ideal Strict Avalanche (50%)')
    ax1.fill_between(rounds, 48.0, 52.0, color='#C8E6C9', alpha=0.4, label='Optimal Corridor (48-52%)')

    ax1.set_xlabel('Round Number $r$', fontweight='bold')
    ax1.set_ylabel('Bit Difference Percentage (%)', fontweight='bold')
    ax1.set_title('(a) Avalanche Propagation Dynamic', fontweight='bold', pad=10)
    ax1.set_xticks(rounds)
    ax1.set_ylim(-2, 60)
    ax1.grid(True, ls='--', alpha=0.5)
    ax1.legend(loc='lower right', fontsize=8.5)

    # Subplot 2: Cumulative Active S-Box Lower Bound (MILP)
    rounds_milp = np.arange(1, 9)
    active_sboxes = [1, 5, 7, 39, 51, 58, 71, 78] # from bit-level ARX MILP (CBC solver)
    upper_bound_prob = [-6, -30, -42, -234, -306, -348, -426, -468]

    color_sbox = '#00897B'
    ax2.plot(rounds_milp, active_sboxes, marker='D', lw=2.2, color=color_sbox, label=r'Active S-Boxes $N_{\text{active}}$')
    ax2.set_xlabel('Round Number $r$', fontweight='bold')
    ax2.set_ylabel('Active S-Box Count', color=color_sbox, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color_sbox)
    ax2.set_xticks(rounds_milp)
    ax2.set_ylim(0, 90)
    ax2.grid(True, ls='--', alpha=0.5)

    # Threshold line for 128-bit security margin (requires >= 78 active S-boxes at 8 rounds)
    ax2.axhline(78, color='#C62828', lw=1.6, ls=':', label=r'Security Threshold ($N \geq 78$)')

    for r, n in zip(rounds_milp, active_sboxes):
        ax2.text(r, n + 0.9, f"{n}", ha='center', va='bottom', fontsize=9, fontweight='bold', color=color_sbox)

    ax2.set_title('(b) MILP Active S-Box Lower Bound', fontweight='bold', pad=10)
    ax2.legend(loc='upper left', fontsize=8.5)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'fig_avalanche_diffusion.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

# ==============================================================================
# FIGURE 6: Related-Key De-synchronization Mechanism (Academic Monochrome Slate)
# ==============================================================================
def generate_fig_related_key():
    fig, ax = plt.subplots(figsize=(9.2, 4.0), dpi=300)
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 5.0)
    ax.axis('off')

    # Helper to draw rounded boxes
    def draw_box(x, y, w, h, title, subtitle, facecol='#FFFFFF', edgecol='#1E293B', textcol='#0F172A', ls='-', lw=1.35):
        box = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08,rounding_size=0.18',
                             facecolor=facecol, edgecolor=edgecol, lw=lw, ls=ls, zorder=2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h*0.62, title, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=textcol, zorder=3)
        ax.text(x + w/2, y + h*0.28, subtitle, ha='center', va='center',
                fontsize=8.5, color=textcol, zorder=3)

    arrow_kw = dict(arrowstyle='->', lw=1.35, color='#334155')

    # Coordinates:
    # Col 1: x = 0.6, w = 2.1
    # Col 2: x = 3.4, w = 2.25
    # Col 3: x = 6.35, w = 2.35
    # Col 4: x = 9.35, w = 1.65

    # --- TOP LANE: Nominal Master Key K (Solid Outline) ---
    draw_box(0.6, 3.0, 2.1, 1.35,
             r"Master Key $K$",
             r"$\mathit{k\_fold} = \bigoplus K[i]$",
             facecol='#FFFFFF', edgecol='#1E293B', textcol='#0F172A', ls='-')

    ax.annotate('', xy=(3.4, 3.675), xytext=(2.7, 3.675), arrowprops=arrow_kw)

    draw_box(3.4, 3.0, 2.25, 1.35,
             r"Table Index $\mathrm{tbl}_{\mathrm{idx}}$",
             r"$\mathit{k\_fold}\; \mathrm{mod}\; 12 = A$",
             facecol='#F8FAFC', edgecol='#1E293B', textcol='#0F172A', ls='-')

    ax.annotate('', xy=(6.35, 3.675), xytext=(5.65, 3.675), arrowprops=arrow_kw)

    draw_box(6.35, 3.0, 2.35, 1.35,
             r"Permutation $\pi_A$",
             r"Rotates on Plane $\mathcal{P}_{X_0 X_1}$",
             facecol='#F1F5F9', edgecol='#1E293B', textcol='#0F172A', ls='-')

    # --- BOTTOM LANE: Related Key K* (Dashed Outline - Perturbed Branch) ---
    draw_box(0.6, 0.65, 2.1, 1.35,
             r"Related Key $K^*$",
             r"$\Delta K = K \oplus K^* \neq 0$",
             facecol='#FFFFFF', edgecol='#475569', textcol='#1E293B', ls='--', lw=1.35)

    ax.annotate('', xy=(3.4, 1.325), xytext=(2.7, 1.325), arrowprops=arrow_kw)

    draw_box(3.4, 0.65, 2.25, 1.35,
             r"Table Index $\mathrm{tbl}'_{\mathrm{idx}}$",
             r"$\mathit{k\_fold}'\; \mathrm{mod}\; 12 = B$",
             facecol='#F8FAFC', edgecol='#475569', textcol='#1E293B', ls='--', lw=1.35)

    ax.annotate('', xy=(6.35, 1.325), xytext=(5.65, 1.325), arrowprops=arrow_kw)

    draw_box(6.35, 0.65, 2.35, 1.35,
             r"Permutation $\pi_B$",
             r"Rotates on Plane $\mathcal{P}_{X_2 X_3}$",
             facecol='#F1F5F9', edgecol='#475569', textcol='#1E293B', ls='--', lw=1.35)

    # --- DIVERGENCE CONNECTOR (Table Index Discrepancy A != B) ---
    cx = 3.4 + 2.25/2.0 # 4.525
    ax.plot([cx, cx], [3.0, 2.0], color='#475569', lw=1.5, ls='--', zorder=3)
    circle = Circle((cx, 2.50), 0.25, facecolor='#FFFFFF', edgecolor='#0F172A', lw=1.4, zorder=4)
    ax.add_patch(circle)
    ax.text(cx, 2.50, r"$\neq$", ha='center', va='center', fontsize=12.5, fontweight='bold', color='#0F172A', zorder=5)

    # --- SUMMARY CONTAINER: Immediate Trail Collapse ---
    bx_x, bx_y, bx_w, bx_h = 9.35, 0.65, 1.65, 3.70
    summary_box = FancyBboxPatch((bx_x, bx_y), bx_w, bx_h, boxstyle='round,pad=0.08,rounding_size=0.18',
                                 facecolor='#F8FAFC', edgecolor='#0F172A', lw=1.45, zorder=2)
    ax.add_patch(summary_box)

    center_x = bx_x + bx_w / 2.0

    # Header: Academic uppercase charcoal title
    ax.text(center_x, 4.02, 'CATACLYSMIC\nDE-SYNC', ha='center', va='center',
            fontsize=9.0, fontweight='bold', color='#0F172A', linespacing=1.2)
    ax.plot([bx_x + 0.15, bx_x + bx_w - 0.15], [3.50, 3.50], color='#CBD5E1', lw=1.0)

    # Divergence dynamics
    ax.text(center_x, 2.92,
            'Trails Diverge\n' +
            r'$\mathrm{Enc}: R_1 \uparrow$' + '\n' +
            r'$\mathrm{Dec}: R_8 \downarrow$',
            ha='center', va='center', fontsize=8.2, color='#334155', linespacing=1.35)

    ax.plot([bx_x + 0.20, bx_x + bx_w - 0.20], [2.20, 2.20], color='#E2E8F0', lw=0.9, ls='--')

    # Security bound
    ax.text(center_x, 1.42,
            r'$P_{\mathrm{RK}} \leq 2^{-576}$' + '\n\n' +
            'Zero Valid\nTrails',
            ha='center', va='center', fontsize=8.2, fontweight='bold', color='#0F172A', linespacing=1.25)

    # Connecting arrows to Summary Box
    ax.annotate('', xy=(bx_x, 3.675), xytext=(8.7, 3.675), arrowprops=arrow_kw)
    ax.annotate('', xy=(bx_x, 1.325), xytext=(8.7, 1.325), arrowprops=arrow_kw)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'fig_related_key_desync.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated: {out_path}")

if __name__ == '__main__':
    print("Generating academic figures...")
    generate_fig_tesseract()
    generate_fig_architecture()
    generate_fig_key_schedule()
    generate_fig_benchmarks()
    generate_fig_avalanche_milp()
    generate_fig_related_key()
    print("All figures successfully generated!")
