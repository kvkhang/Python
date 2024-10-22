import tkinter as tk
from tkinter import Frame
from PIL import Image, ImageTk
from pathlib import Path
import random

WIDTH = 384
HEIGHT = 256
rows, cols = 100, 25
intensity_histogram = [[0 for _ in range(cols)] for _ in range(rows)]
color_histogram = [[0 for _ in range(64)] for _ in range(rows)]
current_selected_img = ("", -1)

# Pagination variables
current_page = 0
images_per_page = 20


def randomize(arr):
    random.shuffle(arr)  # Shuffle the array in place
    display_images()


def show_selected_image(tk_image, image_path, n):
    global current_selected_img

    img = Image.open(image_path)
    current_selected_img = (image_path, n)

    original_width, original_height = img.size
    new_width = original_width * 2
    new_height = original_height * 2
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    large_image = ImageTk.PhotoImage(img)

    selected_image_label.config(image=large_image)
    selected_image_label.image = large_image


def display_images():
    global current_page
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    start_index = current_page * images_per_page
    end_index = start_index + images_per_page
    current_images = photo_images[start_index:end_index]

    for i, (tk_image, image_path, n) in enumerate(current_images):
        frame = tk.Frame(scrollable_frame)
        button = tk.Button(
            frame,
            image=tk_image,
            command=lambda img=tk_image, path=image_path, num=n: show_selected_image(
                img, path, num
            ),
        )
        button.pack()
        image_name = image_path.name
        label = tk.Label(frame, text=image_name)
        label.pack()
        frame.grid(row=i // 5, column=i % 5, padx=5, pady=5)

    prev_button.config(state=tk.NORMAL if current_page > 0 else tk.DISABLED)
    next_button.config(
        state=tk.NORMAL if end_index < len(photo_images) else tk.DISABLED
    )

    page_indicator.config(
        text=f"Page {current_page + 1} of {total_pages(photo_images)}"
    )


def go_to_next_page():
    global current_page
    if (current_page + 1) * images_per_page < len(photo_images):
        current_page += 1
        display_images()


def go_to_prev_page():
    global current_page
    if current_page > 0:
        current_page -= 1
        display_images()


def total_pages(arr):
    return (len(arr) + images_per_page - 1) // images_per_page


def sort_by_distance(photo_arr, histogram):
    global current_selected_img
    if current_selected_img[1] == -1:
        print("No image selected")
        return
    distances = []
    selected_histogram = histogram[current_selected_img[1]]
    for x in range(len(histogram)):
        calculated_distance = 0
        for y in range(len(histogram[x])):
            calculated_distance += abs(
                float((selected_histogram[y] - histogram[x][y]) / (WIDTH * HEIGHT))
            )
        distances.append(calculated_distance)

    sorted_photo_arr = [
        photo for _, photo in sorted(zip(distances, photo_arr), key=lambda x: x[0])
    ]

    photo_images[:] = sorted_photo_arr
    display_images()


# Create the main window
window = tk.Tk()
window.title("100 Images Viewer")
window.geometry("800x600")
window.configure(bg="#f0f0f0")
photo_images = []
# Frame for the selected image and buttons
top_frame = tk.Frame(window, bg="#e6e6e6", borderwidth=2, relief="solid")
top_frame.pack(side="right", fill="y", padx=10, pady=10)

selected_image_label = tk.Label(
    top_frame, text="No Image Selected", bg="white", borderwidth=2, relief="solid"
)
selected_image_label.pack(side="top", padx=10, pady=10, fill="both", expand=True)

# Frame for buttons below the image display
button_frame = tk.Frame(top_frame, bg="#e6e6e6")
button_frame.pack(side="bottom", fill="both", expand=True)

intensity_button = tk.Button(
    button_frame,
    text="Sort by Intensity",
    width=20,
    height=2,
    bg="#d3d3d3",
    fg="#000000",
    command=lambda: sort_by_distance(photo_images, intensity_histogram),
)
intensity_button.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

colorcode_button = tk.Button(
    button_frame,
    text="Sort by Color Code",
    width=20,
    height=2,
    bg="#87ceeb",
    fg="#000000",
    command=lambda: sort_by_distance(photo_images, color_histogram),
)
colorcode_button.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# Previous and Next buttons
prev_button = tk.Button(button_frame, text="Previous", command=go_to_prev_page)
prev_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

# Page indicator label
page_indicator = tk.Label(
    button_frame,
    text=f"Page {current_page + 1} of {total_pages(photo_images)}",
    bg="#e6e6e6",
)
page_indicator.grid(row=2, column=0, padx=10, pady=5)

next_button = tk.Button(button_frame, text="Next", command=go_to_next_page)
next_button.grid(row=2, column=0, padx=10, pady=5, sticky="e")

# Create a scrollable frame for image thumbnails on the left
scrollable_frame = Frame(window, bg="#f9f9f9")
scrollable_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

# Get the home directory of the user
home_dir = Path.home()
image_folder = home_dir / "css484yippee" / "images"
image_paths = list(image_folder.glob("*.jpg"))
image_paths = image_paths[:100]

counter = 0
target_size = 190
for image_path in image_paths:
    img = Image.open(image_path)
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

    width, height = img.size
    if width > height:
        left = (width - height) // 2
        right = left + height
        top, bottom = 0, height
    else:
        top = (height - width) // 2
        bottom = top + width
        left, right = 0, width

    img = img.crop((left, top, right, bottom))
    img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

    tk_image = ImageTk.PhotoImage(img)
    photo_images.append((tk_image, image_path, counter))
    counter += 1

# Display the first page of images
display_images()
window.mainloop()
