# Lab Experiment: Loading and Displaying Digital Images

## Objective

To learn how to load, display, and inspect digital images using OpenCV and Matplotlib.

## Problem Statement

A digital image is a 2D matrix of pixel intensity values. Understanding how to load and visualize images is the foundation of all image processing tasks. In this experiment, you will load images from a dataset, display them using different colormaps, and inspect their properties such as dimensions, data type, and pixel intensity distribution.

## Task Instructions

### Part 1: Setup and Image Loading

1. Install the required dependencies: `opencv-python`, `matplotlib`, and `numpy`.
2. Load a `.tif` image from the dataset using `cv2.imread()` in grayscale mode (`cv2.IMREAD_GRAYSCALE`).
3. Print the following properties of the loaded image:
   - Shape of the image array
   - Data type (`dtype`)
   - Minimum and maximum pixel values

### Part 2: Display the Image

1. Use `plt.imshow()` with `cmap='gray'` to display the grayscale image.
2. Add a title showing the image filename.
3. Display the pixel intensity range in the title or as axis labels.

### Part 3: Display Multiple Images

1. Load 4 different images from the dataset in grayscale mode.
2. Display all 4 images in a 2x2 subplot grid using `plt.subplots(2, 2)`.
3. Add titles to each subplot showing the image name and its dimensions.

### Part 4: Image Properties Exploration

1. Print detailed properties of a selected image in a formatted table:
   - Filename, Dimensions, Total pixels, Data type
   - Min intensity, Max intensity, Mean intensity, Standard deviation
2. Display the image alongside its histogram of pixel intensities using `plt.hist()` with 256 bins.

## Analysis Questions

1. What does the shape of the image array represent? How do grayscale and color images differ in shape?
2. Why do we specify `cmap='gray'` when displaying grayscale images? What happens if we don't?
3. Compare the histogram distributions of two different images. What does a narrow histogram vs a wide histogram indicate about the image?
