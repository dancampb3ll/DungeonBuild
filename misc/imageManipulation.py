from PIL import Image

def split_image(image_path, output_path_without_png_extension):
    """Splits images into 16x16 chunks
    
    """
    original_image = Image.open(image_path)
    original_image = original_image.convert("RGBA")

    # Get size of image
    width, height = original_image.size

    if width % 16 != 0 or height % 16 != 0:
        print("Invalid size, cancelled.")
        return
    
    image_loop_size_x = width // 16
    image_loop_size_y = height // 16

    for i in range(image_loop_size_x):
        for j in range(image_loop_size_y):
            x_start = i * 16
            y_start = j * 16
            x_end = x_start + 16
            y_end = y_start + 16

            # Crop the chunk from the original image
            chunk = original_image.crop((x_start, y_start, x_end, y_end))

            # Save the chunk as a PNG file
            chunk.save(f"{output_path_without_png_extension}{i}{j}.png")

    print("Image successfully split into 16x16 chunks.")


def replace_chroma_color(image_path, chroma_color, replacement_image_path, new_save_path):
    # Open the original image
    original_image = Image.open(image_path)
    original_image = original_image.convert("RGBA")
    original_pixel_data = original_image.load()

    # Load the replacement image
    replacement_image = Image.open(replacement_image_path)
    replacement_image = replacement_image.convert("RGBA")
    replacement_pixel_data = replacement_image.load()

    # Size of the replacement image (16x16)
    replacement_size = replacement_image.size

    # Iterate over each pixel in the original image
    width, height = original_image.size
    for x in range(width):
        for y in range(height):
            # Check if the pixel matches the chroma color
            if original_pixel_data[x, y][:3] == chroma_color:
                # Determine the corresponding pixel from the replacement image using modulus
                replacement_x = x % replacement_size[0]
                replacement_y = y % replacement_size[1]

                # Get the pixel from the replacement image
                replacement_pixel = replacement_pixel_data[replacement_x, replacement_y]

                # Replace the pixel in the original image with the pixel from the replacement image
                original_pixel_data[x, y] = replacement_pixel

    # Save the modified original image
    original_image.save(new_save_path)

def resize_image(input_path, output_path, xheight, yheight):
    with Image.open(input_path) as img:
        resized_img = img.resize((xheight, yheight), Image.NEAREST)
        resized_img.save(output_path)

def make_png_colour_transparent(r, g, b, image_input_path, image_output_path):
    img = Image.open(image_input_path).convert("RGBA")

    data = img.getdata()

    # Creates a new image with transparency
    new_data = []
    for item in data:
        if item[0] == r and item[1] == g and item[2] == b:
            new_data.append((255, 255, 255, 0))  # Transparent
        else:
            new_data.append(item)

    img.putdata(new_data)

    img.save(image_output_path)

"""Replace with transparency
replace_image_path = "assets/other/underworld/coin.png"
output_path = "assets/other/underworld/coin1.png"
make_png_colour_transparent(255, 0, 255, replace_image_path, output_path)
"""

""" Replace chroma with other image
replace_image_path = "assets/underworldtiles/boulderSmall.png"
replacement_texture_path = "assets/underworldtiles/cobblestone.png"
new_path = replace_image_path + " replaced.png"
replace_chroma_color(replace_image_path, (255, 0, 255), replacement_texture_path, new_path)
"""

#split_image("assets/Unused/Hero.png", "assets/Unused/player")
"""
files = ["down1", "down2", "down3", "down4", "left1", "left2", "left3", "left4", "right1", "right2", "right3", "right4", "up1", "up2", "up3", "up4"]
for filename in files:
    imagepath = f"assets/player/overworld/{filename}.png"
    outputpath = f"assets/player/underworld/{filename}.png"
    resize_image(imagepath, outputpath, 32, 32)
"""

"""
replace_image_path = "assets/underworldtiles/stairs.png"
stone_texture_path = "assets/underworldtiles/cobblestone.png"
new_path = replace_image_path + " replaced.png"
replace_chroma_color(replace_image_path, (255, 255, 255), stone_texture_path, new_path)
replace_chroma_color
"""