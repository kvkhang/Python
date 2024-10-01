import tkinter as tk
from PIL import Image, ImageTk


def randomcmd():
    print("boop")


# Create the main window
window = tk.Tk()
window.title("My First GUI")

# Add a label
label = tk.Label(window, text="Hello, World!")
label.pack()

# Create a button
button = tk.Button(window, text="Click Me", command=lambda: randomcmd())
button.pack()

button2 = tk.Button(window, text="Click Me too", command=lambda: randomcmd())
button2.pack()

image_path = "your_image.jpg"  # Replace with the path to your image file
img = Image.open(image_path)

# Convert the image to a format that Tkinter can work with (ImageTk.PhotoImage)
tk_image = ImageTk.PhotoImage(img)

# Create a label to display the image
label = tk.Label(window, image=tk_image)
label.pack()

# Start the event loop
window.mainloop()
