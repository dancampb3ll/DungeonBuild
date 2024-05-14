from PIL import Image

def split_image(image_path, output_path_without_png_extension):
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


replace_image_path = "assets/unused/tinyPot.png"
grass_texture_path = "assets/overgroundGrass.png"
new_path = replace_image_path + " replaced.png"
replace_chroma_color(replace_image_path, (255, 255, 255), grass_texture_path, new_path)


#split_image("assets/Unused/largeHut.png", "assets/Unused/largeHut")