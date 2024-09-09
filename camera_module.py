
# camera_module.py

from picamera2 import Picamera2
import time

def take_photo(camera_index, output_path, shutter=None, gain=None, awb=None):
    picam2 = Picamera2(camera_num=camera_index)
    
    config = picam2.create_still_configuration()

    # Apply settings if provided
    if shutter:
        config["controls"]["ExposureTime"] = shutter
    if gain:
        config["controls"]["AnalogueGain"] = gain
    if awb:
        config["controls"]["AwbEnable"] = awb == 'on'
    
    picam2.configure(config)
    picam2.start()
    time.sleep(2)  # Give some time to stabilize
    picam2.capture_file(output_path)
    picam2.stop()
