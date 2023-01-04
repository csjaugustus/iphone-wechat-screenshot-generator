from PIL import Image, ImageDraw, ImageFont
import re
import os

class Screenshot():
	def __init__(self, mode):
		self.title = ""
		self.time = ""
		self.mode = mode
		self.setMode()
		self.canvas = Image.new('RGB', (w, h), color=self.bg)
		self.canvas.paste(self.system_time_bar, (0,0))
		self.canvas.paste(self.titleBar, (0,97))
		self.canvas.paste(self.inputBox, (0,1618))
		self.entries = []
		self.entriesDark = []

	def setMode(self):
		self.rightText = "#1c1c1c"

		if self.mode == "light":
			self.leftBubbleBase = '#ffffff'
			self.bg = '#ededed'
			self.leftText = '#1c1c1c'
			self.timeColour = '#adadad'
			self.system_time_colour = '#070707'

			self.titleBar = titlebar
			self.inputBox = inputbox
			self.leftArrow = whitearrow
			self.rightArrow = greenarrow
			self.rightBubbleBase = '#97ec6a'

			self.system_time_bar = system_time_bar

		elif self.mode == "dark":
			self.leftBubbleBase = '#2c2c2c'
			self.bg = '#111111'
			self.leftText = '#c9c9c9'
			self.timeColour = '#858585'
			self.system_time_colour = '#fcfcfc'

			self.titleBar = titlebarDark
			self.inputBox = inputboxDark
			self.leftArrow = darkarrow
			self.rightArrow = greenarrowDark
			self.rightBubbleBase = '#42b16c'

			self.system_time_bar = system_time_bar_dark


	def setTitle(self, title):
		self.canvas.paste(self.titleBar, (0,97))
		if title:
			draw = ImageDraw.Draw(self.canvas)
			tw, th = getTextSize(title, title=True)
			drawText(draw, (w-tw)/2, 118, title, self.leftText, title=True)
		self.title = title

	def set_system_time(self, time):
		self.canvas.paste(self.system_time_bar, (0,0))
		if time:
			draw = ImageDraw.Draw(self.canvas)
			draw.text((63, 38), time, font=system_time_font, fill=self.system_time_colour)
			self.system_time = time

	def addTimeMarker(self, t):
		def createTimeMarker():
			tCanvas = Image.new('RGB', (w, timeMarkerHeight + 2 * topMargin), color=self.bg)
			draw = ImageDraw.Draw(tCanvas)
			xPos = (w - draw.textsize(t, font=timeFont)[0])/2
			draw.text((xPos, topMargin), t, font=timeFont, fill=self.timeColour)
			return tCanvas

		if self.mode == "light":
			self.entries.append(createTimeMarker())
			self.mode = "dark"
			self.setMode()
			self.entriesDark.append(createTimeMarker())
			self.mode = "light"
			self.setMode()

		elif self.mode == "dark":
			self.entriesDark.append(createTimeMarker())
			self.mode = "light"
			self.setMode()
			self.entries.append(createTimeMarker())
			self.mode = "dark"
			self.setMode()

		self.update()

	def add(self, avyName, text, side):
		avypath = f"files\\avatars\\{avyName}"
		avatar = Image.open(avypath)
		avatar = avatar.resize((86,86))
		self.createBubble(avatar, text, side)
		self.update()

	def delete(self, indx):
		del self.entries[indx]
		del self.entriesDark[indx]
		blank = Image.new('RGB', (w, maxChatHeight), color=self.bg)
		self.canvas.paste(blank, (0, 184))
		self.update()

	def update(self, changeMode=False):
		if changeMode:
			self.canvas = Image.new('RGB', (w, h), color=self.bg)
			self.canvas.paste(self.system_time_bar, (0,0))
			self.canvas.paste(self.titleBar, (0,97))
			self.canvas.paste(self.inputBox, (0,1618))
			if self.title:
				self.setTitle(self.title)
			if self.system_time:
				self.set_system_time(self.system_time)

		if self.entries:
			if self.mode == "light":
				temp = self.entries
			elif self.mode == "dark":
				temp = self.entriesDark
			img = temp[0]
			if len(temp) > 1:
				for i in range(1, len(temp)):
					img = self.get_concat_v(img, temp[i])
			if img.size[1] > maxChatHeight:
				img = img.crop((0, img.size[1]-maxChatHeight, w, img.size[1]))
			self.canvas.paste(img, (0,184))
		else:
			blank = Image.new('RGB', (w, maxChatHeight), color=self.bg)
			self.canvas.paste(blank, (0,184))

	def createBubble(self, avatar, text, side):
		def breakWord(word):
			lst = []
			while word:
				indx = 0
				for i in range(1, len(word)+1):
					part = word[:i]
					width = getTextSize(part)[0]
					if width <= maxTextWidth:
						indx = i
					else:
						break
				lst.append(word[:indx])
				word = word[indx:]
			return lst

		#break long words
		lines = []
		temp = text.split()
		splitText = []
		for word in temp:
			if getTextSize(word)[0] <= maxTextWidth:
				splitText.append(word)
			else:
				splitText += breakWord(word)

		#split text into lines
		indx = 0
		while splitText:
			for i in range(1,len(splitText)+1):
				currentLine = " ".join(splitText[:i])
				if getTextSize(currentLine)[0] <= maxTextWidth:
					indx = i
				else:
					if not pattern.findall(splitText[i-1]): #break chinese character clusters
						temp = breakWord(currentLine)
						if len(temp) > 1:
							last = temp[1]
							first = splitText[i-1][:-len(last)]
							splitText[i-2] = splitText[i-2] + " " + first
							splitText[i-1] = last
					break
			line = " ".join(splitText[:indx])
			splitText = splitText[indx:]
			lines.append(line)

		textHeight = 0
		for l in lines:
			th = getTextSize(l)[1]
			textHeight += th
		h = 2 * topMargin + 2 * bubbleTopMargin + (len(lines)-1) * bubbleLineMargin + textHeight

		#round avatar mask
		corner = Image.new('RGBA', (10,10), (0,0,0,0))
		cornerDraw = ImageDraw.Draw(corner)
		cornerDraw.pieslice((0,0, 20, 20), 180, 270, fill="black")
		sq = Image.new('RGBA', (86,86), "black")
		sq.paste(corner, (0,0))
		sq.paste(corner.rotate(90), (0, 86-10))
		sq.paste(corner.rotate(180), (86-10, 86-10))
		sq.paste(corner.rotate(270), (86-10, 0))
		
		longestLineLength = max(getTextSize(l)[0] for l in lines)
		if longestLineLength <= 535:
			bubbleWidth = longestLineLength + 2 * 30
			bubbleSideMargin = 30
		else:
			bubbleWidth = fixedBubbleWidth
			bubbleSideMargin = (fixedBubbleWidth - max(getTextSize(l)[0] for l in lines))/2

		bubbleHeight = 2 * bubbleTopMargin + (len(lines)-1) * bubbleLineMargin + textHeight + 7

		#round bubble corners
		bubbleMask = Image.new('RGBA', (bubbleWidth, bubbleHeight), "black")
		bubbleMask.paste(corner, (0,0))
		bubbleMask.paste(corner.rotate(90), (0, bubbleHeight-10))
		bubbleMask.paste(corner.rotate(180), (bubbleWidth-10, bubbleHeight-10))
		bubbleMask.paste(corner.rotate(270), (bubbleWidth-10, 0))

		def getUserCanvas():
			userCanvas = Image.new('RGB', (w, h), color=self.bg)
			if side == "left":
				userCanvas.paste(avatar, (sideMargin, topMargin), mask=sq)
				bubbleColour = self.leftBubbleBase
				textColour = self.leftText
			elif side == "right":
				userCanvas.paste(avatar, (w-sideMargin-86, topMargin), mask=sq)
				bubbleColour = self.rightBubbleBase
				textColour = self.rightText

			bubble = Image.new('RGB', (bubbleWidth, bubbleHeight), color=bubbleColour)
			bubbleCanvas = Image.new('RGB', (bubbleWidth, bubbleHeight), color=self.bg)
			bubbleCanvas.paste(bubble, (0,0), mask=bubbleMask)

			bubbleDraw = ImageDraw.Draw(bubbleCanvas)
			
			yincrement = 0

			for l in lines:
				drawText(bubbleDraw, bubbleSideMargin, bubbleTopMargin+yincrement, l, textColour)
				yincrement += bubbleLineMargin + getTextSize(l)[1]

			if side == "left":
				speechBubble = self.get_concat_h(self.leftArrow, bubbleCanvas)
				userCanvas.paste(speechBubble, (sideMargin+86, topMargin))
			elif side == "right":
				speechBubble = self.get_concat_h(bubbleCanvas, self.rightArrow)
				arrowWidth = greenarrow.size[0]
				userCanvas.paste(speechBubble, (w-bubbleWidth-2*arrowWidth-86, topMargin))
			return userCanvas

		if self.mode == "light":
			self.entries.append(getUserCanvas())
			self.mode = "dark"
			self.setMode()
			self.entriesDark.append(getUserCanvas())
			self.mode = "light"
			self.setMode()

		elif self.mode == "dark":
			self.entriesDark.append(getUserCanvas())
			self.mode = "light"
			self.setMode()
			self.entries.append(getUserCanvas())
			self.mode = "dark"
			self.setMode()


	def get(self):
		return self.canvas

	def get_concat_h(self, im1, im2):
	    dst = Image.new('RGB', (im1.width + im2.width, max(im1.height,im2.height)), color=self.bg)
	    dst.paste(im1, (0, 0))
	    dst.paste(im2, (im1.width, 0))
	    return dst

	def get_concat_v(self, im1, im2):
	    dst = Image.new('RGB', (max(im1.width, im2.width), im1.height + im2.height), color=self.bg)
	    dst.paste(im1, (0, 0))
	    dst.paste(im2, (0, im1.height))
	    return dst

def sortText(text):
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

def getTextSize(text, title=False):
	new = Screenshot("light")
	canvas = new.get()
	draw = ImageDraw.Draw(canvas)
	if not text:
		return (0, 0)

	w, h = 0, 0
	seq = sortText(text)

	if pattern.findall(seq[0]): #first element is not chinese
		if title:
			ft = enTitleFont

			for el in seq:
				tw, th = draw.textsize(el, font=ft)
				w += tw
				if th > h:
					h = th
				if ft == enTitleFont:
					ft = cnTitleFont
				else:
					ft = enTitleFont

		else:
			ft = enTextFont

			for el in seq:
				tw, th = draw.textsize(el, font=ft)
				w += tw
				if th > h:
					h = th
				if ft == enTextFont:
					ft = cnTextFont
				else:
					ft = enTextFont
	else:
		if title:
			ft = cnTitleFont

			for el in seq:
				tw, th = draw.textsize(el, font=ft)
				w += tw
				if th > h:
					h = th
				if ft == enTitleFont:
					ft = cnTitleFont
				else:
					ft = enTitleFont

		else:
			ft = cnTextFont

			for el in seq:
				tw, th = draw.textsize(el, font=ft)
				w += tw
				if th > h:
					h = th
				if ft == enTextFont:
					ft = cnTextFont
				else:
					ft = enTextFont

	return (w, h)

def drawText(imgDrawObj, xcoord, ycoord, text, fill, title=False):
	draw = imgDrawObj
	seq = sortText(text)

	if pattern.findall(seq[0]): #first element is not chinese
		if title:
			ft = enTitleFont

			for el in seq:
				draw.text((xcoord, ycoord), el, font=ft, fill=fill)
				tw, th = draw.textsize(el, font=ft)
				if ft == enTitleFont:
					ft = cnTitleFont
				else:
					ft = enTitleFont
				xcoord += tw
		else:
			ft = enTextFont

			for el in seq:
				draw.text((xcoord, ycoord), el, font=ft, fill=fill)
				tw, th = draw.textsize(el, font=ft)
				if ft == enTextFont:
					ft = cnTextFont
				else:
					ft = enTextFont
				xcoord += tw
	else:
		if title:
			ft = cnTitleFont

			for el in seq:
				draw.text((xcoord, ycoord), el, font=ft, fill=fill)
				tw, th = draw.textsize(el, font=ft)
				if ft == enTitleFont:
					ft = cnTitleFont
				else:
					ft = enTitleFont
				xcoord += tw
		else:
			ft = cnTextFont

			for el in seq:
				draw.text((xcoord, ycoord), el, font=ft, fill=fill)
				tw, th = draw.textsize(el, font=ft)
				if ft == enTextFont:
					ft = cnTextFont
				else:
					ft = enTextFont
				xcoord += tw

def loadAvatar(avypath):
	avatar = Image.open(avypath)
	avatar = avatar.resize((86,86))
	return avatar

# 63,38
# system time dark colour fcfcfc
# system time light colour 070707
#fonts
enTitleFont = ImageFont.truetype('files\\sf-ui-display-semibold-58646eddcae92.otf', 32)
enTextFont = ImageFont.truetype('files\\sf-ui-display-medium-58646be638f96.otf', 32)
cnTitleFont = ImageFont.truetype('files\\PingFang Bold.ttf', 32)
cnTextFont = ImageFont.truetype('files\\PingFang Medium.ttf', 32)
timeFont = ImageFont.truetype('files\\sf-ui-display-medium-58646be638f96.otf', 28)
system_time_font = ImageFont.truetype('files\\SFPRODISPLAYBOLD.OTF', 32)

#constants
pattern = re.compile("[\\dA-Za-z\\s.,\"$%!?:()-\u2014;\u00e9]+")
w, h = 828, 1792
topMargin = 14
sideMargin = 25
fixedBubbleWidth = 595
maxTextWidth = fixedBubbleWidth - 50
bubbleTopMargin = 17
bubbleLineMargin = 20
timeMarkerHeight = 34
maxChatHeight = 1434

#images
titlebar = Image.open('files\\chattitle.png')
inputbox = Image.open('files\\inputbox.png')
whitearrow = Image.open('files\\speechbubblewhitearrow.png')
greenarrow = Image.open('files\\speechbubblegreenarrow.png')
system_time_bar = Image.open('files\\systemtimebarlight.png')

titlebarDark = Image.open('files\\chattitledark.png')
inputboxDark = Image.open('files\\inputboxdark.png')
darkarrow = Image.open('files\\speechbubbledarkarrow.png')
greenarrowDark = Image.open('files\\speechbubblegreenarrowdark.png')
system_time_bar_dark = Image.open('files\\systemtimebardark.png')
