from __future__ import print_function
import string
from PIL import Image, ImageFont, ImageDraw, ImageFilter, ImageOps
import numpy as np

FONT = "../../comic.ttf"

def char_to_pixels(text, path=FONT, fontsize=14, font_name=None, bold=False):
    """
    Based on https://stackoverflow.com/a/27753869/190597 (jsheperd)
    """
    try:
        if font_name:
            # Try to use system font
            import pygame
            pygame.font.init()
            
            # Get font path for system font
            font_path = pygame.font.match_font(font_name, bold=bold)
            if font_path:
                font = ImageFont.truetype(font_path, fontsize)
            else:
                # Fallback to default font
                font = ImageFont.load_default()
        else:
            # Use provided path
            font = ImageFont.truetype(path, fontsize)
    except (OSError, IOError):
        # Fallback to default font if loading fails
        font = ImageFont.load_default()
    
    bbox = font.getbbox(text)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    h *= 3
    image = Image.new('L', (w, h), 1)  
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font) 
    arr = np.asarray(image)
    arr2 = np.where(arr, 0, 1)
    arr2 = arr2[(arr2 != 0).any(axis=1)]
    return arr2

def display(arr, char):
    print(f'["{char}"] = {{\n    height = {arr.shape[0]},\n    length = {arr.shape[1]},\n    points = {{')
    conv_array = np.where(arr, arr, '0')
    result = ""
    #print('\n'.join([''.join(row) for row in result]))
    for row in conv_array:
        result += "{"
        for column in row:
            result += f"{column},"
        result += "},\n"
    result += "}},\n"
    print(result)
    pixel_example = np.where(arr, '#', ' ')
    print("--[[")
    print('\n'.join([''.join(row) for row in pixel_example]))
    print("--]]")
    print(np.count_nonzero(pixel_example))

def display_simple(arr, char):
    pixel_example = np.where(arr, '#', ' ')
    print('\n'.join([''.join(row) for row in pixel_example]))
    print(np.count_nonzero(pixel_example))



def convert_chars():
    for c in string.printable:
        arr = char_to_pixels(
            c, 
            path=FONT, 
            fontsize=24)
        display(arr, c)
        print()

def convert_string(text):
    for c in text:
        arr = char_to_pixels(
            c, 
            path=FONT, 
            fontsize=40)
        display_simple(arr, c)
        print()

def convert_image(path):
    original_image = Image.open(path)
    processed_image = original_image.convert(mode='RGB')
    processed_image = ImageOps.posterize(processed_image,1)#.resize((11,11))#Image.NEAREST
    processed_image = processed_image.convert(mode='L')

    arr = np.asarray(processed_image)
    print(arr)
    unique_values = list(set(i for j in arr for i in j))
    #arr = np.where(arr, 0, 1)
    #arr = arr[(arr != 0).any(axis=1)] #remove all zero rows
    #arr = np.where(arr, unique_values.index(arr), arr)
    zero_value1 = max(unique_values)
    arr = np.array([[map_to_index(y, unique_values, zero_value1, 255) for y in x] for x in arr])

    #original_image.show() 
    processed_image.show()
    print(arr)
    print(unique_values)
    #print(arr2)
    display(arr,":m:")

def map_to_index(value, u_set, zero_value1, zero_value2):
    if(value==zero_value1 or value==zero_value2):
        return 0
    return u_set.index(value)

    