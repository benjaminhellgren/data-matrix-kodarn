import math
from ppf.datamatrix import DataMatrix
from PIL import Image, ImageDraw, ImageFont

def dm_to_image(text, scale=10):
    dm = DataMatrix(text)
    matrix = dm.matrix
    h = len(matrix)
    w = len(matrix[0])

    img = Image.new("L", (w, h), 255)
    pixels = img.load()

    for y in range(h):
        for x in range(w):
            pixels[x, y] = 0 if matrix[y][x] else 255

    return img.resize((w * scale, h * scale), Image.NEAREST)

# ---- SETTINGS ----

START = 0       ## Start of interval of codes to generate
STOP = 50       ## End of interval
COLUMNS = 4     ## How many columns of codes. Less means they take larger space
ROWS = 5        ## How many columns of codes
SPACING_X = 120 ## Space between DM codes on x axis
SPACING_Y = 160 ## Space between DM codes on y axis
PADDING_X= 80   ## left and right padding
PADDING_Y = 80  ## top and bottom padding

## Text settings

TEXT = True # Generate human readable text below.
LABEL_HEIGHT = 120
FONT = "consola.ttf"
LETTER_SIZE = 65

# Load font
try:
    font = ImageFont.truetype(FONT, LETTER_SIZE)
except OSError:
    font = ImageFont.load_default()

# Value error check
if STOP <= START:
    raise ValueError("STOP must be greater than START")
if COLUMNS <= 0 or ROWS <= 0:
    raise ValueError("ROWS and COLUMNS must be above 0")

# Get code size
texts = [f"{i}" for i in range(START, STOP)]
code_width, code_height = dm_to_image(texts[0], scale=20).size

# Canvas size WITH spacing + label area
canvas_width = COLUMNS * code_width + (COLUMNS - 1) * SPACING_X + 2 * PADDING_X
canvas_height = ROWS * (code_height) + (ROWS - 1) * SPACING_Y + 2 * PADDING_Y

pages = []  # store PIL images for the PDF

codes_per_page = ROWS * COLUMNS
total_pages = math.ceil((STOP - START) / codes_per_page)

current_num = START
for page_index in range(total_pages):
    canvas = Image.new("L", (canvas_width, canvas_height), 255)
    draw = ImageDraw.Draw(canvas)

    texts_slice = texts[page_index * codes_per_page : (page_index + 1) * codes_per_page]

    print(f"Generating page {page_index+1}/{total_pages}")
    for i, text in enumerate(texts_slice):
        
        code_img = dm_to_image(text, scale=20)
        col = i % COLUMNS
        row = i // COLUMNS

        x = col * (code_width + SPACING_X) + PADDING_X
        y = row * (code_height + SPACING_Y) + PADDING_Y - int(font.size) // 2 * TEXT # Shift codes upward

        # Paste the DataMatrix
        canvas.paste(code_img, (x, y))

        # Label (centered under code)
        label_text = str(current_num)
        if TEXT:
            bbox = draw.textbbox((0, 0), label_text, font=font)  # Pillow 10+
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            text_x = x + (code_width - text_w) // 2
            text_y = y + code_height + 10  # + margin below code
            draw.text((text_x, text_y), label_text, fill=0, font=font)

        current_num += 1

    # Convert page to RGB for PDF and collect
    pages.append(canvas.convert("RGB"))

# ---- Save all pages into a single PDF ----
output_pdf = "datamatrix_labels.pdf"
if pages:
    pages[0].save(
        output_pdf, 
        save_all=True, 
        append_images=pages[1:], 
        resolution=300
        )
    print(f"Saved PDF: {output_pdf}")
else:
    print("No pages to save.")