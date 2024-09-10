import asyncio
import argparse
from datetime import datetime
import os
from camera_module import take_photo
from image_combiner import combine_images  # Import the new module

# Define default save path
save_path = '/var/www/html/dual/'

# Ensure the folder exists
os.makedirs(save_path, exist_ok=True)

def generate_filename(camera_name, settings, extension='jpg'):
    # Generate filename based on camera type, settings, and datetime
    now = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    settings_str = '_'.join([f"{k}-{v}" for k, v in settings.items() if v is not None])
    return f"{camera_name}_{settings_str}_{now}.{extension}"

async def take_dual_photos(shutter=None, gain=None, awb=None, combine=False, raw=False, only_raw=False):
    # Create filenames for both cameras
    settings = {
        'shutter': shutter,
        'gain': gain,
        'awb': awb
    }
    
    filename_noir = generate_filename("v3_noir", settings)
    filename_normal = generate_filename("v3_normal", settings)
    filename_combined = generate_filename("combined", settings)
    
    # Generate RAW filenames
    if raw or only_raw:
        raw_filename_noir = generate_filename("v3_noir", settings, extension='dng')
        raw_filename_normal = generate_filename("v3_normal", settings, extension='dng')
    else:
        raw_filename_noir = None
        raw_filename_normal = None

    # Full paths for the images
    path_noir = os.path.join(save_path, filename_noir)
    path_normal = os.path.join(save_path, filename_normal)
    path_combined = os.path.join(save_path, filename_combined)
    
    # Full paths for RAW files (optional)
    raw_path_noir = os.path.join(save_path, raw_filename_noir) if raw_filename_noir else None
    raw_path_normal = os.path.join(save_path, raw_filename_normal) if raw_filename_normal else None

    # Run both photo tasks asynchronously
    await asyncio.gather(
        asyncio.to_thread(take_photo, 0, path_noir, shutter, gain, awb, raw_path_noir, only_raw),  # Camera 0 (Noir)
        asyncio.to_thread(take_photo, 1, path_normal, shutter, gain, awb, raw_path_normal, only_raw)  # Camera 1 (Normal)
    )

    # If combine is true and not only_raw, combine the two images
    if combine and not only_raw:
        # Manually set the cropping parameters (adjust as needed)
        crop_left = 200
        crop_bottom = 60

        # Call combine_images with the generated combined filename
        combine_images(path_noir, path_normal, path_combined, crop_left, crop_bottom)

        print(f"Combined image saved at {path_combined}")


def parse_args():
    parser = argparse.ArgumentParser(description="Capture photos with two cameras.")
    parser.add_argument('--shutter', type=int, help="Shutter speed in microseconds")
    parser.add_argument('--gain', type=float, help="Gain value")
    parser.add_argument('--awb', choices=['on', 'off'], help="Auto white balance on/off")
    parser.add_argument('--combine', action='store_true', help="Combine images side by side")
    parser.add_argument('--raw', action='store_true', help="Capture RAW (DNG) images along with JPEG")
    parser.add_argument('--only-raw', action='store_true', help="Capture only RAW (DNG) images without JPEG")

    return parser.parse_args()

def main():
    args = parse_args()

    # Set default values if no arguments are provided
    shutter = args.shutter or 2000000
    gain = args.gain or 2.0
    awb = args.awb or 'on'

    # Run the async function to take photos
    asyncio.run(take_dual_photos(shutter=shutter, gain=gain, awb=awb, combine=args.combine, raw=args.raw, only_raw=args.only_raw))

if __name__ == '__main__':
    main()
