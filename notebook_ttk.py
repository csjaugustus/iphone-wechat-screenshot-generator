from image_processing import Chat, Moments
import re
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageOps
from datetime import datetime
from io import BytesIO
import win32clipboard

if "output" not in os.listdir():
    os.mkdir("output")

def open_images():
    files = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg;*.png")])
    return files

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

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        parent.title("WeChat Screenshot Generator")
        icon = Image.open("files\\wechat.png")
        icon = ImageTk.PhotoImage(icon)
        parent.iconphoto(True, icon)
        parent.tk.call("source", "sun-valley.tcl")
        parent.tk.call("set_theme", "light")
        parent.resizable(False, False)
        self.grid()

        self.tab_control = ttk.Notebook(self)
        self.chat_page = ChatPage(self.tab_control)
        self.moments_page = MomentsPage(self.tab_control)
        self.tab_control.add(self.chat_page, text='Chat')
        self.tab_control.add(self.moments_page, text='Moments')
        self.tab_control.grid()
        self.center_window()

    def center_window(self):
        self.parent.update()
        self.parent.minsize(self.parent.winfo_width(), self.parent.winfo_height())
        x_cordinate = int((self.parent.winfo_screenwidth() / 2) - (self.parent.winfo_width() / 2))
        y_cordinate = int((self.parent.winfo_screenheight() / 2) - (self.parent.winfo_height() / 2))
        self.parent.geometry("+{}+{}".format(x_cordinate, y_cordinate - 20))

class MomentsPage(ttk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_widgets()

    def setup_widgets(self):
        self.canvas = Moments('light')
        current_canvas = self.canvas.get()
        self.w, self.h = current_canvas.size
        image_preview = current_canvas.resize((round(self.w/2.5), round(self.h/2.5)))
        image_preview = ImageTk.PhotoImage(image_preview)
        folder_icon = Image.open("files\\foldericon.png")
        folder_icon = folder_icon.resize((25,25))
        folder_icon = ImageTk.PhotoImage(folder_icon)

        frame1 = ttk.Frame(self)

        options_frame = ttk.Frame(frame1)
        self.clear_button = ttk.Button(options_frame, text="Reset Canvas", command=self.clear)
        open_directory_button = ttk.Button(options_frame, image=folder_icon, command=self.open_dir)
        open_directory_button.image = folder_icon

        info_frame = ttk.Frame(frame1)
        set_avatar_label = ttk.Label(info_frame, text="Avatar:")
        self.avatar_entry = ttk.Entry(info_frame, width=10)
        set_avatar_button = ttk.Button(info_frame, text="Choose", command=self.set_avatar)
        set_name_label = ttk.Label(info_frame, text="Name:")
        self.name_entry = ttk.Entry(info_frame, width=10)
        set_name_button = ttk.Button(info_frame, text="Set", command=self.set_name)
        post_time_label = ttk.Label(info_frame, text="Post Time:")
        self.post_time_entry = ttk.Entry(info_frame, width=10)
        self.post_time_button = ttk.Button(info_frame, text="Set", command=self.set_post_time)

        text_frame = ttk.Frame(frame1)
        text_label = ttk.Label(text_frame, text="Enter your text here:")
        self.tb = tk.Text(text_frame, height=5, width=50)
        tb_scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        self.confirm_button = ttk.Button(text_frame, text="Confirm", command=self.set_text)

        img_frame = ttk.Frame(frame1)
        self.img_label = ttk.Label(img_frame, text="Add images (if any):")
        self.img_lb = tk.Listbox(img_frame, height=10, width=50)
        img_scrollbar = ttk.Scrollbar(img_frame, orient="vertical")
        add_img_button = ttk.Button(img_frame, text="Add", command=self.add_img)
        self.delete_img_button = ttk.Button(img_frame, text="Delete", command=self.delete_img)

        frame2 = ttk.Frame(self)

        self.mode = tk.IntVar()
        dark_mode_cb = ttk.Checkbutton(frame2, text="Dark Mode", variable=self.mode, style="Switch.TCheckbutton")
        dark_mode_cb.bind('<Button-1>', self.change_mode)
        self.image_preview_widget = ttk.Label(frame2, image=image_preview, borderwidth=2, relief="sunken")
        self.image_preview_widget.image = image_preview
        self.copy_button = ttk.Button(frame2, text="Copy", command=self.copy)

        frame3 = ttk.Frame(self)

        likes_frame = ttk.Frame(frame3)
        likes_label = ttk.Label(likes_frame, text="Likes")
        self.likes_lb = tk.Listbox(likes_frame, height=8, width=50)
        likes_scrollbar = ttk.Scrollbar(likes_frame, orient="vertical")
        self.like_entry = ttk.Entry(likes_frame, width=15)
        likes_add_button = ttk.Button(likes_frame, text="Add", command=self.add_like)
        self.likes_delete_button = ttk.Button(likes_frame, text="Delete", command=self.delete_like)

        comments_frame = ttk.Frame(frame3)
        comment_label = ttk.Label(comments_frame, text="Add comments (if any):")
        self.comments_lb = tk.Listbox(comments_frame, height=10, width=50)
        comments_scrollbar = ttk.Scrollbar(comments_frame, orient="vertical")
        add_comment_button = ttk.Button(comments_frame, text="Add", command=self.add_comment)
        self.delete_comment_button = ttk.Button(comments_frame, text="Delete", command=self.delete_comment)

        self.clear_button.config(state=tk.DISABLED)
        self.delete_img_button.config(state=tk.DISABLED)
        self.copy_button.config(state=tk.DISABLED)
        self.avatar_entry.config(state=tk.DISABLED)
        self.delete_comment_button.config(state=tk.DISABLED)
        self.likes_delete_button.config(state=tk.DISABLED)

        frame1.grid(row=0, column=0, padx=10)

        options_frame.grid(row=0, column=0, pady=15)
        info_frame.grid(row=1, column=0, pady=15)
        text_frame.grid(row=2, column=0, pady=15)
        img_frame.grid(row=3, column=0, pady=15)

        self.clear_button.grid(row=0, column=0, padx=10, pady=5)
        open_directory_button.grid(row=0, column=1)

        set_avatar_label.grid(row=0, column=0, padx=5)
        self.avatar_entry.grid(row=0,column=1)
        set_avatar_button.grid(row=0, column=2, padx=5)
        set_name_label.grid(row=1, column=0, padx=5)
        self.name_entry.grid(row=1,column=1)
        set_name_button.grid(row=1, column=2, padx=5)
        post_time_label.grid(row=2, column=0, padx=5)
        self.post_time_entry.grid(row=2, column=1, padx=5)
        self.post_time_button.grid(row=2, column=2, padx=5)

        text_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        self.tb.grid(row=1, column=0, columnspan=3)
        tb_scrollbar.grid(row=1, column=3, sticky="ns")
        tb_scrollbar.config(command=self.tb.yview)
        self.confirm_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        self.img_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        self.img_lb.grid(row=1,column=0, columnspan=3)
        img_scrollbar.grid(row=1, column=3, sticky="ns")
        img_scrollbar.config(command=self.img_lb.yview)
        add_img_button.grid(row=2, column=0, padx=5, pady=5)
        self.delete_img_button.grid(row=2,column=2, padx=5, pady=5)

        frame2.grid(row=0, column=1, padx=10)

        dark_mode_cb.grid(row=0, column=0, padx=5, pady=20)
        self.image_preview_widget.grid(row=1, column=0)
        self.copy_button.grid(row=2, column=0, padx=5, pady=10)

        frame3.grid(row=0, column=2, padx=10)
        likes_frame.grid(row=0, column=0, pady=30)
        comments_frame.grid(row=1, column=0, pady=30)

        likes_label.grid(row=0, column=0, columnspan=3, pady=5)
        self.likes_lb.grid(row=1, column=0, columnspan=3, pady=5)
        likes_scrollbar.grid(row=1, column=3, sticky="ns")
        likes_scrollbar.config(command=self.likes_lb.yview)
        self.like_entry.grid(row=2, column=0, pady=5)
        likes_add_button.grid(row=2, column=1, pady=5)
        self.likes_delete_button.grid(row=2, column=2, pady=5)

        comment_label.grid(row=0, column=0, columnspan=2, pady=5)
        self.comments_lb.grid(row=1, column=0, columnspan=2)
        comments_scrollbar.grid(row=1, column=2, sticky="ns")
        comments_scrollbar.config(command=self.comments_lb.yview)
        add_comment_button.grid(row=2, column=0, pady=5)
        self.delete_comment_button.grid(row=2, column=1, pady=5)

    def set_post_time(self):
        post_time = self.post_time_entry.get()
        self.canvas.post_time = post_time
        self.canvas.refresh()
        self.update_preview()

        # self.update_button_states()

    def add_like(self):
        like = self.like_entry.get()
        if not like.strip():
            messagebox.showerror("Error", "Input cannot be blank.")
            return
        self.canvas.likes.append(like)
        self.like_entry.delete(0, tk.END)
        self.likes_lb.insert(tk.END, like)
        self.canvas.refresh()
        self.update_preview()

        self.update_button_states()

    def delete_like(self):
        selected_index = self.likes_lb.curselection()
        if not selected_index:
            messagebox.showerror("Nothing selected", "Please select an entry to delete.")
        else:
            selected_index = selected_index[0]
            del self.canvas.likes[selected_index]
            self.likes_lb.delete(selected_index)

            self.canvas.refresh()
            self.update_preview()

            self.update_button_states()

    def add_comment(self):
        def confirm():
            commentor_name = e1.get()
            text = tb.get("1.0", tk.END)
            if not commentor_name.strip() or not text.strip():
                messagebox.showerror("Error", "Please input all fields.")
                return

            if cb_var.get():
                reply_to_name = e2.get()
                if not reply_to_name.strip():
                    messagebox.showerror("Error", "Please input all fields.")
                    return

                self.canvas.comments[commentor_name] = {
                    "reply_to_name" : reply_to_name,
                    "text" : text,
                }

            else:
                self.canvas.comments[commentor_name] = {
                    "text" : text,
                }

            self.comments_lb.insert(tk.END, text)
            add_window.destroy()
            self.canvas.refresh()
            self.update_preview()

            self.update_button_states()

        add_window = tk.Toplevel()
        add_window.resizable(False, False)
        add_window.title("Add Comment")

        l1 = ttk.Label(add_window, text="Commentor Name:")
        e1 = ttk.Entry(add_window, width=15)
        l2 = ttk.Label(add_window, text="Reply to:")
        e2 = ttk.Entry(add_window, width=15)
        tb = tk.Text(add_window, height=5, width=50)

        def change_states(event):
            if not cb_var.get():
                e2.config(state=tk.NORMAL)
            else:
                e2.config(state=tk.DISABLED)

        cb_var = tk.BooleanVar()
        cb = ttk.Checkbutton(add_window, text="Add as Reply", variable=cb_var, style="Switch.TCheckbutton")
        cb.bind('<Button-1>', change_states)
        e2.config(state=tk.DISABLED)
        confirm_button = ttk.Button(add_window, text="Confirm", command=confirm)

        cb.grid(row=0, column=0, columnspan=2)
        l1.grid(row=1, column=0)
        e1.grid(row=1, column=1)
        l2.grid(row=2, column=0)
        e2.grid(row=2, column=1)
        tb.grid(row=3, column=0, columnspan=2, pady=10)
        confirm_button.grid(row=4, column=0, columnspan=2, pady=10)

    def delete_comment(self):
        selected_index = self.comments_lb.curselection()
        if not selected_index:
            messagebox.showerror("Nothing selected", "Please select an entry to delete.")
        else:
            selected_index = selected_index[0]
            value = self.comments_lb.get(selected_index)
            for c in self.canvas.comments:
                if self.canvas.comments[c]["text"] == value:
                    del_key = c
            del self.canvas.comments[del_key]
            self.comments_lb.delete(selected_index)

            self.canvas.refresh()
            self.update_preview()

            self.update_button_states()

    def set_text(self):
        post_text = self.tb.get("1.0", tk.END)
        if not post_text.strip():
            messagebox.showerror("Error", "Input cannot be blank.")
            return
        self.canvas.post_text = post_text
        self.canvas.refresh()
        self.update_preview()

        self.update_button_states()

    def update_button_states(self):
        if self.canvas.max_y > 0:
            self.copy_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)

        if self.img_lb.get(0, tk.END):
            self.delete_img_button.config(state=tk.NORMAL)
        else:
            self.delete_img_button.config(state=tk.DISABLED)

        if self.likes_lb.get(0, tk.END):
            self.likes_delete_button.config(state=tk.NORMAL)
        else:
            self.likes_delete_button.config(state=tk.DISABLED)

        if self.comments_lb.get(0, tk.END):
            self.delete_comment_button.config(state=tk.NORMAL)
        else:
            self.delete_comment_button.config(state=tk.DISABLED)

    def get_timestamp(self):
        now = datetime.now()
        dt_string = now.strftime("%Y%d%m%H%M")
        return dt_string

    def update_preview(self):
        current_canvas = self.canvas.get_cropped()
        ccw, cch = current_canvas.size
        image_preview = current_canvas.resize((round(ccw/2.5), round(cch/2.5)))
        image_preview = ImageTk.PhotoImage(image_preview)
        self.image_preview_widget.configure(image=image_preview)
        self.image_preview_widget.image = image_preview
        self.image_preview_widget.grid(row=1, column=0)

    def add_img(self):
        files = open_images()
        for f in files:
            self.img_lb.insert(tk.END, f)
            img = Image.open(f)
            img = ImageOps.exif_transpose(img)
            self.canvas.images.append(img)
        self.canvas.refresh()
        self.update_preview()

        self.update_button_states()

    def delete_img(self):
        selected_index = self.img_lb.curselection()
        if not selected_index:
            messagebox.showerror("Nothing selected", "Please select an entry to delete.")
        else:
            selected_index = selected_index[0]
            del self.canvas.images[selected_index]
            self.img_lb.delete(selected_index)

            self.canvas.refresh()
            self.update_preview()

            self.update_button_states()

    def set_name(self):
        name = self.name_entry.get()
        self.canvas.name = name
        self.canvas.refresh()
        self.update_preview()

        self.update_button_states()

    def set_avatar(self):
        def confirm():
            avy_name = e1.get()
            if not avy_name:
                messagebox.showerror("Error", "Please select an avatar.")
                return

            self.canvas.avatar = avy_name
            self.canvas.set_avatar()
            add_window.destroy()

            self.avatar_entry.config(state=tk.NORMAL)
            self.avatar_entry.insert(0, avy_name)
            self.avatar_entry.config(state=tk.DISABLED)

            self.update_preview()
            self.update_button_states()

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
        add_window.title("Set Avatar")
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

        confirm_button = ttk.Button(add_window, text="Confirm", command=confirm)
        confirm_button.grid(row=1, column=4, columnspan=3, padx=10, pady=10)

    def copy(self):
        img = self.canvas.get_cropped()
        copy_to_clipboard(img)

    def copy_to_clipboard(self, img):
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

    def open_dir(self):
        os.startfile(os.getcwd())

    def clear(self):
        def clear_screen():
            confirmation.destroy()
            self.canvas = Moments("light")
            self.update_preview()

            self.avatar_entry.config(state=tk.NORMAL)
            self.avatar_entry.delete(0, tk.END)
            self.avatar_entry.config(state=tk.DISABLED)
            self.name_entry.delete(0, tk.END)
            self.post_time_entry.delete(0, tk.END)
            self.tb.delete("1.0", tk.END)
            self.img_lb.delete(0, tk.END)
            self.likes_lb.delete(0, tk.END)
            self.comments_lb.delete(0, tk.END)
            self.mode.set(0)

            self.update_button_states()

        confirmation = tk.Toplevel()
        confirmation.resizable(False, False)
        confirmation.title("Confirmation")
        l = ttk.Label(confirmation, text="Are you sure you want to clear the screenshot?\nAll unsaved bubbles will be erased.")
        b1 = ttk.Button(confirmation, text="Yes", command=clear_screen)
        b2 = ttk.Button(confirmation, text="No", command=confirmation.destroy)
        l.grid(row=0,column=0,columnspan=3)
        b1.grid(row=1,column=0, padx=10)
        b2.grid(row=1,column=2, padx=10)

        self.update_button_states()

    def change_mode(self, event):
        if self.canvas.mode == "light":
            self.canvas.mode = "dark"
        else:
            self.canvas.mode = "light"
        self.canvas.set_mode()
        # self.canvas.update(change_mode=True)
        self.update_preview()

class ChatPage(ttk.Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_widgets()

    def setup_widgets(self):
        self.canvas = Chat('light')
        current_canvas = self.canvas.get()
        self.w, self.h = current_canvas.size
        image_preview = current_canvas.resize((round(self.w/2.5), round(self.h/2.5)))
        image_preview = ImageTk.PhotoImage(image_preview)
        folder_icon = Image.open("files\\foldericon.png")
        folder_icon = folder_icon.resize((25,25))
        folder_icon = ImageTk.PhotoImage(folder_icon)

        frame1 = ttk.Frame(self)

        self.mode = tk.IntVar()
        dark_mode_cb = ttk.Checkbutton(frame1, text="Dark Mode", variable=self.mode, style="Switch.TCheckbutton")
        dark_mode_cb.bind('<Button-1>', self.change_mode)
        self.image_preview_widget = ttk.Label(frame1, image=image_preview, borderwidth=2, relief="sunken")
        self.image_preview_widget.image = image_preview
        self.save_button = ttk.Button(frame1, text="Save", command=self.save_screenshot)

        frame2 = ttk.Frame(self)

        options_frame = ttk.Frame(frame2)
        self.clear_button = ttk.Button(options_frame, text="Reset Canvas", command=self.clear)
        open_directory_button = ttk.Button(options_frame, image=folder_icon, command=self.open_dir)
        open_directory_button.image = folder_icon

        info_frame = ttk.Frame(frame2)
        set_time_label = ttk.Label(info_frame, text="System Time:")
        self.time_entry = ttk.Entry(info_frame, width=10)
        set_time_button = ttk.Button(info_frame, text="Set", command=self.set_system_time)
        set_battery_label = ttk.Label(info_frame, text="Battery (%):")
        self.battery_entry = ttk.Entry(info_frame, width=10)
        set_battery_button = ttk.Button(info_frame, text="Set", command=self.set_battery)
        set_title_label = ttk.Label(info_frame, text="Chat Title:")
        self.title_entry = ttk.Entry(info_frame, width=20)
        set_title_button = ttk.Button(info_frame, text="Set", command=self.set_title)

        entry_frame = ttk.Frame(frame2)
        self.img_lb = tk.Listbox(entry_frame, height=28, width=50)
        lb_scrollbar = ttk.Scrollbar(entry_frame, orient="vertical")
        add_button = ttk.Button(entry_frame, text="Add", command=self.add_entry)
        self.delete_button = ttk.Button(entry_frame, text="Delete", command=self.delete_entry)

        frame3 = ttk.Frame(self)

        top_frame = ttk.Frame(frame3)
        top_label = ttk.Label(top_frame, text="Preview w/ Name")
        top_preview = self.canvas.get_cropped_from_top()
        tpw, tph = top_preview.size
        top_preview = top_preview.resize((round(tpw/2.5), round(tph/2.5)))
        top_preview = ImageTk.PhotoImage(top_preview)
        self.crop_from_top_preview = ttk.Label(top_frame, image=top_preview, borderwidth=2, relief="sunken")
        self.crop_from_top_preview.image = top_preview
        self.copy_with_name_button = ttk.Button(top_frame, text="Copy", command=self.copy_with_name)

        bottom_frame = ttk.Frame(frame3)
        bottom_label = ttk.Label(bottom_frame, text="Preview w/o Name")
        bottom_preview = self.canvas.get_cropped_from_bottom()
        bpw, bph = bottom_preview.size
        bottom_preview = bottom_preview.resize((round(bpw/2.5), round(bph/2.5)))
        bottom_preview = ImageTk.PhotoImage(bottom_preview)
        self.crop_from_bottom_preview = ttk.Label(bottom_frame, image=bottom_preview, borderwidth=2, relief="sunken")
        self.crop_from_bottom_preview.image = bottom_preview
        self.copy_without_name_button = ttk.Button(bottom_frame, text="Copy", command=self.copy_without_name)

        self.clear_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.copy_with_name_button.config(state=tk.DISABLED)
        self.copy_without_name_button.config(state=tk.DISABLED)

        frame1.grid(row=0, column=0, padx=20)

        dark_mode_cb.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        self.image_preview_widget.grid(row=1, column=0, columnspan=2)
        self.save_button.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

        frame2.grid(row=0, column=1, padx=20)
        options_frame.grid(row=0, column=0, pady=5)
        info_frame.grid(row=1, column=0, pady=5)
        entry_frame.grid(row=2, column=0, pady=5)

        self.clear_button.grid(row=0, column=1, padx=5, pady=5)
        open_directory_button.grid(row=0, column=2)

        set_time_label.grid(row=0, column=0, padx=5)
        self.time_entry.grid(row=0, column=1)
        set_time_button.grid(row=0, column=2, padx=5)
        set_battery_label.grid(row=1, column=0, padx=5)
        self.battery_entry.grid(row=1,column=1)
        set_battery_button.grid(row=1, column=2, padx=5)
        set_title_label.grid(row=2, column=0, padx=5)
        self.title_entry.grid(row=2,column=1)
        set_title_button.grid(row=2, column=2, padx=5)

        self.img_lb.grid(row=0,column=0, columnspan=3)
        lb_scrollbar.grid(row=0, column=3, sticky="ns")
        lb_scrollbar.config(command=self.img_lb.yview)
        add_button.grid(row=1, column=0, padx=10, pady=5)
        self.delete_button.grid(row=1, column=2, padx=5, pady=5)

        frame3.grid(row=0, column=2, padx=20)
        top_frame.grid(row=0, column=0, pady=10)
        bottom_frame.grid(row=1, column=0, pady=10)

        top_label.grid(row=0, column=0, pady=5)
        self.crop_from_top_preview.grid(row=1, column=0)
        self.copy_with_name_button.grid(row=2, column=0, pady=5)

        bottom_label.grid(row=0, column=0, pady=5)
        self.crop_from_bottom_preview.grid(row=1, column=0)
        self.copy_without_name_button.grid(row=2, column=0, pady=5)


    def update_button_states(self):
        if self.img_lb.get(0) or self.canvas.title or self.canvas.battery or self.canvas.system_time:
            self.clear_button.config(state=tk.NORMAL)

            if self.img_lb.get(0):
                self.delete_button.config(state=tk.NORMAL)
                self.copy_without_name_button.config(state=tk.NORMAL)

                if self.canvas.title and self.canvas.battery and self.canvas.system_time:
                    self.copy_with_name_button.config(state=tk.NORMAL)
                    self.save_button.config(state=tk.NORMAL)
                else:
                    self.copy_with_name_button.config(state=tk.DISABLED)
                    self.save_button.config(state=tk.DISABLED)

            else:
                self.save_button.config(state=tk.DISABLED)
                self.copy_with_name_button.config(state=tk.DISABLED)
                self.copy_without_name_button.config(state=tk.DISABLED)
        else:
            self.clear_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.copy_with_name_button.config(state=tk.DISABLED)
            self.copy_without_name_button.config(state=tk.DISABLED)

    def get_timestamp(self):
        now = datetime.now()
        dt_string = now.strftime("%Y%d%m%H%M")
        return dt_string

    def update_preview(self):
        current_canvas = self.canvas.get()
        image_preview = current_canvas.resize((round(self.w/2.5), round(self.h/2.5)))
        image_preview = ImageTk.PhotoImage(image_preview)
        self.image_preview_widget.configure(image=image_preview)
        self.image_preview_widget.image = image_preview
        self.image_preview_widget.grid(row=1, column=0)

        top_preview = self.canvas.get_cropped_from_top()
        tpw, tph = top_preview.size
        top_preview = top_preview.resize((round(tpw/2.5), round(tph/2.5)))
        top_preview = ImageTk.PhotoImage(top_preview)
        self.crop_from_top_preview.configure(image=top_preview)
        self.crop_from_top_preview.image = top_preview


        bottom_preview = self.canvas.get_cropped_from_bottom()
        bpw, bph = bottom_preview.size
        bottom_preview = bottom_preview.resize((round(bpw/2.5), round(bph/2.5)))
        bottom_preview = ImageTk.PhotoImage(bottom_preview)
        self.crop_from_bottom_preview.configure(image=bottom_preview)
        self.crop_from_bottom_preview.image = bottom_preview

        self.crop_from_top_preview.grid(row=1, column=0)
        self.crop_from_bottom_preview.grid(row=1, column=0)

    def add_entry(self):
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

                self.canvas.add_timestamp(text)
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

                self.canvas.add(avy_name, text, side)
                add_window.destroy()

            self.img_lb.insert(tk.END, text)
            self.update_button_states()

            self.update_preview()

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


    def delete_entry(self):
        selected_index = self.img_lb.curselection()
        if not selected_index:
            messagebox.showerror("Nothing selected", "Please select an entry to delete.")
        else:
            selected_index = selected_index[0]
            self.canvas.delete(selected_index)
            self.img_lb.delete(selected_index)

            self.update_button_states()
            self.update_preview()

    def save_screenshot(self):
        d = f"output\\SS-{self.get_timestamp()}.png"
        current_canvas = self.canvas.get()
        current_canvas.save(d)
        messagebox.showinfo("Successful", f"Saved under {d}.")


    def set_title(self):
        title = self.title_entry.get()
        self.canvas.set_title(title)
        self.update_preview()

        self.update_button_states()

    def set_system_time(self):
        time = self.time_entry.get()
        self.canvas.set_system_time(time)
        self.update_preview()

        self.update_button_states()

    def copy_with_name(self):
        img = self.canvas.get_cropped_from_top()
        copy_to_clipboard(img)

    def copy_without_name(self):
        img = self.canvas.get_cropped_from_bottom()
        copy_to_clipboard(img)

    def open_dir(self):
        os.startfile(os.getcwd())

    def clear(self):
        def clear_screen():
            confirmation.destroy()
            self.canvas.entries.clear()
            self.canvas.entries_dark.clear()
            self.img_lb.delete(0,'end')
            self.canvas = Chat('light')
            self.mode.set(0)
            self.canvas.update()
            self.update_preview()
            self.update_button_states()

        confirmation = tk.Toplevel()
        confirmation.resizable(False, False)
        confirmation.title("Confirmation")
        l = ttk.Label(confirmation, text="Are you sure you want to clear the screenshot?\nAll unsaved bubbles will be erased.")
        b1 = ttk.Button(confirmation, text="Yes", command=clear_screen)
        b2 = ttk.Button(confirmation, text="No", command=confirmation.destroy)
        l.grid(row=0,column=0,columnspan=3)
        b1.grid(row=1,column=0, padx=10)
        b2.grid(row=1,column=2, padx=10)


    def change_mode(self, event):
        if self.canvas.mode == "light":
            self.canvas.mode = "dark"
        else:
            self.canvas.mode = "light"
        self.canvas.set_mode()
        self.canvas.update(change_mode=True)
        self.update_preview()

    def set_battery(self):
        perc = self.battery_entry.get()
        if perc:
            if not perc.isdigit() or int(perc) < 1 or int(perc) > 100:
                messagebox.showerror("Invalid Input", "Please enter a whole number between 1 and 100.")
                self.battery_entry.delete(0, tk.END)
                return
            else:
                perc = int(perc)

        self.canvas.set_battery(perc)
        self.update_preview()

        self.update_button_states()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.mainloop()
