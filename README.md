# WeChat Screenshot Generator
A Tkinter GUI program written to generate WeChat screenshots. Offers support for Chinese characters, custom avatars and dark mode. The phone template used here is iPhone 11.

## Table of Contents
* [Installation](#installation)
* [Main Interface](#main-interface)
* [Adding an Entry](#adding-an-entry)
* [Dark Mode Support](#dark-mode-support)
* [Compiling to EXE](#compiling-to-exe)

## Installation
```
$ git clone https://github.com/csjaugustus/iphone-wechat-screenshot-generator.git
```
```
$ pip install -r requirements.txt
```
```
$ main.py
```

## Main Interface
<img src="https://user-images.githubusercontent.com/61149391/211152064-0544136d-f559-4a88-8ec9-63d71b2951cd.png" width=50% height=50%>
Top: Configure system time, chat title, and battery percentage.
Right: View existing chat bubbles.
Bottom: Copy non-blank portion of generated image to clipboard (either with or without name), save entire screenshot, add/delete entries, clear screen.

## Adding an Entry
<img src="https://user-images.githubusercontent.com/61149391/211152220-6afc3251-5046-4ea6-aabe-7dfd715fabb3.png" width=50% height=50%>
Save your square avatars under files\avatars in either .png or .jpg format. They do not need to be manually resized. You do not need to select an avatar or side if you are adding a timestamp.

## Dark Mode Support
<img src="https://user-images.githubusercontent.com/61149391/211193779-bf2fc70c-bf9d-4248-86f3-142b93bbd45b.png" width=50% height=50%>
<img src="https://user-images.githubusercontent.com/61149391/211193794-46f696d6-5296-4a44-bf5e-ed0f26b9bb50.png" width=50% height=50%>

You can toggle between dark & light mode at any time.

## Compiling to EXE
To compile this to EXE using PyInstaller, do the following steps:

1. Navigate to this directory.
2. In the command line, type the following:
```
$ pyinstaller --icon "wechat.ico" main.py
```
3. In the folder generated in `dist`, put in `files`, `theme`, `sun-valley.tcl`.
