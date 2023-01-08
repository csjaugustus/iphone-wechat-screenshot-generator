from PIL import ImageDraw, Image, ImageFont

def new_get_text_size(text, font):
    temp_canvas = Image.new("RGB", (0, 0))
    draw = ImageDraw.Draw(temp_canvas)

    draw.text((0, 0), text, font=font)
    bbox = draw.textbbox((0, 0), text, font=font)

    x_min, y_min, x_max, y_max = bbox
    tw = x_max - x_min
    th = y_max - y_min
    return tw, th

en_text_font = ImageFont.truetype('files\\SFPRODISPLAYREGULAR.OTF', 32)

print(new_get_text_size("Hello World", en_text_font))
