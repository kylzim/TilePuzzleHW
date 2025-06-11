import os
from PIL import Image

def slice_image(image_path, output_dir, rows=3, cols=3):
    """
    Slices an image into a grid of tiles.
    
    Args:
        image_path (str): The path to the image to slice.
        output_dir (str): The directory to save the sliced tiles.
        rows (int): The number of rows in the grid.
        cols (int): The number of columns in the grid.
        
    Returns:
        list: A list of file paths for the generated tiles, ordered left-to-right, top-to-bottom.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return None

    img = img.resize((300, 300))
    width, height = img.size
    tile_width = width // cols
    tile_height = height // rows
    
    tile_paths = []
    
    # make sure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # the last tile (tile 8) will be our blank space, so only generate 8 tiles.
    for i in range(rows):
        for j in range(cols):
            tile_num = i * cols + j
            if tile_num == (rows * cols - 1): # don't generate the last tile
                continue
            
            left = j * tile_width
            top = i * tile_height
            right = left + tile_width
            bottom = top + tile_height
            
            tile = img.crop((left, top, right, bottom))
            
            # tile numbers correspond to puzzle state (1-8)
            tile_filename = f"tile_{tile_num + 1}.png"
            tile_path = os.path.join(output_dir, tile_filename)
            tile.save(tile_path, 'PNG')
            tile_paths.append(url_for_static(tile_path))

    return tile_paths

def url_for_static(filepath):
    """A helper to convert a file system path to a static URL path."""
    # replaces backslashes with forward slashes for web URLs
    return filepath.replace('\\', '/').replace('static/', '')