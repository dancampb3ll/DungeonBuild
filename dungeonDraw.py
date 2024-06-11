"""Used to draw images of generated dungeons, quicker to test"""
import underworld.tiles
from PIL import Image

def save_image_from_map(save_address, map, material_colour_representations):
    # Background color
    BACKGROUND_COLOUR = (0, 0, 0)
    SCALE = 4  # Scaling factor
    
    # Extract the coordinates
    x_coords = [coord[0] for coord in map.keys()]
    y_coords = [coord[1] for coord in map.keys()]
    
    # Determine the min and max coordinates
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # Calculate scaled image dimensions
    width = (max_x - min_x + 1) * SCALE
    height = (max_y - min_y + 1) * SCALE
    
    # Create a new image with the background color
    image = Image.new('RGB', (width, height), BACKGROUND_COLOUR)
    pixels = image.load()
    
    # Draw the pixels based on the map
    for (x, y), value in map.items():
        material = value[0]
        color = material_colour_representations.get(material, BACKGROUND_COLOUR)
        # Calculate the top-left corner of the 4x4 block
        start_x = (x - min_x) * SCALE
        start_y = (y - min_y) * SCALE
        
        # Fill a 4x4 block with the color
        for dx in range(SCALE):
            for dy in range(SCALE):
                pixels[start_x + dx, start_y + dy] = color
    
    # Save the image to the specified address
    image.save(save_address)

# Example usage
material_colour_representations = {
    "cobblestone": (54, 50, 40),
    "stairs": (200, 200, 200),
    "border": (20, 20, 20)
}

GENERATE_COUNT = 10
for i in range(GENERATE_COUNT):
    print(f"Printing image {i} ******************************************************")
    map, spawns = underworld.tiles.generate_new_map_dict_and_spawns()
    print("************************************************************************************")

    save_image_from_map(f"misc/dungeon_images/output_image{i}.png", map, material_colour_representations)



