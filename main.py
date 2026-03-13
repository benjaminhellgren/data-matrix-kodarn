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
SPACING_X = 120
SPACING_Y = 160
PADDING = 80
START = 200
STOP = 2000
texts = [f"{i}" for i in range(START, STOP)]
columns = 4
rows = 5
LABEL_HEIGHT = 120  # if you want labels under codes; set to 0 to remove

# ---- Generate all codes ----
codes = [dm_to_image(t, scale=20) for t in texts]
cell_w, cell_h = codes[0].size

# Canvas size WITH spacing + label area
canvas_w = columns * cell_w + (columns - 1) * SPACING_X + 2 * PADDING
canvas_h = rows * (cell_h) + (rows - 1) * SPACING_Y + 2 * PADDING

# Font (Windows path; adjust if needed)
font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 65)

pages = []  # store PIL images for the PDF
current_num = START

num_per_page = rows * columns
total_pages = math.ceil(len(codes) / num_per_page)

for page_index in range(total_pages):
    canvas = Image.new("L", (canvas_w, canvas_h), 255)
    draw = ImageDraw.Draw(canvas)

    slice_codes = codes[page_index * num_per_page : (page_index + 1) * num_per_page]

    for i, code_img in enumerate(slice_codes):
        col = i % columns
        row = i // columns

        x = col * (cell_w + SPACING_X) + PADDING
        y = row * (cell_h + SPACING_Y) + PADDING - 20 # skifta uppåt

        # Paste the DataMatrix
        canvas.paste(code_img, (x, y))

        # Label (centered under code)
        label_text = str(current_num)
        if True:
            bbox = draw.textbbox((0, 0), label_text, font=font)  # Pillow 10+
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            text_x = x + (cell_w - text_w) // 2
            text_y = y + cell_h + 10  # margin below code
            draw.text((text_x, text_y), label_text, fill=0, font=font)

        current_num += 1

    # Convert page to RGB for PDF and collect
    pages.append(canvas.convert("RGB"))

# ---- Save all pages into a single PDF ----
output_pdf = "datamatrix_labels.pdf"
if pages:
    pages[0].save(output_pdf, save_all=True, append_images=pages[1:])
    print(f"Saved PDF: {output_pdf}")
else:
    print("No pages to save.")