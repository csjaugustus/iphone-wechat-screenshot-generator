import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFont


root = tk.Tk()
root.configure(bg = 'white')
root.title("Drag and drop window for loading images")

def open_images():
    files = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg;*.png")])
    for f in files:
        img = Image.open(f)
        # img.thumbnail((360, 360))
        img = crop_center_sq(img).resize((173,173))
        img.show()

def crop_center_sq(img):
    w, h = img.size
    sq_length = min(w, h)
    center_x = w / 2
    center_y = h / 2

    x1 = center_x - (sq_length / 2)
    y1 = center_y - (sq_length / 2)

    return img.crop((x1, y1, x1 + sq_length, y1 + sq_length))

open_image_button = ttk.Button(root, text='Open Images', command=open_images)
open_image_button.pack()

root.mainloop()
