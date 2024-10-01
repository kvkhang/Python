import tkinter as tk
from tkinter import Scrollbar, Canvas, Frame
from PIL import Image, ImageTk  # Pillow for handling image formats
import glob
import random


def randomize(arr):
    random.shuffle(arr)  # Shuffle the array in place


# Create the main window
window = tk.Tk()
window.title("100 Images Viewer")

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

# Load and display images (adjust the path and use a wildcard to match multiple images)
image_paths = glob.glob(
    r"C:\Users\Khang\Python\images\*.jpg"
)  # Load all jpg images from the folder

# Limit to 100 images if there are more
image_paths = image_paths[:100]

# Keep a reference to the PhotoImage objects to avoid garbage collection
photo_images = []

for image_path in image_paths:
    img = Image.open(image_path)  # Open the image file
    img = img.resize((150, 150))  # Resize the image to fit within the grid

    tk_image = ImageTk.PhotoImage(img)  # Convert image to PhotoImage
    photo_images.append(tk_image)  # Keep a reference


# Function to display images
def display_images():
    for widget in scrollable_frame.winfo_children():
        widget.destroy()  # Clear existing images

    for i, tk_image in enumerate(photo_images):
        label = tk.Label(scrollable_frame, image=tk_image)
        label.grid(
            row=i // 10, column=i % 10, padx=5, pady=5
        )  # Arrange images in a grid


# Display images initially
display_images()

# Button to randomize and display images
button = tk.Button(
    window,
    text="Shuffle Images",
    command=lambda: (randomize(photo_images), display_images()),
)
button.pack()

# Start the Tkinter event loop
window.mainloop()
