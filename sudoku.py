from PIL import Image, ImageDraw, ImageFilter, ImageFont
import sudokum
import argparse
import numpy as np
from datetime import datetime

# Image size
ixy = (1240, 1250)
font_ttf = "OpenSans-Semibold.ttf"
# Resolution for PDF generation
r = 150.0
# Title font
tf = ImageFont.truetype(font_ttf, size=24)
# Number font
f = ImageFont.truetype(font_ttf, size=42)
# Background color
bg = "white"
# Drow Color
c = "black"
# Diameter for Corner rounds
cd = 75
# Diameter for Box rounds
bd = 74
# Coordinates of the upper-left point of the first Corner round (upper-left of the image)
# The 3 others corner rounds will be drawed by symetry, based on image size
#cxy = (55, 70)
cxy = (60, 65)
# Coordinates of the upper-left point of the first Box round (upper-left of the image)
bxy = (135, 140)
# Vector to apply to a Box round to find the new Box round coordinates (1 box to the right and 1 box to the bottom)
vxy = (112, 112)

def generate_sudoku_grid(index, level, min_number=None):
    print(f"Generating grid [{index}] .", end="")
    while True:
        print(".", end="")
        sg = sudokum.generate(mask_rate=level/10)
        lines_and_squares = []

        if min_number:
            # Cut rows
            for row in sg:
                lines_and_squares.append(row)
            # Cut columns
            for i in range(9):
                lines_and_squares.append([row[i] for row in sg])
            # Cut squares
            for i in range(3):
                for j in range(3):
                    lines_and_squares.append([sg[ii][jj] for ii in range(3*i, 3*i+3) for jj in range(3*j, 3*j+3)])
            
            grid_ok = True
            for item in lines_and_squares:
                if (np.count_nonzero(item) < min_number or np.count_nonzero(item) > 9-min_number):
                    grid_ok = False
                    break
            
            if grid_ok:
                print(".")
                return sg

def generate_image(level, min_number, name, index):
    sg = generate_sudoku_grid(index, level, min_number)
    img = Image.new("RGB", ixy, color=bg)
    draw = ImageDraw.Draw(img)

    # Stamp grid level and name
    draw.text((ixy[0]/2, cxy[1]+bd/2), text=f"Level {level} - {name} [{index}]", fill=c, anchor="mm", font=tf)

    # Draw Corner rounds
    for x in [cxy[0], ixy[0]-cxy[0]-cd]:
        for y in [cxy[1], ixy[1]-cxy[1]-cd]:
            draw.ellipse((x, y, x+cd, y+cd), outline=c, width=2)
            lx = x
            if x == cxy[0]:
                lx = x+cd
            ly = y
            if y == cxy[1]:
                ly = y+cd
            if x == cxy[0]:
                draw.line((0, ly, x+cd/2, ly), fill=c, width=2)
            else:
                draw.line((x+cd/2, ly, ixy[0], ly), fill=c, width=2)
            if y == cxy[1]:
                draw.line((lx, 0, lx, y+cd/2), fill=c, width=2)
            else:
                draw.line((lx, y+cd/2, lx, ixy[1]), fill=c, width=2)

    # Draw Box rounds with inner Number
    for i in range(9):
        for j in range(9):
            draw.ellipse((bxy[0]+i*vxy[0], bxy[1]+j*vxy[1], bxy[0]+i*vxy[0]+bd, bxy[1]+j*vxy[1]+bd), outline=c, width=2)
            if (sg[i][j] != 0):
                draw.text((bxy[0]+i*vxy[0]+bd/2, bxy[1]+j*vxy[1]+bd/2), text=str(sg[i][j]), fill=c, anchor="mm", font=f)
    
    # Debug
    # img.save("output.png")

    # img = img.filter(ImageFilter.SMOOTH)
    return img

def generate_pdf(args):
    name = datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss")
    img_list = []
    for i in range(args.number):
        index = i+1
        img_list.append(generate_image(args.level, args.min, name, index))

    fname = name.replace(" ", "_")
    output_file = f"Sudoku_L{args.level}_{fname}.pdf"
    img_list[0].save(output_file, save_all=True, resolution=r, append_images=img_list[1:])

    print(f"The sudoku grids have been generated here: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate sudoku grids in PDF format, ready to print !")
    parser.add_argument("-l", "--level", default=5.5, type=float, help="Difficulty level from 1 to 9 (1=easiest ; 9=hardest ; 5.5=default). Float value allowed.")
    parser.add_argument("-n", "--number", default=2, type=int, help="Number of grids to generate in PDF (2=default).")
    parser.add_argument("-m", "--min", default=2, type=int, help="Minimum number of initial values (and maximum number of empty initial values) required for density, per line / column / square (2=default).")
    args = parser.parse_args()

    generate_pdf(args)

if __name__ == "__main__":
    main()