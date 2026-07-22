"""
Lumina App Logo Generator
Programmatically draws a high-resolution, custom cyber-neon logo for the Tauri shell.
"""

import math
import os
from PIL import Image, ImageDraw, ImageFilter

def draw_star(draw, x, y, r_outer, color):
    """Draws a sharp, geometric 4-pointed star vector."""
    r_inner = r_outer / 4.0
    points = []
    for i in range(8):
        angle = i * math.pi / 4.0
        r = r_outer if i % 2 == 0 else r_inner
        px = x + r * math.cos(angle - math.pi/2)
        py = y + r * math.sin(angle - math.pi/2)
        points.append((px, py))
    draw.polygon(points, fill=color)

def main():
    # 1. Create a transparent 512x512 base canvas
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    
    # 2. Create the neon glow layer (will be blurred)
    glow_layer = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw_glow = ImageDraw.Draw(glow_layer)
    
    # 3. Create the sharp detail layer
    sharp_layer = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    draw_sharp = ImageDraw.Draw(sharp_layer)
    
    # Color variables matching the Lumina cyber-neon theme
    cyan_glow = (6, 182, 212, 130)
    cyan_sharp = (6, 182, 212, 255)
    pink_glow = (236, 72, 153, 130)
    pink_sharp = (236, 72, 153, 255)
    white_glow = (255, 255, 255, 160)
    white_sharp = (255, 255, 255, 255)
    dark_bg = (13, 19, 35, 255)
    
    # Draw a dark glass emblem base circle (centered, radius 220)
    draw_base = ImageDraw.Draw(img)
    draw_base.ellipse((36, 36, 476, 476), fill=dark_bg, outline=(255, 255, 255, 15), width=2)
    
    # Draw outer border rings
    # Glow (thick, to be blurred)
    draw_glow.ellipse((46, 46, 466, 466), outline=cyan_glow, width=16)
    # Sharp (thin, crisp)
    draw_sharp.ellipse((46, 46, 466, 466), outline=cyan_sharp, width=4)
    
    # Draw diagonal magic wand shaft
    # Glow
    draw_glow.line((150, 362, 330, 182), fill=pink_glow, width=16)
    # Sharp
    draw_sharp.line((150, 362, 330, 182), fill=pink_sharp, width=4)
    # Wand tip highlight (white core)
    draw_sharp.ellipse((325, 177, 335, 187), fill=white_sharp)
    
    # Draw glowing stars/sparkles around the tip
    # Glow (will be blurred out nicely)
    draw_star(draw_glow, 360, 150, 48, white_glow)
    draw_star(draw_glow, 315, 120, 32, cyan_glow)
    draw_star(draw_glow, 390, 190, 24, pink_glow)
    
    # Sharp (clean, glowing core details)
    draw_star(draw_sharp, 360, 150, 24, white_sharp)
    draw_star(draw_sharp, 315, 120, 14, cyan_sharp)
    draw_star(draw_sharp, 390, 190, 10, pink_sharp)
    
    # Apply Gaussian Blur to the glow layer to simulate neon glow
    blurred_glow = glow_layer.filter(ImageFilter.GaussianBlur(radius=12))
    
    # Composite the layers: Base -> Glow -> Sharp
    img.alpha_composite(blurred_glow)
    img.alpha_composite(sharp_layer)
    
    # Save as high-resolution app_logo.png
    output_path = "app_logo.png"
    img.save(output_path, "PNG")
    print(f"[*] Generated glowing neon logo successfully as: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    main()
