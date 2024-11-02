import numpy as np
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
color_intensity_histogram = np.zeros((100, 89))


# Pagination variables
current_page = 0
images_per_page = 20
columns_per_row = 5  # Number of columns to display
rows_per_page = 4  # Number of ro bothws per pageand 

# Adjust size for images
target_size = 180  # Size of each thumbnail image
max_selected_size = 1200  # Maximum size for the selected image

# Store the relevance of each image
image_relevance = {}

# Initialize feature weights
intensity_weights = np.ones(cols) / cols  # Normalized initial weights for intensity
color_weights = np.ones(64) / 64  # Normalized initial weights for color
stdev = []
average = []
feature = []

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
    for i, (tk_image, image_path, n, k) in enumerate(images_to_display):
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

def get_stdev_average():
    global stdev, average, color_intensity_histogram
    stdev = np.std(color_intensity_histogram[:, 2:], axis=0)
    average = np.mean(color_intensity_histogram[:, 2:], axis=0)

def normalize():
    global color_intensity_histogram, stdev, average
    min_nonzero_sstd = np.min(std[dev > 0]) if np.any(stdev > 0) else 1.0
    for(j in range(len(stdev))):
        if stdev[j] == 0:
        

def update_weights(normalized_features, relevant_indices):
    """
    Update feature weights based on relevance feedback.
    Implements the special cases for standard deviation handling.
    """
    if not relevant_indices:
        return np.ones(normalized_features.shape[1]) / normalized_features.shape[1]
    
    relevant_features = normalized_features[relevant_indices]
    
    # Calculate standard deviation and mean of relevant images
    std_relevant = np.std(relevant_features, axis=0)
    mean_relevant = np.mean(relevant_features, axis=0)
    
    # Get minimum non-zero standard deviation
    nonzero_std = std_relevant[std_relevant > 0]
    min_nonzero_std = np.min(nonzero_std) if len(nonzero_std) > 0 else 1.0
    
    # Initialize weights array
    weights = np.zeros(normalized_features.shape[1])
    
    # Handle special cases as per requirements
    for i in range(len(weights)):
        if std_relevant[i] == 0:
            if mean_relevant[i] != 0:
                # Case a: std is 0 but mean is not 0
                std_relevant[i] = 0.5 * min_nonzero_std
                weights[i] = 1 / std_relevant[i]
            else:
                # Case b: both std and mean are 0
                weights[i] = 0
        else:
            # Normal case: use 1/std as weight
            weights[i] = 1 / std_relevant[i]
    
    # Normalize weights to sum to 1
    if np.sum(weights) > 0:
        weights = weights / np.sum(weights)
    else:
        weights = np.ones(len(weights)) / len(weights)
    
    return weights

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

# Normalize histograms by image size
def normalize_histograms(histogram) :
    for i in range(rows): 
        total_pixels =  photo_images[i][3]

        for j in range(cols) :
            histogram[i][j] = histogram[i][j] / total_pixels

def calculate_weighted_distance(query_features, all_features, weights):
    """Calculate weighted distance between query and all features."""
    distances = np.zeros(len(all_features))
    for i in range(len(all_features)):
        # Calculate |Vi(I) - Vi(J)| for each feature
        feature_diff = np.abs(query_features - all_features[i])
        # Multiply by weights and sum
        distances[i] = np.sum(weights * feature_diff)
    return distances

def sort_by_distance_with_rf():
    global current_selected_img, intensity_weights, color_weights
    if current_selected_img[1] == -1:
        print("No image selected")
        return
    
    # Get relevant images from user feedback
    relevant_indices = [idx for idx, rel in image_relevance.items() if rel == 1]
    
    # Convert histograms to numpy arrays for processing
    intensity_features = np.array(intensity_histogram)
    color_features = np.array(color_histogram)
    
    # Normalize features using Gaussian normalization
    normalized_intensity, intensity_mean, intensity_std = gaussian_normalize(intensity_features)
    normalized_color, color_mean, color_std = gaussian_normalize(color_features)
    
    # Update weights if we have relevant images
    if relevant_indices:
        intensity_weights = update_weights(normalized_intensity, relevant_indices)
        color_weights = update_weights(normalized_color, relevant_indices)
    
    # Get query image features
    query_idx = current_selected_img[1]
    
    # Calculate distances using the weighted formula
    intensity_distances = calculate_weighted_distance(
        normalized_intensity[query_idx],
        normalized_intensity,
        intensity_weights
    )
    
    color_distances = calculate_weighted_distance(
        normalized_color[query_idx],
        normalized_color,
        color_weights
    )
    
    # Combine distances with equal weights
    combined_distances = 0.5 * intensity_distances + 0.5 * color_distances
    
    # Sort images based on combined distances
    sorted_indices = np.argsort(combined_distances)
    sorted_photo_arr = [photo_images[i] for i in sorted_indices]
    
    # Update the global photo_images with the sorted array
    photo_images[:] = sorted_photo_arr
    
    # Calculate and print precision for top 20 images
    if relevant_indices:
        top_20_indices = sorted_indices[:20]
        relevant_in_top_20 = sum(1 for idx in top_20_indices if idx in relevant_indices)
        precision = relevant_in_top_20 / 20
        print(f"Precision@20: {precision:.2f}")
    
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

# RF button
rf_button = tk.Button(
    button_frame,
    text="Sort by Intensity & Color Code (RF)",
    width=20,
    height=2,
    bg="#800080",
    fg="#ffffff",
    command=lambda: sort_by_distance(photo_images, color_intensity_histogram),
)
rf_button.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

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
    photo_images.append((tk_image, image_path, counter, width * height))
    counter += 1

color_histogram = np.array(color_histogram)
intensity_histogram = np.array(intensity_histogram)
color_intensity_histogram = np.concatenate((intensity_histogram, color_histogram), axis=1)
get_stdev_average()
normalize()
# Initial image display
display_images()

# Start the main event loop
window.mainloop()
