from PIL import Image, ImageDraw, ImageFont
import re
import os

class Screenshot():
	def __init__(self, mode):
		self.title = ""
		self.system_time = ""
		self.mode = mode
		self.set_mode()
		self.canvas = Image.new('RGB', (w, h), color=self.bg_colour)
		self.canvas.paste(self.system_time_bar, (0,0))
		self.canvas.paste(self.title_bar, (0,system_time_bar_height))
		self.canvas.paste(self.input_box, (0,1618))
		self.entries = []
		self.entries_dark = []
		self.content_height = 0

	def set_mode(self):
		self.right_text = "#1c1c1c"

		if self.mode == "light":
			self.left_bubble_base_colour = '#ffffff'
			self.bg_colour = '#ededed'
			self.left_text_colour = '#1c1c1c'
			self.timestamp_colour = '#adadad'
			self.system_time_colour = '#070707'
			self.right_bubble_base_colour = '#97ec6a'

			self.title_bar = title_bar
			self.input_box = input_box
			self.left_arrow = whitearrow
			self.right_arrow = greenarrow
			self.system_time_bar = system_time_bar

		elif self.mode == "dark":
			self.left_bubble_base_colour = '#2c2c2c'
			self.bg_colour = '#111111'
			self.left_text_colour = '#c9c9c9'
			self.timestamp_colour = '#858585'
			self.system_time_colour = '#fcfcfc'
			self.right_bubble_base_colour = '#42b16c'

			self.title_bar = title_bar_dark
			self.input_box = input_box_dark
			self.left_arrow = darkarrow
			self.right_arrow = greenarrowDark
			self.system_time_bar = system_time_bar_dark


	def set_title(self, title):
		self.canvas.paste(self.title_bar, (0,system_time_bar_height))
		if title:
			draw = ImageDraw.Draw(self.canvas)
			tw, th = get_text_size(title, title=True)
			draw_text(draw, (w-tw)/2, 118, title, self.left_text_colour, title=True)
		self.title = title

	def set_system_time(self, time):
		self.canvas.paste(self.system_time_bar, (0,0))
		if time:
			draw = ImageDraw.Draw(self.canvas)
			draw.text((63, 38), time, font=system_time_font, fill=self.system_time_colour)
			self.system_time = time

	def add_timestamp(self, t):
		def create_timestamp():
			timestamp_canvas = Image.new('RGB', (w, timestamp_height + 2 * top_margin), color=self.bg_colour)
			draw = ImageDraw.Draw(timestamp_canvas)
			x_pos = (w - draw.textsize(t, font=time_font)[0])/2
			draw.text((x_pos, top_margin), t, font=time_font, fill=self.timestamp_colour)
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
		avatar = avatar.resize((86,86))
		self.create_bubble(avatar, text, side)
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
			self.canvas.paste(self.input_box, (0,1618))
			if self.title:
				self.set_title(self.title)
			if self.system_time:
				self.set_system_time(self.system_time)

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
				self.content_height = h
			else:
				self.content_height = top_part_height + img.size[1] + bubble_top_margin
			self.canvas.paste(img, (0,top_part_height))
		else:
			blank = Image.new('RGB', (w, max_chat_height), color=self.bg_colour)
			self.canvas.paste(blank, (0,top_part_height))

	def create_bubble(self, avatar, text, side):
		def break_word(word):
			lst = []
			while word:
				indx = 0
				for i in range(1, len(word)+1):
					part = word[:i]
					width = get_text_size(part)[0]
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
			if get_text_size(word)[0] <= max_text_width:
				split_text.append(word)
			else:
				split_text += break_word(word)

		#split text into lines
		indx = 0
		while split_text:
			for i in range(1,len(split_text)+1):
				current_line = " ".join(split_text[:i])
				if get_text_size(current_line)[0] <= max_text_width:
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

		text_height = 0
		for l in lines:
			th = get_text_size(l)[1]
			text_height += th
		h = 2 * top_margin + 2 * bubble_top_margin + (len(lines)-1) * bubble_line_margin + text_height

		#round avatar mask
		corner = Image.new('RGBA', (10,10), (0,0,0,0))
		corner_draw = ImageDraw.Draw(corner)
		corner_draw.pieslice((0,0, 20, 20), 180, 270, fill="black")
		sq = Image.new('RGBA', (86,86), "black")
		sq.paste(corner, (0,0))
		sq.paste(corner.rotate(90), (0, 86-10))
		sq.paste(corner.rotate(180), (86-10, 86-10))
		sq.paste(corner.rotate(270), (86-10, 0))
		
		longest_line_length = max(get_text_size(l)[0] for l in lines)
		if longest_line_length <= 535:
			bubble_width = longest_line_length + 2 * 30
			bubble_side_margin = 30
		else:
			bubble_width = fixed_bubble_width
			bubble_side_margin = (fixed_bubble_width - max(get_text_size(l)[0] for l in lines))/2

		bubble_height = 2 * bubble_top_margin + (len(lines)-1) * bubble_line_margin + text_height + 7

		#round bubble corners
		bubble_mask = Image.new('RGBA', (bubble_width, bubble_height), "black")
		bubble_mask.paste(corner, (0,0))
		bubble_mask.paste(corner.rotate(90), (0, bubble_height-10))
		bubble_mask.paste(corner.rotate(180), (bubble_width-10, bubble_height-10))
		bubble_mask.paste(corner.rotate(270), (bubble_width-10, 0))

		def get_user_canvas():
			user_canvas = Image.new('RGB', (w, h), color=self.bg_colour)
			if side == "left":
				user_canvas.paste(avatar, (side_margin, top_margin), mask=sq)
				bubble_colour = self.left_bubble_base_colour
				text_colour = self.left_text_colour
			elif side == "right":
				user_canvas.paste(avatar, (w-side_margin-86, top_margin), mask=sq)
				bubble_colour = self.right_bubble_base_colour
				text_colour = self.right_text

			bubble = Image.new('RGB', (bubble_width, bubble_height), color=bubble_colour)
			bubble_canvas = Image.new('RGB', (bubble_width, bubble_height), color=self.bg_colour)
			bubble_canvas.paste(bubble, (0,0), mask=bubble_mask)

			bubble_draw = ImageDraw.Draw(bubble_canvas)
			
			yincrement = 0

			for l in lines:
				draw_text(bubble_draw, bubble_side_margin, bubble_top_margin+yincrement, l, text_colour)
				yincrement += bubble_line_margin + get_text_size(l)[1]

			if side == "left":
				speech_bubble = self.get_concat_h(self.left_arrow, bubble_canvas)
				user_canvas.paste(speech_bubble, (side_margin+86, top_margin))
			elif side == "right":
				speech_bubble = self.get_concat_h(bubble_canvas, self.right_arrow)
				arrow_width = greenarrow.size[0]
				user_canvas.paste(speech_bubble, (w-bubble_width-2*arrow_width-86, top_margin))
			return user_canvas

		if self.mode == "light":
			self.entries.append(get_user_canvas())
			self.mode = "dark"
			self.set_mode()
			self.entries_dark.append(get_user_canvas())
			self.mode = "light"
			self.set_mode()

		elif self.mode == "dark":
			self.entries_dark.append(get_user_canvas())
			self.mode = "light"
			self.set_mode()
			self.entries.append(get_user_canvas())
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

def get_text_size(text, title=False):
	new = Screenshot("light")
	canvas = new.get()
	draw = ImageDraw.Draw(canvas)
	if not text:
		return (0, 0)

	w, h = 0, 0
	seq = sort_text(text)

	if pattern.findall(seq[0]): #first element is not chinese
		if title:
			ft = en_title_font

			for el in seq:
				tw, th = draw.textsize(el, font=ft)
				w += tw
				if th > h:
					h = th
				if ft == en_title_font:
					ft = cn_title_font
				else:
					ft = en_title_font

		else:
			ft = en_text_font

			for el in seq:
				tw, th = draw.textsize(el, font=ft)
				w += tw
				if th > h:
					h = th
				if ft == en_text_font:
					ft = cn_text_font
				else:
					ft = en_text_font
	else:
		if title:
			ft = cn_title_font

			for el in seq:
				tw, th = draw.textsize(el, font=ft)
				w += tw
				if th > h:
					h = th
				if ft == en_title_font:
					ft = cn_title_font
				else:
					ft = en_title_font

		else:
			ft = cn_text_font

			for el in seq:
				tw, th = draw.textsize(el, font=ft)
				w += tw
				if th > h:
					h = th
				if ft == en_text_font:
					ft = cn_text_font
				else:
					ft = en_text_font

	return (w, h)

def draw_text(img_draw_obj, xcoord, ycoord, text, fill, title=False):
	draw = img_draw_obj
	seq = sort_text(text)

	if pattern.findall(seq[0]): #first element is not chinese
		if title:
			ft = en_title_font

			for el in seq:
				draw.text((xcoord, ycoord), el, font=ft, fill=fill)
				tw, th = draw.textsize(el, font=ft)
				if ft == en_title_font:
					ft = cn_title_font
				else:
					ft = en_title_font
				xcoord += tw
		else:
			ft = en_text_font

			for el in seq:
				draw.text((xcoord, ycoord), el, font=ft, fill=fill)
				tw, th = draw.textsize(el, font=ft)
				if ft == en_text_font:
					ft = cn_text_font
				else:
					ft = en_text_font
				xcoord += tw
	else:
		if title:
			ft = cn_title_font

			for el in seq:
				draw.text((xcoord, ycoord), el, font=ft, fill=fill)
				tw, th = draw.textsize(el, font=ft)
				if ft == en_title_font:
					ft = cn_title_font
				else:
					ft = en_title_font
				xcoord += tw
		else:
			ft = cn_text_font

			for el in seq:
				draw.text((xcoord, ycoord), el, font=ft, fill=fill)
				tw, th = draw.textsize(el, font=ft)
				if ft == en_text_font:
					ft = cn_text_font
				else:
					ft = en_text_font
				xcoord += tw

def load_avatar(avypath):
	avatar = Image.open(avypath)
	avatar = avatar.resize((86,86))
	return avatar

#fonts
en_title_font = ImageFont.truetype('files\\sf-ui-display-semibold-58646eddcae92.otf', 32)
en_text_font = ImageFont.truetype('files\\SFPRODISPLAYREGULAR.OTF', 32)
cn_title_font = ImageFont.truetype('files\\PingFang Bold.ttf', 32)
cn_text_font = ImageFont.truetype('files\\PingFang Medium.ttf', 32)
time_font = ImageFont.truetype('files\\sf-ui-display-medium-58646be638f96.otf', 28)
system_time_font = ImageFont.truetype('files\\SFPRODISPLAYBOLD.OTF', 32)

#constants
pattern = re.compile("[\\dA-Za-z\\s.,\"$%!?:()-\u2014;\u00e9]+")
w, h = 828, 1792
top_margin = 14
side_margin = 25
fixed_bubble_width = 595
max_text_width = fixed_bubble_width - 50
bubble_top_margin = 17
bubble_line_margin = 8
timestamp_height = 34
max_chat_height = 1434
chat_title_height = 87
system_time_bar_height = 97
top_part_height = chat_title_height + system_time_bar_height

#images
title_bar = Image.open('files\\chattitle.png')
input_box = Image.open('files\\inputbox.png')
whitearrow = Image.open('files\\speechbubblewhitearrow.png')
greenarrow = Image.open('files\\speechbubblegreenarrow.png')
system_time_bar = Image.open('files\\systemtimebarlight.png')

title_bar_dark = Image.open('files\\chattitledark.png')
input_box_dark = Image.open('files\\inputboxdark.png')
darkarrow = Image.open('files\\speechbubbledarkarrow.png')
greenarrowDark = Image.open('files\\speechbubblegreenarrowdark.png')
system_time_bar_dark = Image.open('files\\systemtimebardark.png')
