import argparse
from PIL import Image, ImageFilter
import numpy as np
from tqdm import tqdm
from skimage.color import rgb2lab, lab2rgb
from scipy.spatial import distance # For efficient distance calculation

def hex_to_rgb(hex_str):
    """Converts a hex color string (like 'ffffff') to an RGB tuple (255, 255, 255)."""
    hex_str = hex_str.lstrip('#') # Allow optional '#' prefix
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def parse_base16_conf(filepath):
    """Parses a Base16 .conf file to extract palette, background, and foreground colors."""
    palette = [(0,0,0)] * 16 # Initialize with default black
    background = (0, 0, 0)
    foreground = (255, 255, 255)
    color_map = {}

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): # Skip empty lines and comments
                continue
            
            # Handle different variable formats (e.g., '$color00 = ...', 'color00="...")
            parts = line.split('=', 1)
            if len(parts) == 2:
                key = parts[0].strip().lstrip('$')
                value = parts[1].strip().strip('"').strip("'") # Remove quotes

                if key.startswith('color'):
                    try:
                        index = int(key[5:], 16) # Get index from hex like '00', '0A', '0F'
                        if 0 <= index < 16:
                             color_map[index] = hex_to_rgb(value)
                    except ValueError:
                        print(f"Warning: Could not parse color index from key '{key}'")
                elif key == 'background':
                    background = hex_to_rgb(value)
                elif key == 'foreground':
                    foreground = hex_to_rgb(value)
                # Ignore 'cursor' or other variables for this script

    # Fill the palette list using the map
    for i in range(16):
        if i in color_map:
            palette[i] = color_map[i]
        else:
             print(f"Warning: Color index {i:02X} not found in config, using black.")

    return palette, background, foreground

def quantize_to_base16(image_pil, palette_rgb, background_rgb, threshold=None):
    """
    Quantizes an image to the nearest color in the Base16 palette using LAB color space.

    Args:
        image_pil (PIL.Image): Input image in RGB mode.
        palette_rgb (list): List of 16 RGB tuples for the Base16 palette.
        background_rgb (tuple): RGB tuple for the background color.
        threshold (int, optional): Brightness threshold (0-100 for LAB's L channel).
                                    Pixels below this lightness are mapped to background. Defaults to None.

    Returns:
        numpy.ndarray: Quantized image as an RGB NumPy array (uint8).
    """
    # --- Preparation ---
    # Convert PIL image to NumPy array (float 0-1) and then to LAB
    image_np_float = np.array(image_pil) / 255.0
    image_lab = rgb2lab(image_np_float)
    height, width, _ = image_lab.shape
    
    # Reshape image data for easier processing: (num_pixels, 3)
    pixels_lab = image_lab.reshape(-1, 3)
    
    # Convert RGB palette and background to LAB
    # Need to handle them as arrays of shape (N, 3) for rgb2lab
    palette_np_rgb_float = np.array(palette_rgb) / 255.0
    palette_lab = rgb2lab(palette_np_rgb_float.reshape(-1, 1, 3)).reshape(-1, 3) # Reshape for rgb2lab

    background_np_rgb_float = np.array(background_rgb) / 255.0
    # rgb2lab expects at least a 2D array, so reshape background
    background_lab = rgb2lab(background_np_rgb_float.reshape(1, 1, 3)).flatten()
    
    # Create output array (initialized to black, will be filled)
    quantized_pixels_rgb = np.zeros((height * width, 3), dtype=np.uint8)

    pbar = tqdm(total=100, desc="Quantizing Image")

    # --- Background Masking (if threshold is set) ---
    background_mask = None
    if threshold is not None:
        # L channel is the first column (index 0) in LAB
        lightness = pixels_lab[:, 0] 
        # Threshold is given 0-255 like original image, but LAB L is 0-100. Scale it.
        # Actually, let's keep threshold relative to L channel 0-100 for clarity.
        # User should provide threshold like 10, 20 etc for LAB lightness.
        background_mask = lightness < threshold
        quantized_pixels_rgb[background_mask] = background_rgb
        pbar.update(10) # Progress update

    # --- Find Nearest Palette Color for non-background pixels ---
    # Determine which pixels need processing (either all or those not masked)
    if background_mask is not None:
        process_mask = ~background_mask
    else:
        # If no threshold, process all pixels
        process_mask = np.ones(pixels_lab.shape[0], dtype=bool)
        pbar.update(10) # Progress update (skipped background step)

    # Select the LAB pixels that need to be compared to the palette
    pixels_to_process_lab = pixels_lab[process_mask]
    
    if pixels_to_process_lab.shape[0] > 0: # Only compute if there are pixels to process
        # Calculate pairwise distances between pixels_to_process and palette colors in LAB space
        # `cdist` calculates distance between each pair of the two collections of inputs.
        # 'euclidean' is the default and correct metric here.
        distances = distance.cdist(pixels_to_process_lab, palette_lab, metric='euclidean')
        pbar.update(70) # Progress update after distance calculation
        
        # Find the index of the palette color with the minimum distance for each pixel
        nearest_indices = np.argmin(distances, axis=1)
        pbar.update(10) # Progress update after finding indices
        
        # Map these indices back to the original RGB palette colors
        nearest_colors_rgb = np.array(palette_rgb)[nearest_indices]
        
        # Assign these colors to the corresponding positions in the output array
        quantized_pixels_rgb[process_mask] = nearest_colors_rgb
        pbar.update(10) # Progress update after assignment
    else:
         pbar.update(90) # Update progress if all pixels were background

    pbar.close()
    
    # Reshape the quantized pixel array back to the original image dimensions
    quantized_image_np = quantized_pixels_rgb.reshape(height, width, 3)
    
    return quantized_image_np # Return as numpy uint8 array

def apply_foreground_edges(original_img_pil, quantized_img_np, highlight_rgb, edge_strength=20):
    """
    Detects edges in the original image and overlays them onto the quantized image
    using the specified highlight color.

    Args:
        original_img_pil (PIL.Image): The original input image (RGB).
        quantized_img_np (numpy.ndarray): The quantized image (RGB NumPy array).
        highlight_rgb (tuple): The RGB color tuple to use for highlighting edges.
        edge_strength (int): Threshold for edge detection (0-255). Higher means stronger edges needed.

    Returns:
        numpy.ndarray: Quantized image with edges highlighted (RGB NumPy array).
    """
    pbar = tqdm(total=2, desc="Highlighting Edges")

    # Step 1: Find edges on the *original* image for better detail
    # Convert original to grayscale ("L") for edge detection
    edges = original_img_pil.convert("L").filter(ImageFilter.FIND_EDGES)
    edges_np = np.array(edges)
    
    # Create a mask where edge intensity is above the threshold
    edge_mask = edges_np > edge_strength
    pbar.update(1)

    # Step 2: Apply highlight color to the quantized image using the mask
    # Make a copy to avoid modifying the input array directly if it's reused elsewhere
    output_np = quantized_img_np.copy() 
    output_np[edge_mask] = highlight_rgb
    pbar.update(1)

    pbar.close()
    return output_np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quantize image to Base16 palette with optional dark collapsing and edge highlighting.")
    parser.add_argument("image", help="Path to input image")
    parser.add_argument("conf", help="Path to Base16 .conf palette file")
    parser.add_argument("output", help="Path to save output image")

    parser.add_argument("--threshold", type=int, default=None,
                        help="Collapse pixels with LAB Lightness (L*) below this to $background (0-100, e.g., 15)")
    parser.add_argument("--edges", action="store_true",
                        help="Highlight edges with $foreground color")
    parser.add_argument("--edge-strength", type=int, default=20,
                        help="Edge detection threshold for edge highlighting (0-255, default: 20)")

    args = parser.parse_args()

    try:
        # Load config and image
        print(f"Loading Base16 config from: {args.conf}")
        palette, background, foreground = parse_base16_conf(args.conf)
        print(f"Background: {background}, Foreground: {foreground}")
        print(f"Palette Colors: {len(palette)}")
        
        print(f"Loading image: {args.image}")
        original_img = Image.open(args.image).convert("RGB")

        # Quantize (returns numpy array)
        quantized_np = quantize_to_base16(original_img, palette, background, args.threshold)

        final_output_np = quantized_np
        # Apply edge overlay if needed (works on numpy arrays)
        if args.edges:
            final_output_np = apply_foreground_edges(original_img, quantized_np, foreground, args.edge_strength)

        # Convert final numpy array to PIL Image for saving
        output_img = Image.fromarray(final_output_np) # Already uint8 RGB
        
        output_img.save(args.output)
        print(f"Saved quantized image to {args.output}")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc() # Print detailed traceback for debugging
