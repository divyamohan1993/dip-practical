# Lab Experiment: Gamma Correction and Power Law Transformations

## Objective

To understand and implement power law (gamma) transformations for image contrast enhancement.

## Problem Statement

The power law transformation s = c * r^γ is one of the most important intensity transformations in image processing. By varying γ, we can enhance dark regions (γ < 1) or compress bright regions (γ > 1). This is widely used in display calibration (gamma correction) and medical image enhancement.

## Task Instructions

### Part 1: Load and Normalize Image

- Load a grayscale image using OpenCV.
- Normalize pixel values to the [0, 1] range for gamma computation.
- Display the original image and print its properties (shape, min/max values).

### Part 2: Apply Gamma Correction

- Apply the power law transformation: **s = c * r^γ** with c = 1.
- Use the following gamma values: **0.3, 0.5, 1.0, 1.5, 2.5, 5.0**.
- Display all results in a grid for comparison.
- Plot the transformation curves for various gamma values to visualize the input-output mapping.

### Part 3: Log Transformation

- Apply the log transformation: **s = c * log(1 + r)**.
- Compare the result with gamma correction (γ = 0.4) on the same image.
- Display both results side by side with the original.

### Part 4: Contrast Enhancement

- **Part 4a:** Apply gamma correction to a dark image using γ = 0.3, 0.4, 0.6. Observe how γ < 1 enhances dark regions.
- **Part 4b:** Apply gamma correction to a bright image using γ = 3.0, 4.0, 5.0. Observe how γ > 1 compresses bright regions.
- **Part 4c:** Compare gamma correction across images with different contrast levels (low, medium, high contrast).
- Display histograms before and after gamma correction to visualize the intensity redistribution.

## Dataset

Images are located in: `DIP3E_CH02_Original_Images/DIP3E_Original_Images_CH02/`

Default images used:
- Fig0241(a)(einstein low contrast).tif - Dark image for gamma enhancement
- Fig0241(b)(einstein med contrast).tif - Medium contrast comparison
- Fig0241(c)(einstein high contrast).tif - High contrast / bright image
- Fig0222(b)(cameraman).tif - General gamma demonstration

## Analysis Questions

1. For a dark image, which gamma value produces the best visual enhancement? Why does gamma < 1 brighten dark regions?

2. Compare log transformation with gamma = 0.4 on the same image. Which produces better results and why?

3. How does gamma correction relate to display devices? If a monitor has gamma = 2.5, what pre-correction gamma should be applied?
