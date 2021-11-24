
import PIL
from PIL import Image
from PIL import ImageDraw
import numpy as np
import math

def read_image(path):
    try:
        image = PIL.Image.open(path)
        return image
    except Exception as e:
        print(e)

def watermark_image(image,text,fontsize,wmalpha,dither):

    # Make a monochrome watermark. This one is just makes it using text. you could probably just draw a monochrome image too.
    fontsize = 54
    font = PIL.ImageFont.truetype("arial.ttf",fontsize )

    watermark_mask = PIL.Image.new("L",font.getsize(text + " "),(0)) 
    watermark_w,watermark_h = watermark_mask.size

    # Turn text into an small image
    draw = PIL.ImageDraw.Draw(watermark_mask)
    draw.text((0,0),  text + " ", font = font, align = "center",fill=(255)) 

    # Tile it to fill the image. Allow users manual control over the positioning of this pattern
    watermark_tiled = PIL.Image.new("L",image.size)    
    tilesw = int(math.ceil(image.size[0] / watermark_mask.size[0] ))
    tilesh = int(math.ceil(image.size[1] / watermark_mask.size[1] ))

    ofs = 0
    for ty in range(0, tilesh):  
        ofs = ofs + watermark_mask.size[0] / 2.33333333
        if ofs > watermark_mask.size[0]:
            ofs = ofs - watermark_mask.size[0]
        ofs = int(ofs)
        for tx in range(-1, tilesw):
            watermark_tiled.paste(watermark_mask, box=(watermark_mask.size[0] * tx + ofs, watermark_mask.size[1] * ty), mask=None)


    # Load the dithering pattern
    # Maybe generate a default one later if its not present?
    dither_sample = read_image(dither)
    

    #tile the dithering pattern to fit the whole image
    dither_stitched = PIL.Image.new("RGB",image.size,(128,128,128,0))   
    dither_tile_w = int(math.ceil(image.size[0] / dither_sample.size[0]))
    dither_tile_h = int(math.ceil(image.size[1] / dither_sample.size[1]))
    for tx in range(0, dither_tile_w):
        for ty in range(0, dither_tile_h):   
            dither_stitched.paste(dither_sample, box=(dither_sample.size[0]  * tx, dither_sample.size[1]  * ty), mask=None)
    
    
    #Set the alpha channel of the pattern to the watermark texture.
    dither_masked = dither_stitched.copy()
    dither_masked = dither_masked.convert("RGBA")
    
    dither_masked.putalpha(watermark_tiled)

    #overlay method, this one is weak around solid black and white
    
    #dither_background= PIL.Image.new("RGBA",image.size,(128,128,128,255))   
    #dither_greyed = PIL.Image.alpha_composite(dither_background,dither_masked)
    #dither_greyed = PIL.Image.blend(dither_greyed, dither_background, 1-wmalpha)
    #watermarked_image = PIL.ImageChops.overlay(image.convert("RGB"), dither_greyed.convert("RGB"))



    #additive/subtractive mode
    #Might want to use something a little less linear than this, otherwise it might be too easy to compensate for.

    brightness = wmalpha*256

    dither_stitched_invert = Image.eval(dither_stitched, (lambda x: 255-x))

    darken_mask = Image.eval(dither_stitched, (lambda x: ((x-127) / 255 * brightness)))
    darken_component = PIL.ImageChops.multiply(watermark_tiled.convert("RGB"), darken_mask.convert("RGB"))


    lighten_mask = Image.eval(dither_stitched_invert, (lambda x: ((x-127) / 255 * brightness)))
    lighten_component = PIL.ImageChops.multiply(watermark_tiled.convert("RGB"), lighten_mask.convert("RGB"))

    #darken_component.save("sub.png")
    #lighten_component.save("add.png")



    watermarked_image = image.copy()
    watermarked_image = PIL.ImageChops.subtract(watermarked_image.convert("RGB"), darken_component.convert("RGB"))
    watermarked_image = PIL.ImageChops.add(watermarked_image.convert("RGB"), lighten_component.convert("RGB"))

    watermarked_image = watermarked_image.convert("RGB")

    return watermarked_image

from PIL import Image, ImageFilter , ImageEnhance

def find_watermark(watermarked_image,original_image,lossy):
    # Clean Analysis
    analyzed_image = PIL.ImageChops.difference(original_image.convert("RGB"),watermarked_image )

    if not lossy:
        enhancer = ImageEnhance.Brightness(analyzed_image)
        analyzed_image = enhancer.enhance(16)

        enhancer = ImageEnhance.Contrast(analyzed_image)
        analyzed_image = enhancer.enhance(16)

    if lossy:
        for ty in range(0, 2):  
            analyzed_image = analyzed_image.filter(PIL.ImageFilter.GaussianBlur(radius=1))
           
        enhancer = ImageEnhance.Brightness(analyzed_image)
        analyzed_image = enhancer.enhance(0.9)

        enhancer = ImageEnhance.Contrast(analyzed_image)
        analyzed_image = enhancer.enhance(15)

        enhancer = ImageEnhance.Brightness(analyzed_image)
        analyzed_image = enhancer.enhance(10)


        #enhancer = ImageEnhance.Sharpness(analyzed_image)
        #analyzed_image = enhancer.enhance(1)

        enhancer = ImageEnhance.Color(analyzed_image)
        analyzed_image = enhancer.enhance(0)

    return analyzed_image

#oh baby this is where i try these out

import os
import sys

try: 
    image_path = sys.argv[1]; 
except IndexError: 
    sys.exit("ERROR: you need to specify an image name!")

try: 
    quality = sys.argv[2]; 
except IndexError: 
    quality = 100

try: 
    ditherpattern = sys.argv[3]; 
except IndexError: 
    ditherpattern = "dithersample.png"


def watermark_for_user(image,user):
    foldername = "users/" + user
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    target_path = foldername + "/" + image_path 
    watermarked = watermark_image(image,user,False,0.02,"ditherpatterns/" + ditherpattern)
    watermarked.save(target_path,quality=100)
    print("wrote " + target_path)
    #testing code
    watermarked = read_image(target_path)
    analyzed = find_watermark(watermarked,image,True)
    analyzed.save(target_path + "_analysis.png")
    print("wrote " + target_path + "_analysis.png")


def watermark_for_users(image,users):
    for user in users:
        user = user.strip('\n')
        user = user.strip('\t')
        watermark_for_user(user)


image = read_image(image_path)
image = image.convert('RGB')

watermark_for_user(image,"trash")

#subfile = open('users.txt','r')
#subscribers = subfile.readlines()
#watermark_for_users(subscribers)