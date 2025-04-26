import argparse
from PIL import Image, ImageFilter
import numpy as np

def hex_to_rgb(hex_str):
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def parse_base16_conf(filepath):
    palette = []
    background = (0, 0, 0)
    foreground = (255, 255, 255)
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('$color') and '=' in line:
                _, hex_value = line.split('=')
                palette.append(hex_to_rgb(hex_value.strip()))
            elif line.startswith('$background='):
                _, hex_value = line.split('=')
                background = hex_to_rgb(hex_value.strip())
            elif line.startswith('$foreground='):
                _, hex_value = line.split('=')
                foreground = hex_to_rgb(hex_value.strip())
    return palette[:16], background, foreground

def brightness(pixel):
    return 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]

def quantize_to_base16(image, palette, background, threshold=None):
    data = np.array(image)
    shape = data.shape
    palette_np = np.array(palette)
    background_np = np.array(background)

    def nearest_color(pixel):
        if threshold is not None and brightness(pixel) < threshold:
            return background_np
        distances = np.sqrt(np.sum((palette_np - pixel) ** 2, axis=1))
        return palette_np[np.argmin(distances)]

    pixels = data.reshape(-1, 3)
    quantized_pixels = np.array([nearest_color(p) for p in pixels], dtype=np.uint8)
    return Image.fromarray(quantized_pixels.reshape(shape))

def apply_foreground_edges(original_img, quantized_img, foreground_rgb, edge_strength=20):
    edges = original_img.convert("L").filter(ImageFilter.FIND_EDGES)
    edges_np = np.array(edges)
    edge_mask = edges_np > edge_strength

    quantized_np = np.array(quantized_img)
    quantized_np[edge_mask] = foreground_rgb
    return Image.fromarray(quantized_np)

def main():
    parser = argparse.ArgumentParser(description="Quantize image to Base16 palette with optional dark collapsing and edge highlighting.")
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("conf", help="Path to Base16 .conf palette")
    parser.add_argument("output", help="Path to save output image")

    parser.add_argument("--threshold", type=int, default=None,
                        help="Collapse pixels with brightness below this to $background (0-255)")
    parser.add_argument("--edges", action="store_true",
                        help="Highlight edges with $foreground color")
    parser.add_argument("--edge-strength", type=int, default=20,
                        help="Edge detection threshold for edge highlighting (default: 20)")

    args = parser.parse_args()

    # Load config and image
    palette, background, foreground = parse_base16_conf(args.conf)
    original_img = Image.open(args.image).convert("RGB")

    # Quantize with optional threshold
    quantized_img = quantize_to_base16(original_img, palette, background, args.threshold)

    # Apply edge overlay if needed
    if args.edges:
        quantized_img = apply_foreground_edges(original_img, quantized_img, foreground, args.edge_strength)

    quantized_img.save(args.output)
    print(f"Saved quantized image to {args.output}")

if __name__ == "__main__":
    main()
