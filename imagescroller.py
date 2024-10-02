import tkinter as tk
from tkinter import Scrollbar, Canvas, Frame
from PIL import Image, ImageTk  # Pillow for handling image formats
import glob
import random


def randomize(arr):
    random.shuffle(arr)  # Shuffle the array in place


# Function to show the selected image in a larger view
def show_selected_image(tk_image, image_path):
    # Resize the image for larger display
    img = Image.open(image_path)
    img = img.resize((600, 600))  # Change the size as needed
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

# Create a grid for buttons
for i in range(4):  # 2 rows
    for j in range(2):  # 4 columns
        button = tk.Button(
            button_frame, text=f"Button {i*2 + j + 1}", width=15, height=2
        )
        button.grid(
            row=i, column=j, padx=5, pady=5, sticky="nsew"
        )  # Sticky to fill the cell

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
    photo_images.append((tk_image, image_path))  # Keep a reference and the file path

# Display images initially
display_images()

# Start the Tkinter event loop
window.mainloop()
