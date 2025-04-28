import subprocess
import sys
from pathlib import Path

# --- Configuration ---
original_script_path = Path("script.py")
input_image_path = Path("~/Pictures/Wallpaper/c9ksqyk289tz.jpg").expanduser()
config_file_path = Path("~/.config/hypr/colors.conf").expanduser()
output_dir = Path("./quantized_variations")

threshold_values = range(0, 101, 20)  
edge_strength_values = range(0, 101, 20) 

# Base filename pattern (using f-string formatting)
output_filename_pattern = "wallpaper_base16-t{t:02d}-e{e:02d}.png"
# --- End Configuration ---

# Create the output directory if it doesn't exist
output_dir.mkdir(parents=True, exist_ok=True)

# --- Check for required files ---
if not original_script_path.is_file():
    print(f"Error: Original script not found at '{original_script_path}'")
    sys.exit(1)
if not input_image_path.is_file():
    print(f"Error: Input image not found at '{input_image_path}'")
    sys.exit(1)
if not config_file_path.is_file():
    print(f"Error: Config file not found at '{config_file_path}'")
    sys.exit(1)

# Store generated image paths for the Markdown table
generated_images = {} # Using a dictionary with (t, e) tuples as keys

# --- Run the script for each combination ---
total_runs = len(threshold_values) * len(edge_strength_values)
current_run = 0
print(f"Starting batch processing for {total_runs} combinations...")

for t in threshold_values:
    generated_images[t] = {} # Initialize inner dictionary for this threshold
    for e in edge_strength_values:
        current_run += 1
        print(f"\n--- Running combination {current_run}/{total_runs} (t={t}, e={e}) ---")

        # Construct the output filename
        output_filename = output_filename_pattern.format(t=t, e=e)
        output_filepath = output_dir / output_filename

        # Build the command arguments
        command = [
            sys.executable, # Use the same python interpreter that's running this script
            str(original_script_path),
            str(input_image_path),
            str(config_file_path),
            str(output_filepath),
            "--threshold", str(t),
            "--edges", # Always include edges as per the request structure
            "--edge-strength", str(e)
        ]

        print(f"Executing: {' '.join(command)}")

        try:
            # Run the command
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print("Script executed successfully.")
            print("Output:\n", result.stdout)
            generated_images[t][e] = output_filepath # Store relative path
        except subprocess.CalledProcessError as err:
            print(f"Error running script for t={t}, e={e}:")
            print(f"Return code: {err.returncode}")
            print("Stderr:\n", err.stderr)
            generated_images[t][e] = None # Mark as failed
        except Exception as exc:
             print(f"An unexpected error occurred running script for t={t}, e={e}: {exc}")
             generated_images[t][e] = None # Mark as failed


print("\n--- Batch processing finished ---")

# --- Generate Markdown Table ---
print("\nGenerating Markdown table...")

markdown_lines = []

# Header row
header_e_values = [f"e={e}" for e in edge_strength_values]
markdown_lines.append(f"| Threshold (t) \\ Edge Strength (e) | {' | '.join(header_e_values)} |")

# Separator row
markdown_lines.append(f"|---|{'---|'*len(edge_strength_values)}")

# Data rows
for t in threshold_values:
    row_cells = [f"**t={t}**"] # Start row with threshold value
    for e in edge_strength_values:
        img_path = generated_images.get(t, {}).get(e)
        if img_path:
            relative_img_path = img_path 
            cell_content = f"![t={t}, e={e}]({relative_img_path})"
        else:
            cell_content = "Error"
        row_cells.append(cell_content)
    markdown_lines.append(f"| {' | '.join(row_cells)} |")

markdown_output = "\n".join(markdown_lines)

# --- Output Markdown ---
print("\n--- Generated Markdown Table ---")
print(markdown_output)

markdown_file_path = Path("./results_table.md")
try:
    with open(markdown_file_path, 'w') as f:
        f.write(markdown_output)
    print(f"\nMarkdown table also saved to '{markdown_file_path}'")
except IOError as e:
    print(f"\nWarning: Could not save Markdown table to file: {e}")
