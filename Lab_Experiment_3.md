# Lab Experiment: Image Negation, Grayscale Conversion, Subtraction, and Inversion

## Objective

To implement and analyze fundamental intensity transformation operations including image negation, grayscale conversion, image subtraction, and intensity inversion.

## Problem Statement

Intensity transformations are point operations that modify pixel values individually. Negation (s = L-1-r) reverses the intensity scale, useful for enhancing white/gray detail in dark regions. Image subtraction (g = |f1-f2|) reveals differences between two images, widely used in medical imaging (Digital Subtraction Angiography). These operations form the building blocks of image enhancement.

## Task Instructions

### Part 1: Image Loading and Grayscale Conversion

- Load a color image from the dataset.
- Convert the image from BGR to grayscale using `cv2.cvtColor()`.
- Display both the original color image and the grayscale image side by side.

### Part 2: Image Negation

- Compute the negative of a grayscale image using the formula: **s = 255 - r**
- Display the original and negative images side by side.
- Plot histograms of both images to observe the intensity transformation.

### Part 3: Image Subtraction

- Load two related images (angiography mask and live image).
- Compute the absolute difference: **|img1 - img2|**
- Display all three images (mask, live, and difference).
- Repeat for dental X-ray and tungsten shading correction image pairs.

### Part 4: Image Inversion and Combined Operations

- Apply inversion to the subtraction result.
- Apply contrast stretching for enhancement.
- Display the complete pipeline from subtraction through negation to enhancement.

## Analysis Questions

1. In the angiography example, what structures become visible after subtraction that were not visible in either original image?

2. Why is absolute difference used instead of simple subtraction? What would happen with signed vs unsigned arithmetic?

3. Compare the histogram of the original image with its negative. What mathematical relationship exists between them?
