from os import remove
import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
import random
import os

WIDTH = 384
HEIGHT = 256
rows, cols = 100, 25
intensity_histogram = [[0 for _ in range(cols)] for _ in range(rows)]
color_histogram = [[0 for _ in range(64)] for _ in range(rows)]
current_selected_img = ("", -1)

# Pagination variables
current_page = 0
images_per_page = 20
columns_per_row = 5  # Number of columns to display
rows_per_page = 4  # Number of rows per page

# Adjust size for images
target_size = 180  # Size of each thumbnail image
max_selected_size = 1200  # Maximum size for the selected image

# Store the relevance of each image
image_relevance = {}


def randomize(arr):
    random.shuffle(arr)
    display_images()


def show_selected_image(tk_image, image_path, n):
    global current_selected_img

    # Open the original image
    img = Image.open(image_path)
    current_selected_img = (image_path, n)

    # Get the original dimensions of the image
    original_width, original_height = img.size
    new_width = original_width * 2
    new_height = original_height * 2
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    large_image = ImageTk.PhotoImage(img)

    selected_image_label.config(image=large_image)
    selected_image_label.image = large_image


def display_images():
    # Clear all widgets in the scrollable frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    # Calculate the starting and ending indices for the current page
    start_index = current_page * images_per_page
    end_index = start_index + images_per_page

    # Get the images for the current page
    images_to_display = photo_images[start_index:end_index]

    # Loop through photo_images to display the images as buttons
    for i, (tk_image, image_path, n) in enumerate(images_to_display):
        # Create a frame to hold the button, checkbox, and the label
        frame = tk.Frame(scrollable_frame)

        # Create the button for the image
        button = tk.Button(
            frame,
            image=tk_image,
            command=lambda img=tk_image, path=image_path, num=n: show_selected_image(
                img, path, num
            ),
        )
        button.pack(side="top")  # Stack the image button at the top

        # Create a label to show the image name (basename)
        image_name = image_path.name  # Get the name of the file
        label = tk.Label(frame, text=image_name)
        label.pack(side="top")  # Stack the label below the checkbox

        # Create a checkbox for relevance
        var = tk.IntVar(
            value=image_relevance.get(n, 0)
        )  # Default to current relevance state
        checkbox = tk.Checkbutton(
            frame,
            text="Relevant",
            variable=var,
            command=lambda n=n, var=var: update_relevance(n, var),
        )
        checkbox.pack(side="top")  # Stack the checkbox below the image button

        # Arrange the frame in a grid, with 5 columns
        frame.grid(row=i // columns_per_row, column=i % columns_per_row, padx=5, pady=5)


def update_relevance(index, var):
    """Update the relevance state of an image."""
    image_relevance[index] = var.get()
    if var.get() == 0:
        image_relevance.pop(index)
    print(image_relevance)


def sort_by_distance(photo_arr, histogram):
    global current_selected_img  # Access the global variable
    if current_selected_img[1] == -1:
        print("No image selected")
        return  # Exit if no image is selected
    reset_images()
    distances = []

    selected_histogram = histogram[
        current_selected_img[1]
    ]  # Selected image's histogram

    for x in range(len(histogram)):
        calculated_distance = 0
        for y in range(len(histogram[x])):
            calculated_distance += abs(
                float((selected_histogram[y] - histogram[x][y]) / (WIDTH * HEIGHT))
            )
        distances.append(calculated_distance)

    # Sorting photo_arr based on the calculated distances
    sorted_photo_arr = [
        photo for _, photo in sorted(zip(distances, photo_arr), key=lambda x: x[0])
    ]

    # Update the global photo_images with the sorted array
    photo_images[:] = sorted_photo_arr  # Update in place

    # Display images in sorted order
    display_images()


def reset_images():
    global photo_images, image_relevance
    # Sort photo_images based on the image names (file names)
    photo_images.sort(key=lambda x: x[1].name)
    display_images()


def reset_images_button():
    global photo_images, image_relevance
    # Sort photo_images based on the image names (file names)
    photo_images.sort(key=lambda x: x[1].name)
    image_relevance.clear()
    display_images()


def previous_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        display_images()


def next_page():
    global current_page
    if (current_page + 1) * images_per_page < len(photo_images):
        current_page += 1
        display_images()


# Create the main window
window = tk.Tk()
window.title("100 Images Viewer")

# Set window size and background color for a cleaner UI
window.geometry("800x600")
window.configure(bg="#f0f0f0")

# Create a frame for the selected image and buttons, aligned on the right
top_frame = tk.Frame(window, bg="#e6e6e6", borderwidth=2, relief="solid")
top_frame.pack(side="right", fill="y", padx=10, pady=10)

# Create a label to display the selected image with padding
selected_image_label = tk.Label(
    top_frame, text="No Image Selected", bg="white", borderwidth=2, relief="solid"
)
selected_image_label.pack(side="top", padx=10, pady=10, fill="both", expand=True)

# Create a frame for buttons below the image display
button_frame = tk.Frame(top_frame, bg="#e6e6e6")
button_frame.pack(side="bottom", fill="both", expand=True)

# Sort by Intensity button
intensity_button = tk.Button(
    button_frame,
    text="Sort by Intensity",
    width=20,
    height=2,
    bg="#d3d3d3",  # Light gray for neutral actions
    fg="#000000",  # Black text for clarity
    command=lambda: sort_by_distance(photo_images, intensity_histogram),
)
intensity_button.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

# Sort by Color Code button
colorcode_button = tk.Button(
    button_frame,
    text="Sort by Color Code",
    width=20,
    height=2,
    bg="#87ceeb",  # Light blue to differentiate this button
    fg="#000000",
    command=lambda: sort_by_distance(photo_images, color_histogram),
)
colorcode_button.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# Reset Images button
reset_button = tk.Button(
    button_frame,
    text="Reset Images",
    width=20,
    height=2,
    bg="#ffcccb",  # Light red to indicate this is a reset function
    fg="#000000",
    command=reset_images_button,
)
reset_button.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

# Navigation buttons for pages
prev_button = tk.Button(
    button_frame,
    text="Previous Page",
    width=20,
    height=2,
    command=previous_page,
)
prev_button.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

next_button = tk.Button(
    button_frame,
    text="Next Page",
    width=20,
    height=2,
    command=next_page,
)
next_button.grid(
    row=3, column=1, padx=10, pady=5, sticky="nsew"
)  # Placed next to prev_button

# Configure grid weights for responsive buttons
button_frame.grid_rowconfigure(0, weight=1)  # Ensure the rows can expand
button_frame.grid_rowconfigure(1, weight=1)
button_frame.grid_rowconfigure(2, weight=1)
button_frame.grid_rowconfigure(3, weight=1)
button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)  # Added column for next_button

# Create a scrollable frame for image thumbnails on the left
scrollable_frame = tk.Frame(window, bg="#f9f9f9")

# Pack the scrollable frame in the main window
scrollable_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

folder_name = "images"  # Replace with your folder name

# Create a Path object
current_directory = Path.cwd()
folder_path = current_directory / folder_name

image_folder = folder_path

# Use a wildcard to match .jpg images
image_paths = list(image_folder.glob("*.jpg"))

# Limit to 100 images if there are more
image_paths = image_paths[:100]

# Keep a reference to the PhotoImage objects to avoid garbage collection
photo_images = []

# Define the maximum dimensions for the grid cells
counter = 0
for image_path in image_paths:
    img = Image.open(image_path)  # Open the image file
    # Image Processing
    width, height = img.size

    # Crop the image to a square (take the smallest dimension)
    min_dimension = min(width, height)
    img_cropped = img.crop((0, 0, min_dimension, min_dimension))

    # Create a square thumbnail for the image
    img_cropped.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
    tk_image = ImageTk.PhotoImage(img_cropped)

    # Create histograms
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            rgbvals = pixels[x, y]
            intensity = int(
                rgbvals[0] * 0.299 + rgbvals[1] * 0.587 + rgbvals[2] * 0.114
            )
            histobin = int(intensity / 10)
            if histobin == 25:
                histobin -= 1
            intensity_histogram[counter][histobin] += 1
            # Assuming color histogram bins are set for RGB values
            colorcode = 0
            if rgbvals[0] >= 192:
                colorcode += 48
            elif rgbvals[0] >= 128:
                colorcode += 32
            elif rgbvals[0] >= 64:
                colorcode += 16
            if rgbvals[1] >= 192:
                colorcode += 12
            elif rgbvals[1] >= 128:
                colorcode += 8
            elif rgbvals[1] >= 64:
                colorcode += 4
            if rgbvals[2] >= 192:
                colorcode += 3
            elif rgbvals[2] >= 128:
                colorcode += 2
            elif rgbvals[2] >= 64:
                colorcode += 1
            color_histogram[counter][colorcode] += 1

    # Add the image to the list with its path and index
    photo_images.append((tk_image, image_path, counter))
    counter += 1

# Initial image display
display_images()

# Start the main event loop
window.mainloop()
