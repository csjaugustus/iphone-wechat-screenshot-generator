from image_processing import Screenshot
import re
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from datetime import datetime
from io import BytesIO
import win32clipboard

def update_button_states():
	if lb.get(0) or title_is_set or battery_is_set or system_time_is_set:
		clear_button.config(state=tk.NORMAL)

		if lb.get(0):
			delete_button.config(state=tk.NORMAL)
			copy_without_name_button.config(state=tk.NORMAL)

			if title_is_set and battery_is_set and system_time_is_set:
				copy_with_name_button.config(state=tk.NORMAL)
				save_button.config(state=tk.NORMAL)
			else:
				copy_with_name_button.config(state=tk.DISABLED)
				save_button.config(state=tk.DISABLED)

		else:
			save_button.config(state=tk.DISABLED)
			copy_with_name_button.config(state=tk.DISABLED)
			copy_without_name_button.config(state=tk.DISABLED)
	else:
		clear_button.config(state=tk.DISABLED)
		delete_button.config(state=tk.DISABLED)
		save_button.config(state=tk.DISABLED)
		copy_with_name_button.config(state=tk.DISABLED)
		copy_without_name_button.config(state=tk.DISABLED)

def get_timestamp():
	now = datetime.now()
	dt_string = now.strftime("%Y%d%m%H%M")
	return dt_string

def update_preview():
	current_canvas = canvas.get()
	image_preview = current_canvas.resize((round(w/2.85), round(h/2.85)))
	image_preview = ImageTk.PhotoImage(image_preview)
	image_preview_widget.configure(image=image_preview)
	image_preview_widget.image = image_preview
	image_preview_widget.grid(row=2, column=0)

def add_entry():
	whitespace = re.compile("^\\s$")
	def confirm():
		if cb_var.get():
			time_regex = re.compile('^\\d{2}:\\d{2}$')
			text = e2.get("1.0", tk.END)
			errors = []
			if whitespace.findall(text):
				errors.append("Please enter some text.")
			# elif not time_regex.findall(text):
			#   errors.append("Please enter a valid time in such format xx:xx.")
			if errors:
				messagebox.showerror("Error", "\n".join(e for e in errors))
				return

			canvas.add_timestamp(text)
			add_window.destroy()

		else:
			side = var.get()
			text = e2.get("1.0", tk.END)
			avy_name = e1.get()

			#check for errors
			errors = []
			if not avy_name:
				errors.append("Please select an avatar.")
			if whitespace.findall(text):
				errors.append("Please enter some text.")
			if errors:
				messagebox.showerror("Error", "\n".join(e for e in errors))
				return

			canvas.add(avy_name, text, side)
			add_window.destroy()

		lb.insert(tk.END, text)
		update_button_states()

		update_preview()

	def select_avatar(x):
		e1.config(state=tk.NORMAL)
		e1.delete(0, tk.END)
		e1.insert(0, x)
		e1.config(state=tk.DISABLED)

	if not os.listdir("files\\avatars"):
		messagebox.showerror("Error", "No avatar image found. Please add at least one avatar image in files\\avatars.")
		return

	add_window = tk.Toplevel()
	add_window.resizable(False, False)
	add_window.title("Add Entry")
	r, c = 0, 0

	avy_buttons = []
	for avy_name in os.listdir("files\\avatars"):
		avy_image = Image.open(f"files\\avatars\\{avy_name}")
		avy_image = avy_image.resize((50,50))
		avy_image = ImageTk.PhotoImage(avy_image)
		b = ttk.Button(add_window, image=avy_image, command=lambda x=avy_name:select_avatar(x))
		b.image = avy_image
		avy_buttons.append(b)
		b.grid(row=r, column=c)
		c += 1
		if c == 4:
			c = 0
			r += 1

	l1 = ttk.Label(add_window, text="Avatar Selected:")
	e1 = ttk.Entry(add_window, width=30)
	l1.grid(row=0, column=4, padx=10)
	e1.grid(row=0, column=5, columnspan=2)
	e1.config(state=tk.DISABLED)

	l2 = ttk.Label(add_window, text="Text:")
	e2 = tk.Text(add_window, height=10, width=30)
	l2.grid(row=1, column=4, padx=10)
	e2.grid(row=1, column=5,columnspan=2)

	l3 = ttk.Label(add_window, text="Side:")
	var = tk.StringVar()
	var.set(' ')
	r1 = ttk.Radiobutton(add_window, text="Left", variable=var, value="left")
	r2 = ttk.Radiobutton(add_window, text="Right", variable=var, value="right")
	l3.grid(row=2,column=4, padx=10, pady=10)
	r1.grid(row=2, column=5, pady=10)
	r2.grid(row=2, column=6, pady=10)

	def change_states(event):
		if not cb_var.get():
			r1.config(state=tk.DISABLED)
			r2.config(state=tk.DISABLED)
			e1.delete(0, tk.END)
			for b in avy_buttons:
				b.config(state=tk.DISABLED)
		else:
			r1.config(state=tk.NORMAL)
			r2.config(state=tk.NORMAL)
			for b in avy_buttons:
				b.config(state=tk.NORMAL)

	cb_var = tk.BooleanVar()
	cb = ttk.Checkbutton(add_window, text="Add as Timestamp", variable=cb_var, style="Switch.TCheckbutton")
	cb.grid(row=3, column=5, columnspan=2, padx=10, pady=10)
	cb.bind('<Button-1>', change_states)

	confirm_button = ttk.Button(add_window, text="Confirm", command=confirm)
	confirm_button.grid(row=4, column=5, columnspan=2, padx=10, pady=10)
	r1.invoke()


def delete_entry():
	selected_index = lb.curselection()
	if not selected_index:
		messagebox.showerror("Nothing selected", "Please select an entry to delete.")
	else:
		selected_index = selected_index[0]
		canvas.delete(selected_index)
		lb.delete(selected_index)

		update_button_states()
		update_preview()

def save_screenshot():
	d = f"output\\SS-{get_timestamp()}.png"
	current_canvas = canvas.get()
	current_canvas.save(d)
	messagebox.showinfo("Successful", f"Saved under {d}.")


def set_title():
	title = title_entry.get()
	canvas.set_title(title)
	update_preview()

	global title_is_set

	if title:
		title_is_set = True
	else:
		title_is_set = False
	update_button_states()

def set_system_time():
	time = time_entry.get()
	canvas.set_system_time(time)
	update_preview()

	global system_time_is_set

	if time:
		system_time_is_set = True
	else:
		system_time_is_set = False
	update_button_states()

def copy_with_name():
	img = canvas.get_cropped_from_top()
	copy_to_clipboard(img)

def copy_without_name():
	img = canvas.get_cropped_from_bottom()
	copy_to_clipboard(img)

def copy_to_clipboard(img):
	def send_to_clipboard(clip_type, data):
		win32clipboard.OpenClipboard()
		win32clipboard.EmptyClipboard()
		win32clipboard.SetClipboardData(clip_type, data)
		win32clipboard.CloseClipboard()

	output = BytesIO()
	img.convert("RGB").save(output, "BMP")
	data = output.getvalue()[14:]
	output.close()

	send_to_clipboard(win32clipboard.CF_DIB, data)

def open_dir():
	os.startfile(os.getcwd())

def clear():
	def clear_screen():
		confirmation.destroy()
		canvas.entries.clear()
		canvas.entries_dark.clear()
		lb.delete(0,'end')
		canvas.set_title("")
		canvas.set_system_time("")
		canvas.battery = ""
		title_is_set = False
		system_time_is_set = False
		battery_is_set = False
		canvas.update()
		update_preview()

	confirmation = tk.Toplevel()
	confirmation.resizable(False, False)
	confirmation.title("Confirmation")
	l = ttk.Label(confirmation, text="Are you sure you want to clear the screenshot?\nAll unsaved bubbles will be erased.")
	b1 = ttk.Button(confirmation, text="Yes", command=clear_screen)
	b2 = ttk.Button(confirmation, text="No", command=confirmation.destroy)
	l.grid(row=0,column=0,columnspan=3)
	b1.grid(row=1,column=0, padx=10)
	b2.grid(row=1,column=2, padx=10)

	clear_button.config(state=tk.DISABLED)
	delete_button.config(state=tk.DISABLED)
	save_button.config(state=tk.DISABLED)
	copy_with_name_button.config(state=tk.DISABLED)
	copy_without_name_button.config(state=tk.DISABLED)

def change_mode(event):
	if canvas.mode == "light":
		canvas.mode = "dark"
	else:
		canvas.mode = "light"
	canvas.set_mode()
	canvas.update(change_mode=True)
	update_preview()

def set_battery():
	perc = battery_entry.get()
	if perc:
		if not perc.isdigit() or int(perc) < 1 or int(perc) > 100:
			messagebox.showerror("Invalid Input", "Please enter a whole number between 1 and 100.")
			battery_entry.delete(0, tk.END)
			return
		else:
			perc = int(perc)

	canvas.set_battery(perc)
	update_preview()

	global battery_is_set

	if perc:
		battery_is_set = True
	else:
		battery_is_set = False
	update_button_states()

system_time_is_set = False
title_is_set = False
battery_is_set = False

if "output" not in os.listdir():
	os.mkdir("output")

root = tk.Tk()
root.title("WeChat Screenshot Generator")
icon = Image.open("files\\wechat.png")
icon = ImageTk.PhotoImage(icon)
root.iconphoto(True, icon)
root.tk.call("source", "sun-valley.tcl")
root.tk.call("set_theme", "light")
root.resizable(False, False)

canvas = Screenshot('light')
current_canvas = canvas.get()
w, h = current_canvas.size
image_preview = current_canvas.resize((round(w/2.85), round(h/2.85)))
image_preview = ImageTk.PhotoImage(image_preview)
image_preview_widget = ttk.Label(root, image=image_preview, borderwidth=2, relief="sunken")
folder_icon = Image.open("files\\foldericon.png")
folder_icon = folder_icon.resize((25,25))
folder_icon = ImageTk.PhotoImage(folder_icon)

save_button = ttk.Button(root, text="Save", command=save_screenshot)
set_title_label = ttk.Label(root, text="Chat Title:")
set_title_button = ttk.Button(root, text="Set", command=set_title)
set_time_label = ttk.Label(root, text="System Time:")
set_time_button = ttk.Button(root, text="Set", command=set_system_time)
set_battery_label = ttk.Label(root, text="Battery Percentage:")
set_battery_button = ttk.Button(root, text="Set", command=set_battery)
title_entry = ttk.Entry(root, width=20)
time_entry = ttk.Entry(root, width=10)
battery_entry = ttk.Entry(root, width=10)
lb = tk.Listbox(root, height=35, width=50)
add_button = ttk.Button(root, text="Add", command=add_entry)
delete_button = ttk.Button(root, text="Delete", command=delete_entry)
copy_with_name_button = ttk.Button(root, text="Copy w/ Name", command=copy_with_name)
open_directory_button = ttk.Button(root, image=folder_icon, command=open_dir)
open_directory_button.image = folder_icon
clear_button = ttk.Button(root, text="Clear", command=clear)
mode = tk.IntVar()
dark_mode_cb = ttk.Checkbutton(root, text="Dark Mode", variable=mode, style="Switch.TCheckbutton")
dark_mode_cb.bind('<Button-1>', change_mode)
copy_without_name_button = ttk.Button(root, text="Copy w/o Name", command=copy_without_name)

clear_button.config(state=tk.DISABLED)
delete_button.config(state=tk.DISABLED)
save_button.config(state=tk.DISABLED)
copy_with_name_button.config(state=tk.DISABLED)
copy_without_name_button.config(state=tk.DISABLED)

image_preview_widget.grid(row=2, column=0, columnspan=3)
dark_mode_cb.grid(row=0,column=0, columnspan=3, padx=10)
set_title_label.grid(row=0, column=3, padx=5, pady=5)
set_time_label.grid(row=1, column=0, padx=5, pady=5)
set_battery_label.grid(row=1, column=3, padx=5)
title_entry.grid(row=0,column=4)
time_entry.grid(row=1,column=1)
battery_entry.grid(row=1,column=4)
set_title_button.grid(row=0, column=5, padx=5)
set_time_button.grid(row=1, column=2, padx=5, pady=5)
set_battery_button.grid(row=1, column=5, padx=5, pady=5)
lb.grid(row=2,column=3, columnspan=4)
save_button.grid(row=3,column=2, padx=10, pady=10)
add_button.grid(row=3, column=3, padx=10, pady=10)
delete_button.grid(row=3,column=4, padx=10, pady=10)
copy_with_name_button.grid(row=3,column=1, padx=10, pady=10)
open_directory_button.grid(row=0,column=6)
clear_button.grid(row=3,column=5, padx=10, pady=10)
copy_without_name_button.grid(row=3, column=0, padx=10, pady=10)

root.update()
root.minsize(root.winfo_width(), root.winfo_height())
x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
root.geometry("+{}+{}".format(x_cordinate, y_cordinate - 20))

root.mainloop()
