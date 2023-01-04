# WeChat Screenshot Generator
A Tkinter GUI program written to generate WeChat screenshots. Offers support for Chinese characters, custom avatars and dark mode.

## Table of Contents
* [Installation](#installation)
* [Main Interface](#main-interface)
* [Adding an Entry](#adding-an-entry)
* [Saving Images](#saving-images)
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
<img src="https://user-images.githubusercontent.com/61149391/210511380-58821842-fa98-49f1-9f2b-e20c7f92956e.png" width=50% height=50%>
On the right you can set the chat title and add new speech bubbles, and on the left the changes are reflected in the preview image area.

## Adding an Entry
<img src="https://user-images.githubusercontent.com/61149391/128868975-d398fab7-2c2e-44f1-9f06-90dbadee1c19.png" width=50% height=50%>
Save your square avatars under files\avatars in either .png or .jpg format. They do not need to be manually resized. You do not need to select an avatar or side if you are adding a time marker.

## Saving Images
<img src="https://user-images.githubusercontent.com/61149391/210512702-ab926b27-e1fc-4f11-bf7b-d4c1a270ba61.png" width=50% height=50%>
You can choose to either save the entire screenshot. Outputs will be saved under the "output" folder, which will be automatically created. Alternatively, you can choose to "copy screenshot", which will copy to clipboard non-blank parts of the screenshot.

## Dark Mode Support
<img src="https://user-images.githubusercontent.com/61149391/210512615-7eee7bcf-1e6a-40c9-9fdd-488e1ec6b1b3.png" width=50% height=50%>
You can toggle between dark & light mode at any time.

## Compiling to EXE
To compile this to EXE using PyInstaller, do the following steps:

1. Navigate to this directory.
2. In the command line, type the following:
```
$ pyinstaller --icon "wechat.ico" main.py
```
3. In the folder generated in `dist`, put in `files`, `theme`, `sun-valley.tcl`.
