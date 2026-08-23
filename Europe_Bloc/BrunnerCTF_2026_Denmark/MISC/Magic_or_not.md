 Solver : SideChicks
  ### 1. Analysis of File Obfuscation

  Inspecting the first few bytes of each file reveals that each file was encrypted using a single-byte XOR cipher:
  • Brunner1.jpg: First bytes a7 80 a7 b3...
      • Standard JPEG magic header is FF D8 FF ...
      • 0xA7 ^ 0xFF = 0x58 ('X')
  • Brunner2.gif: First bytes 10 1e 11 6f 6e 36...
      • Standard GIF89a magic header is 47 49 46 38 39 61 ("GIF89a")
      • 0x10 ^ 0x47 = 0x57 ('W')
  • Brunner3.png: First bytes d0 09 17 1e 54 53...
      • Standard PNG magic header is 89 50 4E 47 0D 0A...
      • 0xD0 ^ 0x89 = 0x59 ('Y')
  • Brunner4.bmp: First bytes 18 17...
      • Standard BMP magic header is 42 4D ("BM")
      • 0x18 ^ 0x42 = 0x5A ('Z')

  ──────
  ### 2. Recovery & Stitching
  XORing each file with its respective key recovers the 4 valid image files:

  • Slice 1: 642 x 896 px
  • Slice 2: 190 x 896 px
  • Slice 3: 68 x 896 px
  • Slice 4: 321 x 896 px
  All 4 images share the same height of 896 px. Stitching them horizontally in sequential order 1 -> 2 -> 3 -> 4 reveals the complete original image containing the flag
  on the flag cloth.

    from PIL import Image
    
    files_keys = [
        ('Brunner1.jpg', 0x58),
        ('Brunner2.gif', 0x57),
        ('Brunner3.png', 0x59),
        ('Brunner4.bmp', 0x5a),
    ]
    
    slices = []
    for filename, key in files_keys:
        with open(filename, 'rb') as f:
            data = bytes([b ^ key for b in f.read()])
        # Save temporary recovered slice
        temp_path = f'recovered_{filename}'
        with open(temp_path, 'wb') as f:
            f.write(data)
        slices.append(Image.open(temp_path).convert('RGB'))
    
    # Stitch horizontally
    total_width = sum(im.width for im in slices)
    height = slices[0].height
    stitched = Image.new('RGB', (total_width, height))
    
    x = 0
    for im in slices:
        stitched.paste(im, (x, 0))
        x += im.width

    stitched.save('flag_revealed.png')
  ──────
  ### Flag

    brunner{ctf2026}
