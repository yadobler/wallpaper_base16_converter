from PIL import Image
import numpy as np

def hex_to_rgb(hex_str):
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def parse_base16_conf(filepath):
    palette = []
    background = (0, 0, 0)  # fallback
#!/usr/bin/env python3
import argparse
from PIL import Image
import numpy as np

def hex_to_rgb(hex_str):
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def parse_base16_conf(filepath):
    palette = []
    background = (0, 0, 0)  # default fallback
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('$color') and '=' in line:
                _, hex_value = line.split('=')
                palette.append(hex_to_rgb(hex_value.strip()))
            elif line.startswith('$background='):
                _, hex_value = line.split('=')
                background = hex_to_rgb(hex_value.strip())
    return palette[:16], background

def brightness(pixel):
    return 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]

def quantize_to_base16_with_background(image_path, palette, background, output_path, threshold=None):
    img = Image.open(image_path).convert("RGB")
    data = np.array(img)
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
    quantized_img = quantized_pixels.reshape(shape)
    Image.fromarray(quantized_img).save(output_path)
    print(f"Saved quantized image to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Quantize image to Base16 palette with optional dark pixel collapsing.")
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("conf", help="Path to Base16 .conf palette")
    parser.add_argument("output", help="Path to save output image")
    parser.add_argument("--threshold", type=int, default=None, help="Collapse pixels with brightness below this to $background (0-255)")

    args = parser.parse_args()

    palette, background = parse_base16_conf(args.conf)
    quantize_to_base16_with_background(args.image, palette, background, args.output, args.threshold)

if __name__ == "__main__":
    main()
