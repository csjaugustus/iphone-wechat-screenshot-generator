from PIL import Image, ImageDraw, ImageFont

def new_get_text_size(text, font): # uses bbox instead of textsize, since textsize is deprecated
    temp_canvas = Image.new("RGB", (0, 0))
    draw = ImageDraw.Draw(temp_canvas)

    draw.text((0, 0), text, font=font)
    bbox = draw.textbbox((0, 0), text, font=font)

    x_min, y_min, x_max, y_max = bbox
    tw = x_max - x_min
    th = y_max - y_min
    return tw, th

def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, max(im1.height,im2.height)), color='#000000')
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

def get_px(perc):
    return int(pinless_w // (100/perc))

def round_corners(img, corner_px=5, curve_strength=1.8): # modifies on the spot, no return value
    img_w, img_h = img.size

    # create a corner image
    corner = Image.new('RGBA', (corner_px, corner_px), (0,0,0,0))
    corner_draw = ImageDraw.Draw(corner)
    corner_draw.pieslice((0,0,corner_px*curve_strength,corner_px*curve_strength), 180, 270, fill="black")

    img.paste(corner, (0,0))
    img.paste(corner.rotate(90), (0, img_h-corner_px))
    img.paste(corner.rotate(180), (img_w-corner_px, img_h-corner_px))
    img.paste(corner.rotate(270), (img_w-corner_px, 0))

def create_battery(perc, mode):
    if mode == "light":
        filled_colour = light_filled_colour
        unfilled_colour = light_unfilled_colour
        bg_colour = light_bg_colour
        font_colour = light_font_colour

        if perc >= 99:
            battery_pin = full_light_battery_pin
        else:
            battery_pin = light_battery_pin
    elif mode == "dark":
        filled_colour = dark_filled_colour
        unfilled_colour = dark_unfilled_colour
        bg_colour = dark_bg_colour
        font_colour = dark_font_colour

        if perc >= 99:
            battery_pin = full_dark_battery_pin
        else:
            battery_pin = dark_battery_pin
    else:
        print("Invalid mode.")
        return

    if perc <= 20:
        filled_colour = low_battery_filled_colour

    battery_mask = Image.new('RGBA', (pinless_w, h), "black")
    round_corners(battery_mask)

    filled_px = get_px(perc)
    unfilled_px = pinless_w - filled_px

    filled_rec = Image.new('RGB', (filled_px, h), color=filled_colour)
    unfilled_rec = Image.new('RGB', (unfilled_px, h), color=unfilled_colour)
    rec = get_concat_h(filled_rec, unfilled_rec)

    canvas = Image.new('RGB', (w, h), color=bg_colour)
    canvas.paste(rec, (0,0), mask=battery_mask)
    canvas.paste(battery_pin, (pinless_w,0))

    # adding text
    draw = ImageDraw.Draw(canvas)
    tw, th = new_get_text_size(str(perc), font=battery_font)
    x_pos = (pinless_w - tw) / 2
    draw.text((x_pos, 0+y_pos_offset), str(perc), font=battery_font, fill=font_colour)

    return canvas

#constants
w, h = 53, 27
pinless_w = 48
y_pos_offset = -2
light_filled_colour = "#080808"
light_unfilled_colour = "#a5a5a5"
dark_filled_colour = "#fdfdfd"
dark_unfilled_colour = "#8a8a8a"
light_bg_colour = '#ededed'
dark_bg_colour = '#111111'
light_font_colour = "#ebebeb"
dark_font_colour = "#050505"
low_battery_filled_colour = "#fe453b"

#files
light_battery_pin = Image.open("files\\light_battery_pin.png")
dark_battery_pin = Image.open("files\\dark_battery_pin.png")
full_light_battery_pin = Image.open("files\\full_light_battery_pin.png")
full_dark_battery_pin = Image.open("files\\full_dark_battery_pin.png")
battery_font = ImageFont.truetype('files\\SFPRODISPLAYBOLD.OTF', 25)

if __name__ == "__main__":
    b = create_battery(19, "dark")
    b.show()




