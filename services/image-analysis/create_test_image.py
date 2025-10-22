#!/usr/bin/env python3
"""Create a simple test image for testing the image upload endpoint"""

import numpy as np
from PIL import Image
import os

def create_test_image():
    # Create a simple 224x224 RGB image with greenish color (like plant leaf)
    width, height = 224, 224

    # Create a green background with some variation
    image_array = np.zeros((height, width, 3), dtype=np.uint8)

    # Add green base color (plant-like)
    image_array[:, :, 1] = 150  # Green channel
    image_array[:, :, 0] = 50   # Red channel
    image_array[:, :, 2] = 30   # Blue channel

    # Add some variation to make it more realistic
    noise = np.random.randint(-20, 20, (height, width, 3))
    image_array = np.clip(image_array + noise, 0, 255).astype(np.uint8)

    # Add some yellow spots (simulating deficiency symptoms)
    for _ in range(10):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        radius = np.random.randint(5, 15)

        y_grid, x_grid = np.ogrid[:height, :width]
        mask = (x_grid - x)**2 + (y_grid - y)**2 <= radius**2

        image_array[mask] = [200, 200, 50]  # Yellow color

    # Create PIL image
    image = Image.fromarray(image_array)

    # Save the image
    output_path = os.path.join(os.path.dirname(__file__), 'test_image.jpg')
    image.save(output_path, 'JPEG', quality=90)

    print(f"Test image created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_test_image()