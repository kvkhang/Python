# PixInfo.py
# Program to start evaluating an image in python

from PIL import Image, ImageTk  # Correct import for Pillow
import glob, os, math
import tkinter as tk


# Pixel Info class.
class PixInfo:
    # Constructor.
    def __init__(self, master):
        self.master = master
        self.imageList = []
        self.photoList = []
        self.xmax = 0
        self.ymax = 0
        self.colorCode = []
        self.intenCode = []

        # Add each image (for evaluation) into a list,
        # and a Photo from the image (for the GUI) in a list.
        for infile in glob.glob("images/*.jpg"):
            file, ext = os.path.splitext(infile)
            im = Image.open(infile)

            # Resize the image for thumbnails.
            imSize = im.size
            x = imSize[0] // 4  # Ensure integer division
            y = imSize[1] // 4
            imResize = im.resize((x, y), Image.ANTIALIAS)
            photo = ImageTk.PhotoImage(imResize)

            # Find the max height and width of the set of pics.
            if x > self.xmax:
                self.xmax = x
            if y > self.ymax:
                self.ymax = y

            # Add the images to the lists.
            self.imageList.append(im)
            self.photoList.append(photo)

        # Create a list of pixel data for each image and add it
        # to a list.
        for im in self.imageList[:]:
            pixList = list(im.getdata())
            CcBins, InBins = self.encode(pixList)
            self.colorCode.append(CcBins)
            self.intenCode.append(InBins)

    # Bin function returns an array of bins for each
    # image, both Intensity and Color-Code methods.
    def encode(self, pixlist):
        # 2D array initialization for bins, initialized
        # to zero.
        CcBins = [0] * 64
        InBins = [0] * 25

        for r, g, b in pixlist:
            r_bin = r // 64
            g_bin = g // 64
            b_bin = b // 64
            color_index = (r_bin * 8) + (g_bin * 4) + b_bin
            CcBins[color_index] += 1

            intensity = (r + g + b) // 3
            InBins[intensity // 10] += 1

        return CcBins, InBins

    # Accessor functions:
    def get_imageList(self):
        return self.imageList

    def get_photoList(self):
        return self.photoList

    def get_xmax(self):
        return self.xmax

    def get_ymax(self):
        return self.ymax

    def get_colorCode(self):
        return self.colorCode

    def get_intenCode(self):
        return self.intenCode


def main():
    root = tk.Tk()
    pix_info = PixInfo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
