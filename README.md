Examples (Bladerunner 2049 wallpaper)


![](wallpaper_base16.png)


![](wallpaper_base16-2.png)

Usage:

```
# Basic quantization
python base16_quantizer.py wallpaper.jpg theme.conf out.png

# Collapse dark pixels below brightness 40
python base16_quantizer.py wallpaper.jpg theme.conf out.png --threshold 40

# Highlight edges using $foreground (with optional edge threshold)
python base16_quantizer.py wallpaper.jpg theme.conf out.png --edges --edge-strength 25
```

- Omit --threshold to disable collapsing.
- Works with any Base16-compatible .conf file:

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

# preview

| Threshold (t) \ Edge Strength (e) | e=0 | e=20 | e=40 | e=60 | e=80 | e=100 |
|---|---|---|---|---|---|---|
| **t=0** | ![t=0, e=0](quantized_variations/wallpaper_base16-t00-e00.png) | ![t=0, e=20](quantized_variations/wallpaper_base16-t00-e20.png) | ![t=0, e=40](quantized_variations/wallpaper_base16-t00-e40.png) | ![t=0, e=60](quantized_variations/wallpaper_base16-t00-e60.png) | ![t=0, e=80](quantized_variations/wallpaper_base16-t00-e80.png) | ![t=0, e=100](quantized_variations/wallpaper_base16-t00-e100.png) |
| **t=20** | ![t=20, e=0](quantized_variations/wallpaper_base16-t20-e00.png) | ![t=20, e=20](quantized_variations/wallpaper_base16-t20-e20.png) | ![t=20, e=40](quantized_variations/wallpaper_base16-t20-e40.png) | ![t=20, e=60](quantized_variations/wallpaper_base16-t20-e60.png) | ![t=20, e=80](quantized_variations/wallpaper_base16-t20-e80.png) | ![t=20, e=100](quantized_variations/wallpaper_base16-t20-e100.png) |
| **t=40** | ![t=40, e=0](quantized_variations/wallpaper_base16-t40-e00.png) | ![t=40, e=20](quantized_variations/wallpaper_base16-t40-e20.png) | ![t=40, e=40](quantized_variations/wallpaper_base16-t40-e40.png) | ![t=40, e=60](quantized_variations/wallpaper_base16-t40-e60.png) | ![t=40, e=80](quantized_variations/wallpaper_base16-t40-e80.png) | ![t=40, e=100](quantized_variations/wallpaper_base16-t40-e100.png) |
| **t=60** | ![t=60, e=0](quantized_variations/wallpaper_base16-t60-e00.png) | ![t=60, e=20](quantized_variations/wallpaper_base16-t60-e20.png) | ![t=60, e=40](quantized_variations/wallpaper_base16-t60-e40.png) | ![t=60, e=60](quantized_variations/wallpaper_base16-t60-e60.png) | ![t=60, e=80](quantized_variations/wallpaper_base16-t60-e80.png) | ![t=60, e=100](quantized_variations/wallpaper_base16-t60-e100.png) |
| **t=80** | ![t=80, e=0](quantized_variations/wallpaper_base16-t80-e00.png) | ![t=80, e=20](quantized_variations/wallpaper_base16-t80-e20.png) | ![t=80, e=40](quantized_variations/wallpaper_base16-t80-e40.png) | ![t=80, e=60](quantized_variations/wallpaper_base16-t80-e60.png) | ![t=80, e=80](quantized_variations/wallpaper_base16-t80-e80.png) | ![t=80, e=100](quantized_variations/wallpaper_base16-t80-e100.png) |
| **t=100** | ![t=100, e=0](quantized_variations/wallpaper_base16-t100-e00.png) | ![t=100, e=20](quantized_variations/wallpaper_base16-t100-e20.png) | ![t=100, e=40](quantized_variations/wallpaper_base16-t100-e40.png) | ![t=100, e=60](quantized_variations/wallpaper_base16-t100-e60.png) | ![t=100, e=80](quantized_variations/wallpaper_base16-t100-e80.png) | ![t=100, e=100](quantized_variations/wallpaper_base16-t100-e100.png) |


Credits:
- ChatGPT
