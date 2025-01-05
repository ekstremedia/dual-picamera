from picamera2 import Picamera2
import time

def take_photo(camera_index, output_path, shutter=None, gain=None, awb=None, raw_path=None, only_raw=False):
    picam2 = Picamera2(camera_num=camera_index)
    
    # Create configuration for still capture (JPEG or RAW)
    config = picam2.create_still_configuration(raw={}, display=None)  # Enable raw capture

    # Apply settings if provided
    if shutter:
        config["controls"]["ExposureTime"] = shutter

        # If the exposure is over 1 second (1,000,000 microseconds), disable AEC, AGC, and AWB
        if shutter > 1000000:
            # Disable automatic exposure control and gain control by setting manual gain
            config["controls"]["AeEnable"] = False  # Disable automatic exposure
            config["controls"]["AnalogueGain"] = gain or 1.0  # Apply the provided gain or default to 1.0

            # Disable automatic white balance
            config["controls"]["AwbEnable"] = False
            print("AEC/AGC and AWB disabled for long exposure.")
        else:
            # Otherwise, use provided or default settings
            if gain:
                config["controls"]["AnalogueGain"] = gain
            if awb:
                config["controls"]["AwbEnable"] = awb == 'on'
    else:
        # Default gain and AWB behavior if no shutter is provided
        if gain:
            config["controls"]["AnalogueGain"] = gain
        if awb:
            config["controls"]["AwbEnable"] = awb == 'on'
    
    # Skip preview if the exposure is long to speed up capture
    if shutter and shutter > 1000000:
        immediate = True  # Skip preview for long exposures
    else:
        immediate = False  # Use normal capture flow

    picam2.configure(config)
    picam2.start()
    time.sleep(2 if not immediate else 0)  # Skip the 2s delay for long exposures

    # If only RAW is requested, capture only RAW
    if only_raw and raw_path:
        picam2.capture_request().save_dng(raw_path)
        print(f"RAW image saved at {raw_path}")
    else:
        # Otherwise capture JPEG and optionally RAW
        if output_path:
            picam2.capture_file(output_path)
            print(f"JPEG image saved at {output_path}")
        if raw_path:
            picam2.capture_request().save_dng(raw_path)
            print(f"RAW image saved at {raw_path}")
    
    picam2.stop()
