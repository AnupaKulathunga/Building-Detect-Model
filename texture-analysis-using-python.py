import rasterio
from skimage.feature import graycomatrix, graycoprops
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to process each window and compute GLCM features
def process_window(row, col, win_size):
    window = vv_band_uint8[row:row + win_size, col:col + win_size]
    glcm = graycomatrix(window, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
    contrast = graycoprops(glcm, 'contrast')[0, 0]
    dissimilarity = graycoprops(glcm, 'dissimilarity')[0, 0]
    homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]
    energy = graycoprops(glcm, 'energy')[0, 0]
    return (row, col, contrast, dissimilarity, homogeneity, energy)

# Function to update the texture feature images
def update_texture_images(result):
    row, col, contrast, dissimilarity, homogeneity, energy = result
    contrast_img[row, col] = contrast
    dissimilarity_img[row, col] = dissimilarity
    homogeneity_img[row, col] = homogeneity
    energy_img[row, col] = energy
    if (row * vv_band_uint8.shape[1] + col) % 1000 == 0:
        logging.info(f'Processed window at row {row}, col {col}')

# Read the SAR image
with rasterio.open('results/processed.tif') as src:
    vv_band = src.read(1)  # Assuming Sigma0_VV_db is the first band
    vh_band = src.read(2)  # Assuming Sigma0_VH_db is the second band

# Normalize and convert the bands to unsigned 8-bit integer
vv_band_uint8 = ((vv_band - vv_band.min()) / (vv_band.max() - vv_band.min()) * 255).astype('uint8')

# Define a window size for texture calculation
win_size = 5

# Placeholder arrays for texture features
contrast_img = np.zeros((vv_band_uint8.shape[0] - win_size, vv_band_uint8.shape[1] - win_size), dtype=np.float64)
dissimilarity_img = np.zeros_like(contrast_img, dtype=np.float64)
homogeneity_img = np.zeros_like(contrast_img, dtype=np.float64)
energy_img = np.zeros_like(contrast_img, dtype=np.float64)

# Execute texture analysis in parallel
with ThreadPoolExecutor(max_workers=8) as executor:
    # Submit tasks to the executor pool
    futures = [executor.submit(process_window, row, col, win_size)
               for row in range(vv_band_uint8.shape[0] - win_size)
               for col in range(vv_band_uint8.shape[1] - win_size)]

    # As each task completes, update texture feature images
    for future in futures:
        update_texture_images(future.result())

# Display the texture features
fig, axs = plt.subplots(2, 2, figsize=(10, 10))
axs[0, 0].imshow(contrast_img, cmap='gray')
axs[0, 0].set_title('Contrast')
axs[0, 1].imshow(dissimilarity_img, cmap='gray')
axs[0, 1].set_title('Dissimilarity')
axs[1, 0].imshow(homogeneity_img, cmap='gray')
axs[1, 0].set_title('Homogeneity')
axs[1, 1].imshow(energy_img, cmap='gray')
axs[1, 1].set_title('Energy')

for ax in axs.flat:
    ax.axis('off')

plt.tight_layout()
plt.savefig('results/contrast_feature_image.png')
# plt.show()
