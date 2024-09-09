import cv2
import numpy as np
from PIL import Image

def align_images(image1_path, image2_path):
    # Load images
    img1 = cv2.imread(image1_path, cv2.IMREAD_COLOR)
    img2 = cv2.imread(image2_path, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Detect ORB features and compute descriptors
    orb = cv2.ORB_create(5000)
    keypoints1, descriptors1 = orb.detectAndCompute(gray1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(gray2, None)

    # Match descriptors using BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(descriptors1, descriptors2)

    # Sort matches based on their distances
    matches = sorted(matches, key=lambda x: x.distance)

    # Extract the location of matched keypoints
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 2)

    # Estimate affine transformation matrix (rotation + translation, no distortion)
    affine_matrix, _ = cv2.estimateAffinePartial2D(dst_pts, src_pts)

    # Apply affine transformation to the second image
    height, width, _ = img1.shape
    aligned_img2 = cv2.warpAffine(img2, affine_matrix, (width, height))

    return img1, aligned_img2

def manual_crop(img, crop_left, crop_bottom):
    # Manually crop the image: remove pixels from left and bottom
    height, width, _ = img.shape
    cropped_img = img[0:height - crop_bottom, crop_left:width]  # Cropping the left and bottom areas
    return cropped_img

def combine_images(image_path_1, image_path_2, output_path, crop_left, crop_bottom):
    # Align the images
    img1, img2_aligned = align_images(image_path_1, image_path_2)

    # Apply manual cropping
    cropped_img1 = manual_crop(img1, crop_left, crop_bottom)
    cropped_img2 = manual_crop(img2_aligned, crop_left, crop_bottom)

    # Convert the cropped images to PIL format for combining
    img1_pil = Image.fromarray(cv2.cvtColor(cropped_img1, cv2.COLOR_BGR2RGB))
    img2_pil = Image.fromarray(cv2.cvtColor(cropped_img2, cv2.COLOR_BGR2RGB))

    # Create a new image with the combined width of both cropped images
    combined_image = Image.new('RGB', (img1_pil.width + img2_pil.width, img1_pil.height))

    # Paste both images side by side into the new image
    combined_image.paste(img1_pil, (0, 0))
    combined_image.paste(img2_pil, (img1_pil.width, 0))

    # Save the combined image
    combined_image.save(output_path)

def main(image1_path, image2_path, output_path, crop_left, crop_bottom):
    # Call the combine_images function with manual cropping dimensions
    combine_images(image1_path, image2_path, output_path, crop_left, crop_bottom)

# Example usage
if __name__ == "__main__":
    image1_path = "path/to/first_image.jpg"  # Replace with actual path
    image2_path = "path/to/second_image.jpg"  # Replace with actual path
    output_path = "path/to/output_combined_image.jpg"  # Replace with actual output path

    # Manually crop 200 pixels from the left and 60 pixels from the bottom
    crop_left = 200
    crop_bottom = 60

    main(image1_path, image2_path, output_path, crop_left, crop_bottom)
