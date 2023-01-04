from imageProcessing import Screenshot
import re
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from datetime import datetime
import pyperclip
from io import BytesIO
import win32clipboard

def getTimestamp():
	now = datetime.now()
	dt_string = now.strftime("%Y%d%m%H%M")
	return dt_string

def updatePreview():
	currentCanvas = canvas.get()
	imagePreview = currentCanvas.resize((round(w/2.85), round(h/2.85)))
	imagePreview = ImageTk.PhotoImage(imagePreview)
	imagePreviewWidget.configure(image=imagePreview)
	imagePreviewWidget.image = imagePreview
	imagePreviewWidget.grid(row=2, column=0)

def popupMessage(title, message, windowToClose=None):
	popupWindow = tk.Toplevel()
	popupWindow.resizable(False, False)
	popupWindow.title(title)
	if not windowToClose:
		close = popupWindow.destroy
	elif windowToClose == 'all':
		close = popupWindow.quit
	else:
		def close():
			popupWindow.destroy()
			windowToClose.destroy()
	msg = ttk.Label(popupWindow, text=message)
	ok = ttk.Button(popupWindow, text="Ok", command=close)
	msg.pack(padx=10, pady=10)
	ok.pack(padx=10, pady=10)
	

def addEntry():
	whitespace = re.compile("^\\s$")
	def confirm():
		if cbVar.get():
			timeRegex = re.compile('^\\d{2}:\\d{2}$')
			text = e2.get("1.0", tk.END)
			errors = []
			if whitespace.findall(text):
				errors.append("Please enter some text.")
			# elif not timeRegex.findall(text):
			# 	errors.append("Please enter a valid time in such format xx:xx.")
			if errors:
				popupMessage("Error", "\n".join(e for e in errors))
				return

			canvas.addTimeMarker(text)
			addWindow.destroy()

		else:
			side = var.get()
			text = e2.get("1.0", tk.END)
			avyName = e1.get()

			#check for errors
			pyperclip.copy(text)
			errors = []
			if not avyName:
				errors.append("Please select an avatar.")
			if whitespace.findall(text):
				errors.append("Please enter some text.")
			if errors:
				popupMessage("Error", "\n".join(e for e in errors))
				return

			canvas.add(avyName, text, side)
			addWindow.destroy()

		lb.insert(tk.END, text)
		clearButton.config(state=tk.NORMAL)
		deleteButton.config(state=tk.NORMAL)
		saveButton.config(state=tk.NORMAL)
		copy_screenshot_button.config(state=tk.NORMAL)

		updatePreview()

	def selectAvatar(x):
		e1.config(state=tk.NORMAL)
		e1.delete(0, tk.END)
		e1.insert(0, x)
		e1.config(state=tk.DISABLED)

	if not os.listdir("files\\avatars"):
		popupMessage("Error", "No avatar image found. Please add at least one avatar image in files\\avatars.")
		return

	addWindow = tk.Toplevel()
	addWindow.resizable(False, False)
	addWindow.title("Add Entry")
	r, c = 0, 0

	avyButtons = []
	for avyName in os.listdir("files\\avatars"):
		avyImage = Image.open(f"files\\avatars\\{avyName}")
		avyImage = avyImage.resize((50,50))
		avyImage = ImageTk.PhotoImage(avyImage)
		b = ttk.Button(addWindow, image=avyImage, command=lambda x=avyName:selectAvatar(x))
		b.image = avyImage
		avyButtons.append(b)
		b.grid(row=r, column=c)
		c += 1
		if c == 4:
			c = 0
			r += 1

	l1 = ttk.Label(addWindow, text="Avatar Selected:")
	e1 = ttk.Entry(addWindow, width=30)
	l1.grid(row=0, column=4, padx=10)
	e1.grid(row=0, column=5, columnspan=2)
	e1.config(state=tk.DISABLED)

	l2 = ttk.Label(addWindow, text="Text:")
	e2 = tk.Text(addWindow, height=10, width=30)
	l2.grid(row=1, column=4, padx=10)
	e2.grid(row=1, column=5,columnspan=2)

	l3 = ttk.Label(addWindow, text="Side:")
	var = tk.StringVar()
	var.set(' ')
	r1 = ttk.Radiobutton(addWindow, text="Left", variable=var, value="left")
	r2 = ttk.Radiobutton(addWindow, text="Right", variable=var, value="right")
	l3.grid(row=2,column=4, padx=10, pady=10)
	r1.grid(row=2, column=5, pady=10)
	r2.grid(row=2, column=6, pady=10)

	def changeStates(event):
		if r1['state'] == tk.NORMAL:
			r1.config(state=tk.DISABLED)
			r2.config(state=tk.DISABLED)
			e1.delete(0, tk.END)
			for b in avyButtons:
				b.config(state=tk.DISABLED)
		else:
			r1.config(state=tk.NORMAL)
			r2.config(state=tk.NORMAL)
			for b in avyButtons:
				b.config(state=tk.NORMAL)

	cbVar = tk.IntVar()
	cb = ttk.Checkbutton(addWindow, text="Add as Time Marker", variable=cbVar, style="Switch.TCheckbutton")
	cb.grid(row=3, column=5, columnspan=2, padx=10, pady=10)
	cb.bind('<Button-1>', changeStates)

	confirmButton = ttk.Button(addWindow, text="Confirm", command=confirm)
	confirmButton.grid(row=4, column=5, columnspan=2, padx=10, pady=10)
	r1.invoke()


def deleteEntry():
	selectedIndex = lb.curselection()
	if not selectedIndex:
		popupMessage("Nothing selected",
					 "Please select an entry to delete.")
	else:
		selectedIndex = selectedIndex[0]
		canvas.delete(selectedIndex)
		lb.delete(selectedIndex)

		if not lb.get(0):
			if not canvas.title:
				clearButton.config(state=tk.DISABLED)
				deleteButton.config(state=tk.DISABLED)
				saveButton.config(state=tk.DISABLED)
				copy_screenshot_button.config(state=tk.DISABLED)

		updatePreview()

def saveScreenshot():
	d = f"output\\SS-{getTimestamp()}.png"
	currentCanvas = canvas.get()
	currentCanvas.save(d)
	popupMessage("Successful", f"Saved under {d}.")
	

def setTitle():
	title = titleEntry.get()
	canvas.setTitle(title)
	updatePreview()

	if title:
		clearButton.config(state=tk.NORMAL)
		titleSet = True
	else:
		if not lb.get(0) and not systemTimeSet:
			clearButton.config(state=tk.DISABLED)
			deleteButton.config(state=tk.DISABLED)
			saveButton.config(state=tk.DISABLED)
			copy_screenshot_button.config(state=tk.DISABLED)

def set_system_time():
	time = timeEntry.get()
	canvas.set_system_time(time)
	updatePreview()

	if time:
		clearButton.config(state=tk.NORMAL)
		systemTimeSet = True
	else:
		if not lb.get(0) and not titleSet:
			clearButton.config(state=tk.DISABLED)
			deleteButton.config(state=tk.DISABLED)
			saveButton.config(state=tk.DISABLED)
			copy_screenshot_button.config(state=tk.DISABLED)

def copy_screenshot():
	def send_to_clipboard(clip_type, data):
	    win32clipboard.OpenClipboard()
	    win32clipboard.EmptyClipboard()
	    win32clipboard.SetClipboardData(clip_type, data)
	    win32clipboard.CloseClipboard()

	output = BytesIO()
	canvas.get().convert("RGB").save(output, "BMP")
	data = output.getvalue()[14:]
	output.close()

	send_to_clipboard(win32clipboard.CF_DIB, data)

def openDir():
	os.startfile(os.getcwd())

def clear():
	def clearScreen():
		confirmation.destroy()
		canvas.entries.clear()
		canvas.entriesDark.clear()
		lb.delete(0,'end')
		canvas.setTitle("")
		canvas.set_system_time("")
		titleSet = False
		systemTimeSet = False
		canvas.update()
		updatePreview()

	confirmation = tk.Toplevel()
	confirmation.resizable(False, False)
	confirmation.title("Confirmation")
	l = ttk.Label(confirmation, text="Are you sure you want to clear the screenshot?\nAll unsaved bubbles will be erased.")
	b1 = ttk.Button(confirmation, text="Yes", command=clearScreen)
	b2 = ttk.Button(confirmation, text="No", command=confirmation.destroy)
	l.grid(row=0,column=0,columnspan=3)
	b1.grid(row=1,column=0, padx=10)
	b2.grid(row=1,column=2, padx=10)

	clearButton.config(state=tk.DISABLED)
	deleteButton.config(state=tk.DISABLED)
	saveButton.config(state=tk.DISABLED)
	copy_screenshot_button.config(state=tk.DISABLED)

def changeMode(event):
	if canvas.mode == "light":
		canvas.mode = "dark"
	else:
		canvas.mode = "light"
	canvas.setMode()
	canvas.update(changeMode=True)
	updatePreview()

systemTimeSet = False
titleSet = False

if "output" not in os.listdir():
	os.mkdir("output")

root = tk.Tk()
root.title("WeChat Screenshot Generator")
icon = Image.open("files\\wechat-logo.png")
icon = ImageTk.PhotoImage(icon)
root.iconphoto(True, icon)
root.tk.call("source", "sun-valley.tcl")
root.tk.call("set_theme", "light")
root.resizable(False, False)

canvas = Screenshot('light')
currentCanvas = canvas.get()
w, h = currentCanvas.size
imagePreview = currentCanvas.resize((round(w/2.85), round(h/2.85)))
imagePreview = ImageTk.PhotoImage(imagePreview)
imagePreviewWidget = ttk.Label(root, image=imagePreview, borderwidth=2, relief="sunken")
folderIcon = Image.open("files\\foldericon.png")
folderIcon = folderIcon.resize((25,25))
folderIcon = ImageTk.PhotoImage(folderIcon)

saveButton = ttk.Button(root, text="Save Screenshot", command=saveScreenshot)
setTitleLabel = ttk.Label(root, text="Chat Title:")
setTitleButton = ttk.Button(root, text="Set", command=setTitle)
setTimeLabel = ttk.Label(root, text="System Time:")
setTimeButton = ttk.Button(root, text="Set", command=set_system_time)
titleEntry = ttk.Entry(root, width=20)
timeEntry = ttk.Entry(root, width=10)
lb = tk.Listbox(root, height=35, width=50)
addButton = ttk.Button(root, text="Add", command=addEntry)
deleteButton = ttk.Button(root, text="Delete", command=deleteEntry)
copy_screenshot_button = ttk.Button(root, text="Copy Screenshot", command=copy_screenshot)
openDirectoryButton = ttk.Button(root, image=folderIcon, command=openDir)
openDirectoryButton.image = folderIcon
clearButton = ttk.Button(root, text="Clear", command=clear)
mode = tk.IntVar()
darkMode = ttk.Checkbutton(root, text="Dark Mode", variable=mode, style="Switch.TCheckbutton")
darkMode.bind('<Button-1>', changeMode)

clearButton.config(state=tk.DISABLED)
deleteButton.config(state=tk.DISABLED)
saveButton.config(state=tk.DISABLED)
copy_screenshot_button.config(state=tk.DISABLED)

imagePreviewWidget.grid(row=2, column=0, columnspan=2)
darkMode.grid(row=0,column=0, columnspan=2, padx=10)
setTitleLabel.grid(row=0, column=2, padx=10, pady=10)
titleEntry.grid(row=0,column=3)
timeEntry.grid(row=1,column=3)
setTitleButton.grid(row=0, column=4, padx=10)
setTimeLabel.grid(row=1, column=2, padx=10)
setTimeButton.grid(row=1, column=4, padx=10)
lb.grid(row=2,column=2, columnspan=4)
saveButton.grid(row=3,column=1, padx=10, pady=10)
addButton.grid(row=3, column=2, padx=10, pady=10)
deleteButton.grid(row=3,column=3, padx=10, pady=10)
copy_screenshot_button.grid(row=3,column=4,columnspan=2, padx=10, pady=10)
openDirectoryButton.grid(row=0,column=5)
clearButton.grid(row=3,column=0, padx=10, pady=10)

root.update()
root.minsize(root.winfo_width(), root.winfo_height())
x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
root.geometry("+{}+{}".format(x_cordinate, y_cordinate - 20))

root.mainloop()
