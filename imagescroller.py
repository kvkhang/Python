import tkinter as tk
from tkinter import Scrollbar, Canvas, Frame
from turtle import color
from PIL import Image, ImageTk  # Pillow for handling image formats
import glob
from pathlib import Path
import random

rows, cols = 100, 25
intensity_histogram = [[0 for _ in range(cols)] for _ in range(rows)]
color_histogram = [[0 for _ in range(64)] for _ in range(rows)]
current_selected_img = ""


def randomize(arr):
    random.shuffle(arr)  # Shuffle the array in place


# Function to show the selected image in a larger view
def show_selected_image(tk_image, image_path):
    # Open the original image
    img = Image.open(image_path)
    current_selected_img = image_path

    # Get the original dimensions of the image
    original_width, original_height = img.size

    # Double the size of the image
    new_width = original_width * 2
    new_height = original_height * 2

    # Resize the image while maintaining its original aspect ratio
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Convert to a Tkinter-compatible image
    large_image = ImageTk.PhotoImage(img)

    # Update the displayed image
    selected_image_label.config(image=large_image)
    selected_image_label.image = (
        large_image  # Keep a reference to avoid garbage collection
    )


# Function to display images as buttons
def display_images():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()  # Clear existing images

    for i, (tk_image, image_path) in enumerate(photo_images):
        button = tk.Button(
            scrollable_frame,
            image=tk_image,
            command=lambda img=tk_image, path=image_path: show_selected_image(
                img, path
            ),
        )
        button.grid(
            row=i // 10, column=i % 10, padx=5, pady=5
        )  # Arrange images in a grid


# Function to sort by Intensity

# Create the main window
window = tk.Tk()
window.title("100 Images Viewer")

# Create a frame for the selected image and buttons
top_frame = tk.Frame(window)
top_frame.pack(side="top", fill="x", padx=10, pady=10)  # Fill horizontally

# Create a label to display the selected image
selected_image_label = tk.Label(top_frame)
selected_image_label.pack(side="left")  # Position it on the left of the frame

# Create a frame for buttons
button_frame = tk.Frame(top_frame)
button_frame.pack(side="right", expand=True)  # Use expand to allow for centering

rows, columns = 2, 1
# Create a grid for buttons
for i in range(rows):
    for j in range(columns):
        button = tk.Button(
            button_frame, text=f"Button {i * 2 + j + 1}", width=15, height=2
        )
        button.grid(
            row=i, column=j, padx=5, pady=5, sticky="nsew"
        )  # Sticky to fill the cell

button = tk.Button(
    button_frame,
    text="Sort by Intensity",
    width=15,
    height=2,
    command=lambda: randomize(),
)

# Configure grid weights to make it center
for i in range(2):
    button_frame.grid_rowconfigure(i, weight=1)  # Allow rows to expand
for j in range(4):
    button_frame.grid_columnconfigure(j, weight=1)  # Allow columns to expand

# Create a scrollable canvas
canvas = Canvas(window)
scrollbar = Scrollbar(window, orient="vertical", command=canvas.yview)
scrollable_frame = Frame(canvas)

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Add the scrollable frame to the canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Pack the canvas and scrollbar in the main window
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Get the home directory of the user
home_dir = Path.home()

# Define a relative path from the home directory to the images folder
image_folder = home_dir / "Python" / "images"

# Use a wildcard to match .jpg images
image_paths = list(image_folder.glob("*.jpg"))

# Limit to 100 images if there are more
image_paths = image_paths[:100]

# Keep a reference to the PhotoImage objects to avoid garbage collection
photo_images = []

# Define the maximum dimensions for the grid cells
max_width, max_height = 160, 160

# Define the target dimensions for the grid cells (150x150)
target_size = 150
counter = 0
for image_path in image_paths:
    img = Image.open(image_path)  # Open the image file

    # Image Processing
    width, height = img.size
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            rgbvals = pixels[x, y]
            intensity = (int)(
                rgbvals[0] * 0.299 + rgbvals[1] * 0.587 + rgbvals[2] * 0.114
            )
            histobin = (int)(intensity / 10)
            if histobin == 25:
                histobin -= 1
            intensity_histogram[counter][histobin] += 1

    counter += 1
    # Get the original dimensions of the image
    width, height = img.size

    # Determine the dimensions to crop a square
    if width > height:
        # Crop width to make it a square
        left = (width - height) // 2
        right = left + height
        top, bottom = 0, height
    else:
        # Crop height to make it a square
        top = (height - width) // 2
        bottom = top + width
        left, right = 0, width

    # Crop the image to a square
    img = img.crop((left, top, right, bottom))

    # Resize the square image to fit the grid cell
    img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

    tk_image = ImageTk.PhotoImage(img)  # Convert image to PhotoImage
    photo_images.append((tk_image, image_path))  # Keep a reference and the file path

# Display images initially
display_images()

# Start the Tkinter event loop
window.mainloop()
