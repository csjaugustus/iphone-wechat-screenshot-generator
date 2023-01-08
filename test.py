from PIL import ImageDraw, Image, ImageFont

def get_min_letter_height(text, font):
    temp_canvas = Image.new("RGB", (200,200), color="white")
    draw = ImageDraw.Draw(temp_canvas)
    if not text:
        return 0
    if len(text) == 1:
        return draw.textsize(text, font)[1]

    for i, letter in enumerate(text):
        if i == 0:
            current_th = draw.textbbox(letter, font=font)
            prev_th = current_th
            min_th = current_th
        else:
            current_th = draw.textbbox(letter, font=font)
            if current_th < prev_th:
                min_th = current_th

    return min_th

en_text_font = ImageFont.truetype('files\\SFPRODISPLAYREGULAR.OTF', 32)

blank = Image.new('RGB', (114,37), color="white")
draw_obj = ImageDraw.Draw(blank)
draw_obj.text((0,0), "example", font=en_text_font, fill="black")
tw, th = draw_obj.textbbox("example", font=en_text_font)
print(tw, th)
print(get_min_letter_height("example", font=en_text_font))
blank.show()
