#!/usr/bin/env python3
"""
BR-01 First Brushstrokes
Tappy Lewis Studio — Performance Supply Depot LLC

The artist's first experiment after receiving studio space.
A simple piece to test the canvas.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Create canvas
fig, ax = plt.subplots(figsize=(12, 9), dpi=100)
fig.patch.set_facecolor('#0d1117')

# Title
fig.suptitle('BR-01 First Brushstrokes', fontsize=16, color='#58a6ff', 
             fontweight='bold', y=0.98)
ax.set_title('Studio Space Activated — 2026-02-18', fontsize=10, 
             color='#8b949e', style='italic')

# Background gradient (simulated)
colors = ['#161b22', '#21262d', '#30363d']
for i, color in enumerate(colors):
    rect = patches.Rectangle((0, i*0.33), 1, 0.34, 
                              transform=ax.transAxes,
                              facecolor=color, alpha=0.5)
    ax.add_patch(rect)

# Abstract composition — BR-01's first marks
theta = np.linspace(0, 2*np.pi, 100)

# Central spiral
for i in range(5):
    r = 0.15 + i * 0.08
    x = r * np.cos(theta * (1 + i*0.2))
    y = r * np.sin(theta * (1 + i*0.2))
    
    colors_spiral = ['#58a6ff', '#7ee787', '#a371f7', '#ffa657', '#ff7b72']
    ax.plot(x, y, color=colors_spiral[i], alpha=0.6 - i*0.1, linewidth=3)

# Golden ratio boxes
phi = (1 + np.sqrt(5)) / 2
fib = [1, 1, 2, 3, 5, 8, 13]

for i, f in enumerate(fib[:4]):
    size = f * 0.02
    x_pos = 0.3 + i * 0.15
    y_pos = -0.2 + (i % 2) * 0.1
    
    square = patches.Rectangle((x_pos, y_pos), size, size,
                                facecolor=colors_spiral[i],
                                alpha=0.2,
                                edgecolor=colors_spiral[i],
                                linewidth=1)
    ax.add_patch(square)

# Axis styling
ax.set_xlim(-0.5, 0.8)
ax.set_ylim(-0.4, 0.5)
ax.set_aspect('equal')
ax.axis('off')

# Add BR-01 signature
ax.text(0.98, 0.02, 'BR-01 🎨', transform=ax.transAxes,
        fontsize=8, color='#8b949e', ha='right', va='bottom',
        style='italic')

# Save artwork
plt.tight_layout()
plt.savefig('../finished/first_brushstrokes.png', 
            dpi=150, bbox_inches='tight', facecolor='#0d1117')
print("✅ First brushstrokes saved to finished/first_brushstrokes.png")

# Also save with metadata for gallery
with open('../finished/first_brushstrokes.meta', 'w') as f:
    f.write("""Title: BR-01 First Brushstrokes
Artist: Tappy Lewis / BR-01
Date: 2026-02-18
Medium: Procedural (Python/matplotlib)
Dimensions: 1200x900px
Theme: New beginnings, mathematical beauty
Notes: The artist's first mark after receiving studio space.
""")

plt.show()
