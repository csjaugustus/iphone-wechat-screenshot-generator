from PIL import Image, ImageDraw, ImageFont
import re
import os
from create_battery_icon import create_battery

class Moments():
    def __init__(self, mode):
        self.name = ""
        self.avatar = ""
        self.post_text = []
        self.images = []
        self.post_time = ""
        self.likes = []
        self.comments = {}

        self.max_y = 0

        self.mode = mode
        self.set_mode()
        self.canvas = Image.new('RGB', (w, pyq_h), color=self.bg_colour)

    def set_mode(self):
        if self.mode == "light":
            self.bg_colour = "#fefefe"
            self.name_colour = "#5b6a91"
            self.text_colour = "#1a1a1a"
            self.time_colour = "#b3b3b3"
            self.likes_bar_colour = "#f7f7f7"
            self.line_colour = "#dddddd"
            self.more_options = more_options_light
            self.heart = light_heart

        elif self.mode == "dark":
            self.bg_colour = "#191919"
            self.name_colour = "#818d99"
            self.text_colour = "#c9c9c9"
            self.time_colour = "#5f5f5f"
            self.likes_bar_colour = "#212121"
            self.line_colour = "#2b2b2b"
            self.more_options = more_options_dark
            self.heart = dark_heart

        self.refresh()

    def get(self):
        return self.canvas

    def set_avatar(self):
        avypath = f"files\\avatars\\{self.avatar}"
        avatar = Image.open(avypath)
        avatar = avatar.resize((pyq_avatar_px,pyq_avatar_px))

        sq_mask = Image.new('RGBA', (pyq_avatar_px, pyq_avatar_px), "black")
        round_corners(sq_mask)
        self.canvas.paste(avatar, (pyq_left_margin, pyq_top_margin), mask=sq_mask)

        self.max_y = max(self.max_y, pyq_top_margin + pyq_avatar_px + pyq_top_margin)

    def set_name(self):
        eraser_rect = Image.new('RGB', (w-pyq_left_margin-pyq_avatar_px, pyq_avatar_px), color=self.bg_colour)
        self.canvas.paste(eraser_rect, (pyq_left_margin+pyq_avatar_px, pyq_top_margin))
        if self.name:
            draw = ImageDraw.Draw(self.canvas)
            tw, th = get_text_size(self.name, "op_name")
            draw_text(draw, pyq_left_margin+pyq_avatar_px+pyq_avy_name_x_margin, pyq_top_margin+pyq_avy_name_y_margin+th/2, self.name, self.name_colour, "op_name")

        self.max_y = max(self.max_y, pyq_top_margin + pyq_avy_name_y_margin + th + pyq_top_margin + pyq_avy_name_y_margin)

    def set_post_time(self):
        start_x = pyq_left_margin+pyq_avatar_px+pyq_avy_name_x_margin
        start_y = pyq_top_margin + pyq_avy_name_y_margin

        if self.name:
            start_y += get_text_size(self.name, "op_name")[1]
            start_y += margin_to_name

        if self.post_text:
            post_text_lines = get_lines(self.post_text, pyq_max_text_width, "pyq_text")
            start_y += get_lines_dimensions(post_text_lines, pyq_line_mid_to_mid_distance, "pyq_text")[1]

        if self.images:
            start_y += margin_to_photo
            start_y += self.get_imgs_h()

        start_y += to_time_margin

        draw = ImageDraw.Draw(self.canvas)
        tw, th = get_text_size(self.post_time, "pyq_time")
        draw_text(draw, start_x, start_y+th/2, self.post_time, self.time_colour, "pyq_time")

        # add more options icon
        icon_w, icon_h = self.more_options.size
        x = w-more_options_side_margin-icon_w
        y = int(start_y+th/2-icon_h/2)
        self.canvas.paste(self.more_options, (x, y))

        self.max_y = max(self.max_y, start_y + th + to_time_margin)

    def get_imgs_h(self):
        if not self.images:
            return 0
        if len(self.images) == 1:
            return self.images[0].size[1]
        elif 1 < len(self.images) < 4:
            return square_img_px
        elif 4 <= len(self.images) < 7:
            return 2 * square_img_px + photos_margin
        else:
            return 3* square_img_px + 2 * photos_margin

    def set_post_text(self):
        start_x = pyq_left_margin+pyq_avatar_px+pyq_avy_name_x_margin
        start_y = pyq_top_margin + pyq_avy_name_y_margin

        if self.name:
            start_y += get_text_size(self.name, "op_name")[1]
            start_y += margin_to_name

        draw = ImageDraw.Draw(self.canvas)
        lines = get_lines(self.post_text, pyq_max_text_width, "pyq_text")
        first_line_h = get_text_size(lines[0], "pyq_text")[1]
        draw_lines(lines, draw, self.text_colour, start_x, start_y+first_line_h/2, pyq_line_mid_to_mid_distance, "pyq_text")

        l_d = get_lines_dimensions(lines, pyq_line_mid_to_mid_distance, "pyq_text")[1]

        self.max_y = max(self.max_y, start_y + l_d + start_y)

    def set_images(self):
        start_x = pyq_left_margin + pyq_avatar_px + pyq_avy_name_x_margin
        start_y = pyq_top_margin + pyq_avy_name_y_margin

        if self.name:
            start_y += get_text_size(self.name, "op_name")[1]
            start_y += margin_to_name

        if self.post_text:
            post_text_lines = get_lines(self.post_text, pyq_max_text_width, "pyq_text")
            start_y += get_lines_dimensions(post_text_lines, pyq_line_mid_to_mid_distance, "pyq_text")[1]

        start_y += margin_to_photo

        if len(self.images) == 1:
            img = self.images[0]
            img.thumbnail((max_img_px, max_img_px))
            self.canvas.paste(img, (start_x, start_y))

            img_y = img.size[1]

        else:
            cropped_imgs = [crop_center_sq(img).resize((square_img_px, square_img_px)) for img in self.images]

            x_offset = start_x
            y_offset = start_y
            img_y = 0

            for i, img in enumerate(cropped_imgs):
                self.canvas.paste(img, (x_offset, y_offset))
                x_offset += square_img_px + photos_margin
                if i != len(self.images) - 1 and (i+1) % 3 == 0:
                    x_offset = start_x
                    y_offset += square_img_px + photos_margin
                    img_y += square_img_px + photos_margin

        self.max_y = max(self.max_y, start_y + img_y)

    def set_likes(self):
        start_x = pyq_left_margin + pyq_avatar_px + pyq_avy_name_x_margin
        start_y = pyq_top_margin + pyq_avy_name_y_margin

        if self.name:
            start_y += get_text_size(self.name, "op_name")[1]
            start_y += margin_to_name

        if self.post_text:
            post_text_lines = get_lines(self.post_text, pyq_max_text_width, "pyq_text")
            start_y += get_lines_dimensions(post_text_lines, pyq_line_mid_to_mid_distance, "pyq_text")[1]

        if self.images:
            start_y += margin_to_photo
            start_y += self.get_imgs_h()

        if self.post_time:
            start_y += to_time_margin
            start_y += get_text_size(self.post_time, "pyq_time")[1]

        start_y += margin_to_likes

        likes_str = ", ".join(self.likes)
        lines = get_lines(likes_str, likes_bar_w-2*likes_left_margin, "comment_name", indentation=likes_indentation)
        longest_line_length, total_text_h = get_lines_dimensions(lines, likes_m2m, "comment_name")
        bubble_height = total_text_h + 2*likes_top_margin

        bubble_mask = Image.new('RGBA', (likes_bar_w, bubble_height), "black")
        if self.comments:
            round_corners(bubble_mask, top_half=True)
        else:
            round_corners(bubble_mask)
        bubble = Image.new('RGB', (likes_bar_w, bubble_height), color=self.likes_bar_colour)
        bubble_canvas = Image.new('RGB', (likes_bar_w, bubble_height), color=self.bg_colour)
        bubble_canvas.paste(bubble, (0,0), mask=bubble_mask)
        bubble_canvas.paste(self.heart, heart_start_coords)

        bubble_draw = ImageDraw.Draw(bubble_canvas)

        # draw_lines(lines, bubble_draw, self.name_colour, likes_left_margin, likes_top_margin, likes_m2m, "comment_name", indentation=likes_indentation)

        text_start_x = likes_left_margin
        original_start_x = likes_left_margin
        for i, l in enumerate(lines):
            current_th = get_text_size(l, "comment_name")[1]
            if i == 0:
                text_start_x += likes_indentation
                yincrement = current_th / 2
            else:
                text_start_x = original_start_x
                yincrement += prev_th / 2 + likes_m2m - current_th / 2

            # draw_text(draw_obj, start_x, likes_top_margin + yincrement, l, text_colour, ft_type)

            for char in l:
                if char == ",":
                    ft = get_font(char, "comment_text")
                    fill = self.text_colour
                else:
                    ft = get_font(char, "comment_name")
                    fill = self.name_colour
                tw, th = new_get_text_size(char, font=ft)
                bubble_draw.text((text_start_x, likes_top_margin+yincrement), char, font=ft, fill=fill, anchor="lm")
                text_start_x += tw

            prev_th = current_th

        self.canvas.paste(bubble_canvas, (start_x, start_y))

        self.max_y = max(self.max_y, start_y+bubble_height+margin_to_likes)
        self.likes_bubble_height = bubble_height

    def set_comments(self):
        start_x = pyq_left_margin + pyq_avatar_px + pyq_avy_name_x_margin
        start_y = pyq_top_margin + pyq_avy_name_y_margin

        if self.name:
            start_y += get_text_size(self.name, "op_name")[1]
            start_y += margin_to_name

        if self.post_text:
            post_text_lines = get_lines(self.post_text, pyq_max_text_width, "pyq_text")
            start_y += get_lines_dimensions(post_text_lines, pyq_line_mid_to_mid_distance, "pyq_text")[1]

        if self.images:
            start_y += margin_to_photo
            start_y += self.get_imgs_h()

        if self.post_time:
            start_y += to_time_margin
            start_y += get_text_size(self.post_time, "pyq_time")[1]

        if self.likes:
            start_y += margin_to_likes
            start_y += self.likes_bubble_height

        line = Image.new('RGB', (likes_bar_w, 1), color=self.line_colour)
        self.canvas.paste(line, (start_x, start_y))
        start_y += 1

        comment_strs = []
        for c in self.comments:
            try:
                self.comments[c]['reply_to_name']
            except KeyError:
                comment_strs.append(f"{c}: {self.comments[c]['text']}")
            else:
                comment_strs.append(f"{c}回复{self.comments[c]['reply_to_name']}: {self.comments[c]['text']}")

        split_lst = []
        for c in comment_strs:
            tw, th = get_text_size(c, "comment_name")
            if tw <= likes_bar_w - 2*likes_left_margin:
                split_lst.append(c)
            else:
                lines = get_lines(c, likes_bar_w - 2*likes_left_margin, "comment_name")
                for l in lines:
                    split_lst.append(l)

        longest_line_length, total_text_h = get_lines_dimensions(split_lst, likes_m2m, "comment_name")
        bubble_height = total_text_h + 2*likes_top_margin

        bubble_mask = Image.new('RGBA', (likes_bar_w, bubble_height), "black")
        if self.likes:
            round_corners(bubble_mask, bottom_half=True)
        else:
            round_corners(bubble_mask)
        bubble = Image.new('RGB', (likes_bar_w, bubble_height), color=self.likes_bar_colour)
        bubble_canvas = Image.new('RGB', (likes_bar_w, bubble_height), color=self.bg_colour)
        bubble_canvas.paste(bubble, (0,0), mask=bubble_mask)

        bubble_draw = ImageDraw.Draw(bubble_canvas)

        bubble_start_x = likes_left_margin
        for i, l in enumerate(split_lst):
            current_th = get_text_size(l, "comment_name")[1]
            current_x = bubble_start_x
            if i == 0:
                yincrement = current_th / 2
            else:
                yincrement += prev_th / 2 + likes_m2m - current_th / 2

            match = re.match(r"(.*)回复(.*): (.*)", l)
            match2 = re.match(r"(.*): (.*)", l)
            if match:
                commentor_name, reply_to_name, text = match.groups()
                bubble_draw.text((current_x, likes_top_margin+yincrement), commentor_name, font=get_font(commentor_name, "comment_name"), fill=self.name_colour, anchor="lm")
                current_x += get_text_size(commentor_name, "comment_name")[0]
                bubble_draw.text((current_x, likes_top_margin+yincrement), "回复", font=get_font("回复", "comment_text"), fill=self.text_colour, anchor="lm")
                current_x += get_text_size("回复", "comment_text")[0]
                bubble_draw.text((current_x, likes_top_margin+yincrement), reply_to_name, font=get_font(reply_to_name, "comment_name"), fill=self.name_colour, anchor="lm")
                current_x += get_text_size(reply_to_name, "comment_name")[0]
                bubble_draw.text((current_x, likes_top_margin+yincrement), f": {text}", font=get_font(f": {text}", "comment_text"), fill=self.text_colour, anchor="lm")
            elif match2:
                commentor_name, text = match2.groups()
                bubble_draw.text((current_x, likes_top_margin+yincrement), commentor_name, font=get_font(commentor_name, "comment_name"), fill=self.name_colour, anchor="lm")
                current_x += get_text_size(commentor_name, "comment_name")[0]
                bubble_draw.text((current_x, likes_top_margin+yincrement), f": {text}", font=get_font(f": {text}", "comment_text"), fill=self.text_colour, anchor="lm")
            else:
                bubble_draw.text((current_x, likes_top_margin+yincrement), l, font=get_font(l, "comment_text"), fill=self.text_colour, anchor="lm")

            prev_th = current_th

        self.canvas.paste(bubble_canvas, (start_x, start_y))

        self.max_y = max(self.max_y, start_y+bubble_height+margin_to_likes+1)

    def get_cropped(self):
        if self.max_y == 0:
            return self.canvas.crop((0, 0, w, pyq_h))
        return self.canvas.crop((0, 0, w, self.max_y))

    def refresh(self):
        self.max_y = 0
        self.canvas = Image.new('RGB', (w, pyq_h), color=self.bg_colour)
        if self.avatar:
            self.set_avatar()
        if self.name:
            self.set_name()
        if self.post_text:
            self.set_post_text()
        if self.images:
            self.set_images()
        if self.post_time:
            self.set_post_time()
        if self.likes:
            self.set_likes()
        if self.comments:
            self.set_comments()


class Chat():
    def __init__(self, mode):
        self.title = ""
        self.system_time = ""
        self.battery = ""
        self.mode = mode
        self.set_mode()
        self.canvas = Image.new('RGB', (w, h), color=self.bg_colour)
        self.canvas.paste(self.system_time_bar, (0,0))
        self.canvas.paste(self.title_bar, (0,system_time_bar_height))
        self.canvas.paste(self.input_box, (0,h-input_box_height))
        self.entries = []
        self.entries_dark = []
        self.content_height = 0

    def set_mode(self):
        self.right_text = "#1c1c1c"

        if self.mode == "light":
            self.left_bubble_base_colour = '#ffffff'
            self.bg_colour = '#ededed'
            self.left_text_colour = '#1c1c1c'
            self.timestamp_colour = '#a9a9a9'
            self.system_time_colour = '#070707'
            self.right_bubble_base_colour = '#97ec6a'

            self.title_bar = title_bar
            self.input_box = input_box
            self.left_arrow = whitearrow
            self.right_arrow = greenarrow
            self.system_time_bar = system_time_bar
            self.system_time_bar_eraser = system_time_bar_eraser
            self.battery_eraser = battery_light_eraser

        elif self.mode == "dark":
            self.left_bubble_base_colour = '#2c2c2c'
            self.bg_colour = '#111111'
            self.left_text_colour = '#c9c9c9'
            self.timestamp_colour = '#535353'
            self.system_time_colour = '#fefefe'
            self.right_bubble_base_colour = '#42b16c'

            self.title_bar = title_bar_dark
            self.input_box = input_box_dark
            self.left_arrow = darkarrow
            self.right_arrow = greenarrowDark
            self.system_time_bar = system_time_bar_dark
            self.system_time_bar_eraser = system_time_bar_dark_eraser
            self.battery_eraser = battery_dark_eraser


    def set_title(self, title):
        self.canvas.paste(self.title_bar, (0,system_time_bar_height))
        if title:
            draw = ImageDraw.Draw(self.canvas)
            tw, th = get_text_size(title, "title")
            draw_text(draw, (w-tw)/2, system_time_bar_height + chat_title_height / 2, title, self.left_text_colour, "title")
        self.title = title

    def set_system_time(self, time):
        self.canvas.paste(self.system_time_bar_eraser, (0,0))
        if time:
            draw = ImageDraw.Draw(self.canvas)
            draw.text((63, 38), time, font=system_time_font, fill=self.system_time_colour)
        self.system_time = time

    def set_battery(self, perc):
        self.canvas.paste(self.battery_eraser, (741,36))
        if perc:
            battery_img = create_battery(perc, self.mode)
            self.canvas.paste(battery_img, (741, 36))
        self.battery = perc

    def add_timestamp(self, t):
        ft = get_font(t, "timestamp")
        def create_timestamp():
            timestamp_canvas = Image.new('RGB', (w, timestamp_height + 2 * top_margin), color=self.bg_colour)
            draw = ImageDraw.Draw(timestamp_canvas)
            x_pos = (w - new_get_text_size(t, font=ft)[0])/2
            draw.text((x_pos, top_margin), t, font=ft, fill=self.timestamp_colour)
            return timestamp_canvas

        if self.mode == "light":
            self.entries.append(create_timestamp())
            self.mode = "dark"
            self.set_mode()
            self.entries_dark.append(create_timestamp())
            self.mode = "light"
            self.set_mode()

        elif self.mode == "dark":
            self.entries_dark.append(create_timestamp())
            self.mode = "light"
            self.set_mode()
            self.entries.append(create_timestamp())
            self.mode = "dark"
            self.set_mode()

        self.update()

    def add(self, avyName, text, side):
        avypath = f"files\\avatars\\{avyName}"
        avatar = Image.open(avypath)
        avatar = avatar.resize((avatar_px,avatar_px))
        self.create_user_strip(avatar, text, side)
        self.update()

    def delete(self, indx):
        del self.entries[indx]
        del self.entries_dark[indx]
        blank = Image.new('RGB', (w, max_chat_height), color=self.bg_colour)
        self.canvas.paste(blank, (0, top_part_height))
        self.update()

    def update(self, change_mode=False):
        if change_mode:
            self.canvas = Image.new('RGB', (w, h), color=self.bg_colour)
            self.canvas.paste(self.system_time_bar, (0,0))
            self.canvas.paste(self.title_bar, (0,system_time_bar_height))
            self.canvas.paste(self.input_box, (0,h-input_box_height))
            if self.title:
                self.set_title(self.title)
            if self.system_time:
                self.set_system_time(self.system_time)
            if self.battery:
                self.set_battery(self.battery)

        if self.entries:
            if self.mode == "light":
                temp = self.entries
            elif self.mode == "dark":
                temp = self.entries_dark
            img = temp[0]
            if len(temp) > 1:
                for i in range(1, len(temp)):
                    img = self.get_concat_v(img, temp[i])
            if img.size[1] > max_chat_height:
                img = img.crop((0, img.size[1]-max_chat_height, w, img.size[1]))
                self.content_height = max_chat_height
            else:
                self.content_height = img.size[1]
            self.canvas.paste(img, (0,top_part_height))
        else:
            blank = Image.new('RGB', (w, max_chat_height), color=self.bg_colour)
            self.canvas.paste(blank, (0,top_part_height))

    def get_cropped_from_top(self):
        if self.content_height == max_chat_height:
            return self.canvas.crop((0, 0, w, h))
        return self.canvas.crop((0, 0, w, self.content_height + top_part_height))

    def get_cropped_from_bottom(self):
        if not self.content_height:
            return self.input_box
        content_part = self.canvas.crop((0, top_part_height, w, self.content_height + top_part_height))
        return self.get_concat_v(content_part, self.input_box)

    def create_user_strip(self, avatar, text, side):
        lines = get_lines(text, max_text_width, "text")
        longest_line_length, total_text_h = get_lines_dimensions(lines, line_mid_to_mid_distance,"text")

        first_line_h = get_text_size(lines[0], "text")[1]
        last_line_h = get_text_size(lines[-1], "text")[1]
        speech_bubble_required_h = 2 * top_margin + 2 * bubble_top_margin + total_text_h
        avatar_required_h = avatar_px + 2 * top_margin
        h = max(speech_bubble_required_h, avatar_required_h)

        if longest_line_length + 2 * bubble_left_margin <= max_bubble_width:
            bubble_width = longest_line_length + 2 * bubble_left_margin
        else:
            bubble_width = max_bubble_width

        bubble_height = h - (2 * top_margin)

        sq_mask = Image.new('RGBA', (avatar_px,avatar_px), "black")
        round_corners(sq_mask)
        bubble_mask = Image.new('RGBA', (bubble_width, bubble_height), "black")
        round_corners(bubble_mask)

        user_canvas = Image.new('RGB', (w, h), color=self.bg_colour)
        if side == "left":
            user_canvas.paste(avatar, (side_margin, top_margin), mask=sq_mask)
            bubble_colour = self.left_bubble_base_colour
            text_colour = self.left_text_colour
        elif side == "right":
            user_canvas.paste(avatar, (w-side_margin-avatar_px, top_margin), mask=sq_mask)
            bubble_colour = self.right_bubble_base_colour
            text_colour = self.right_text

        bubble = Image.new('RGB', (bubble_width, bubble_height), color=bubble_colour)
        bubble_canvas = Image.new('RGB', (bubble_width, bubble_height), color=self.bg_colour)
        bubble_canvas.paste(bubble, (0,0), mask=bubble_mask)

        bubble_draw = ImageDraw.Draw(bubble_canvas)

        draw_lines(lines, bubble_draw, text_colour, bubble_left_margin, bubble_top_margin, line_mid_to_mid_distance, "text")

        if side == "left":
            speech_bubble = self.get_concat_h(self.left_arrow, bubble_canvas)
            user_canvas.paste(speech_bubble, (side_margin+avatar_px, top_margin))
        elif side == "right":
            speech_bubble = self.get_concat_h(bubble_canvas, self.right_arrow)
            arrow_width = greenarrow.size[0]
            user_canvas.paste(speech_bubble, (w-bubble_width-2*arrow_width-avatar_px, top_margin))

        if self.mode == "light":
            self.entries.append(user_canvas)
            self.mode = "dark"
            self.set_mode()
            self.entries_dark.append(user_canvas)
            self.mode = "light"
            self.set_mode()

        elif self.mode == "dark":
            self.entries_dark.append(user_canvas)
            self.mode = "light"
            self.set_mode()
            self.entries.append(user_canvas)
            self.mode = "dark"
            self.set_mode()

    def get(self):
        return self.canvas

    def get_concat_h(self, im1, im2):
        dst = Image.new('RGB', (im1.width + im2.width, max(im1.height,im2.height)), color=self.bg_colour)
        dst.paste(im1, (0, 0))
        dst.paste(im2, (im1.width, 0))
        return dst

    def get_concat_v(self, im1, im2):
        dst = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height), color=self.bg_colour)
        dst.paste(im1, (0, 0))
        dst.paste(im2, (0, im1.height))
        return dst

def sort_text(text):
    seq = []

    matches = pattern.findall(text)

    current_lang = ""

    while True:
        if any(text.startswith(match) for match in matches):
            current_lang = "en"
            for match in matches:
                if text.startswith(match):
                    seq.append(match)
                    text = text.lstrip(match)
        else:
            if current_lang == "cn":
                seq[-1] = seq[-1] + text[0]
                text = text[1:]
            else:
                current_lang = "cn"
                seq.append(text[0])
                text = text[1:]
        if not text:
            break

    return seq

def get_text_size(text, ft_type): # this is not to be confused with new_get_text_size which gets the textsize of individual elements
    if not text:
        return (0, 0)

    w, h = 0, 0
    seq = sort_text(text)

    for el in seq:
        tw, th = new_get_text_size(el, font=get_font(el, ft_type))
        w += tw
        if th > h:
            h = th

    return (w, h)

def draw_text(img_draw_obj, xcoord, ycoord, text, fill, ft_type):
    draw = img_draw_obj
    seq = sort_text(text)

    for el in seq:
        ft = get_font(el, ft_type)
        tw, th = new_get_text_size(el, font=ft)
        draw.text((xcoord, ycoord), el, font=ft, fill=fill, anchor="lm")
        xcoord += tw

def contains_chinese(x):
    r = pattern.findall(x)
    if not r:
        return True
    if r[0] == x:
        return False
    return True

def get_font(text, ft_type):
    dic = {
        "en" : {
            "title" : en_title_font,
            "text" : en_text_font,
            "timestamp" : en_timestamp_font,
            "system_time" : system_time_font,
            "op_name" : en_op_name_font,
            "pyq_text" : en_pyq_text_font,
            "pyq_time" : en_pyq_time_font,
            "comment_name" : en_comment_name_font,
            "comment_text" : en_comment_text_font
        },
        "cn" : {
            "title" : cn_title_font,
            "text" : cn_text_font,
            "timestamp" : cn_timestamp_font,
            "system_time" : system_time_font,
            "op_name" : cn_op_name_font,
            "pyq_text" : cn_pyq_text_font,
            "pyq_time" : cn_pyq_time_font,
            "comment_name" : cn_comment_name_font,
            "comment_text" : cn_comment_text_font
        }
    }

    if contains_chinese(text):
        return dic["cn"][ft_type]

    else:
        return dic["en"][ft_type]


def new_get_text_size(text, font): # uses bbox instead of textsize, since textsize is deprecated
    temp_canvas = Image.new("RGB", (0, 0))
    draw = ImageDraw.Draw(temp_canvas)

    draw.text((0, 0), text, font=font)
    bbox = draw.textbbox((0, 0), text, font=font)

    x_min, y_min, x_max, y_max = bbox
    tw = x_max - x_min
    th = y_max - y_min
    return tw, th

def round_corners(img, corner_px=10, curve_strength=1.8, top_half=False, bottom_half=False): # modifies on the spot, no return value
    img_w, img_h = img.size

    # create a corner image
    corner = Image.new('RGBA', (corner_px, corner_px), (0,0,0,0))
    corner_draw = ImageDraw.Draw(corner)
    corner_draw.pieslice((0,0,corner_px*curve_strength,corner_px*curve_strength), 180, 270, fill="black")

    if top_half:
        img.paste(corner, (0,0))
        img.paste(corner.rotate(270), (img_w-corner_px, 0))

    elif bottom_half:
        img.paste(corner.rotate(90), (0, img_h-corner_px))
        img.paste(corner.rotate(180), (img_w-corner_px, img_h-corner_px))

    else:
        img.paste(corner, (0,0))
        img.paste(corner.rotate(90), (0, img_h-corner_px))
        img.paste(corner.rotate(180), (img_w-corner_px, img_h-corner_px))
        img.paste(corner.rotate(270), (img_w-corner_px, 0))

def get_lines(text, max_text_width, ft_type, indentation=None):
    def break_word(word):
        lst = []
        while word:
            indx = 0
            for i in range(1, len(word)+1):
                part = word[:i]
                width = get_text_size(part, ft_type)[0]
                if width <= max_text_width:
                    indx = i
                else:
                    break
            lst.append(word[:indx])
            word = word[indx:]
        return lst

    #break long words
    lines = []
    temp = text.split()
    split_text = []
    for word in temp:
        if get_text_size(word, ft_type)[0] <= max_text_width:
            split_text.append(word)
        else:
            split_text += break_word(word)

    #split text into lines
    indx = 0
    first_line = True
    while split_text:
        if first_line and indentation:
            line_width = max_text_width - indentation
        else:
            line_width = max_text_width
        for i in range(1,len(split_text)+1):
            current_line = " ".join(split_text[:i])
            if get_text_size(current_line, ft_type)[0] <= line_width:
                indx = i
            else:
                if not pattern.findall(split_text[i-1]): #break chinese character clusters
                    temp = break_word(current_line)
                    if len(temp) > 1:
                        last = temp[1]
                        first = split_text[i-1][:-len(last)]
                        split_text[i-2] = split_text[i-2] + " " + first
                        split_text[i-1] = last
                break
        line = " ".join(split_text[:indx])
        split_text = split_text[indx:]
        lines.append(line)
        first_line = False

    return lines


def get_lines_dimensions(lines, m2m_dist, ft_type):
    first_line_h = get_text_size(lines[0], ft_type)[1]
    last_line_h = get_text_size(lines[-1], ft_type)[1]
    total_text_h = int((len(lines)-1) * m2m_dist + first_line_h/2 + last_line_h/2)

    longest_line_length = max(get_text_size(l, ft_type)[0] for l in lines)

    return longest_line_length, total_text_h

def draw_lines(lines, draw_obj, text_colour, start_x, start_y, m2m_dist, ft_type, indentation=None):
    original_start_x = start_x
    for i, l in enumerate(lines):
        current_th = get_text_size(l, ft_type)[1]
        if i == 0:
            if indentation:
                start_x += indentation
            yincrement = current_th / 2
        else:
            start_x = original_start_x
            yincrement += prev_th / 2 + m2m_dist - current_th / 2
        draw_text(draw_obj, start_x, start_y + yincrement, l, text_colour, ft_type)
        prev_th = current_th


def crop_center_sq(img):
    w, h = img.size
    sq_length = min(w, h)
    center_x = w / 2
    center_y = h / 2

    x1 = center_x - (sq_length / 2)
    y1 = center_y - (sq_length / 2)

    return img.crop((x1, y1, x1 + sq_length, y1 + sq_length))

#fonts
en_title_font = ImageFont.truetype('files\\sf-ui-display-semibold-58646eddcae92.otf', 32)
en_text_font = ImageFont.truetype('files\\SFPRODISPLAYREGULAR.OTF', 32)
cn_title_font = ImageFont.truetype('files\\PingFang Bold.ttf', 32)
cn_text_font = ImageFont.truetype('files\\PingFang Medium.ttf', 32)
en_timestamp_font = ImageFont.truetype('files\\FontsFree-Net-SF-UI-Display-Regular-1.ttf', 28)
cn_timestamp_font = ImageFont.truetype('files\\PingFang Medium.ttf', 27)
system_time_font = ImageFont.truetype('files\\SFPRODISPLAYBOLD.OTF', 32)

cn_op_name_font = ImageFont.truetype('files\\PingFang Heavy.ttf', 32)
en_op_name_font = ImageFont.truetype('files\\sf-ui-display-semibold-58646eddcae92.otf', 33)
cn_pyq_text_font = ImageFont.truetype('files\\PingFang Medium.ttf', 32)
en_pyq_text_font = ImageFont.truetype('files\\SF-UI-Display-Regular.otf', 34)
cn_pyq_time_font = ImageFont.truetype('files\\PingFang Regular.ttf', 26)
en_pyq_time_font = ImageFont.truetype('files\\SF-UI-Display-Regular.otf', 28)
cn_comment_name_font = ImageFont.truetype('files\\PingFang Heavy.ttf', 28)
en_comment_name_font = ImageFont.truetype('files\\sf-ui-display-semibold-58646eddcae92.otf', 29)
cn_comment_text_font = ImageFont.truetype('files\\PingFang Medium.ttf', 28)
en_comment_text_font = ImageFont.truetype('files\\SF-UI-Display-Regular.otf', 29)

#constants
pattern = re.compile("[\\dA-Za-z\\s.,\"$%!?:()-\u2014;\u00e9]+")
w, h = 828, 1792
top_margin = 17
side_margin = 24
bubble_left_margin = 25
max_bubble_width = 574
max_text_width = max_bubble_width - 2 * bubble_left_margin
bubble_top_margin = 25
timestamp_height = 34
chat_title_height = 87
system_time_bar_height = 97
top_part_height = chat_title_height + system_time_bar_height
input_box_height = 174
max_chat_height = h - top_part_height - input_box_height
avatar_px = 80
line_mid_to_mid_distance = 40

#  pyq constants
pyq_h = 1607
square_img_px = 173
pyq_avatar_px = 86

pyq_top_margin = 28
pyq_left_margin = 39
pyq_avy_name_x_margin = 21
pyq_avy_name_y_margin = 5
pyq_line_mid_to_mid_distance = 46
margin_to_name = 5
margin_to_photo = 40
photos_margin = 10
to_time_margin = 40
time_to_bottom = 33
max_img_px = 360
pyq_max_text_width = 620
more_options_side_margin = 44
margin_to_likes = 32
likes_bar_w = 644
heart_start_coords = (21, 18)
likes_top_margin = 15
likes_left_margin = 18
likes_m2m = 45
likes_indentation = 40

#images
title_bar = Image.open('files\\chattitle.png')
input_box = Image.open('files\\inputbox.png')
whitearrow = Image.open('files\\speechbubblewhitearrow.png')
greenarrow = Image.open('files\\speechbubblegreenarrow.png')
system_time_bar = Image.open('files\\systemtimebarlight.png')
system_time_bar_eraser = Image.open('files\\systemtimebarlight_eraser.png')
battery_light_eraser = Image.open('files\\battery_light_eraser.png')

title_bar_dark = Image.open('files\\chattitledark.png')
input_box_dark = Image.open('files\\inputboxdark.png')
darkarrow = Image.open('files\\speechbubbledarkarrow.png')
greenarrowDark = Image.open('files\\speechbubblegreenarrowdark.png')
system_time_bar_dark = Image.open('files\\systemtimebardark.png')
system_time_bar_dark_eraser = Image.open('files\\systemtimebardark_eraser.png')
battery_dark_eraser = Image.open('files\\battery_dark_eraser.png')

more_options_light = Image.open('files\\more_options_light.png')
more_options_dark = Image.open('files\\more_options_dark.png')
light_heart = Image.open('files\\light_heart.png')
dark_heart = Image.open('files\\dark_heart.png')
