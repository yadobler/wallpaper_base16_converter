import argparse
from PIL import Image, ImageFilter
import numpy as np
from tqdm import tqdm

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

    pixels = data.reshape(-1, 3)

    pbar = tqdm(total=3, desc="Quantizing")  # 3 major steps: brightness, distance, assignment

    if threshold is not None:
        brightnesses = 0.299 * pixels[:,0] + 0.587 * pixels[:,1] + 0.114 * pixels[:,2]
        dark_mask = brightnesses < threshold
    else:
        dark_mask = np.zeros((pixels.shape[0],), dtype=bool)
    pbar.update(1)

    dists = np.sqrt(((pixels[:, None, :] - palette_np[None, :, :]) ** 2).sum(axis=2))
    nearest_palette_indices = np.argmin(dists, axis=1)
    pbar.update(1)

    quantized_pixels = palette_np[nearest_palette_indices]
    quantized_pixels[dark_mask] = background_np
    quantized_pixels = quantized_pixels.astype(np.uint8)
    pbar.update(1)

    pbar.close()
    return Image.fromarray(quantized_pixels.reshape(shape))

def apply_foreground_edges(original_img, quantized_img, foreground_rgb, edge_strength=20):
    edges = original_img.convert("L").filter(ImageFilter.FIND_EDGES)
    edges_np = np.array(edges)

    pbar = tqdm(total=2, desc="Highlighting Edges")

    edge_mask = edges_np > edge_strength
    pbar.update(1)

    quantized_np = np.array(quantized_img)
    quantized_np[edge_mask] = foreground_rgb
    pbar.update(1)

    pbar.close()
    return Image.fromarray(quantized_np)

if __name__ == "__main__":
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
