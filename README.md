# Color quantization

Matches your wallpaper to your base16 template (reverse pywal?)

## requirements

- python:

```text
numpy==2.2.5
pillow==11.2.1
scikit-image==0.25.2
scipy==1.15.2
tqdm==4.67.1
```

## Examples (Bladerunner 2049 wallpaper)

### threshold: 50, edge-strength: 15
![](wallpaper_base16.png)


### threshold: 25, edge-strength: 25
![](wallpaper_base16-2.png)


### threshold: 50, edge-strength: 5
![](wallpaper_base16-3.png)

## Usage:

```
# Basic quantization
python base16_quantizer.py wallpaper.jpg theme.conf out.png

# Collapse dark pixels below brightness 40
python base16_quantizer.py wallpaper.jpg theme.conf out.png --threshold 40

# Highlight edges using $foreground (with optional edge threshold)
python base16_quantizer.py wallpaper.jpg theme.conf out.png --edges --edge-strength 25

# Combined
python base16_quantizer.py wallpaper.jpg theme.conf out.png --threshold 40 --edges --edge-strength 25
```

- Omit --threshold to disable collapsing.
- Works with any Base16-compatible .conf file:

## Colour palette format

```conf
$color00=161616
$color01=262626
$color02=393939
$color03=525252
$color04=dde1e6
$color05=f2f4f8
$color06=ffffff
$color07=08bdba
$color08=3ddbd9
$color09=78a9ff
$color0A=ee5396
$color0B=33b1ff
$color0C=ff7eb6
$color0D=42be65
$color0E=be95ff
$color0F=82cfff
$foreground=f2f4f8
$background=161616
$cursor=ffffff
```

Credits:
- ChatGPT
