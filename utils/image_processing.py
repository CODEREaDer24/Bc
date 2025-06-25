import cv2
import numpy as np

def analyze_strip(image_file):
    """
    Basic placeholder image processing for a test strip.
    Expects image_file to be a file-like object.
    Returns mock chemical values based on dummy logic.
    """
    # Convert to NumPy array
    file_bytes = np.frombuffer(image_file.read(), np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    # Resize for consistency
    img = cv2.resize(img, (400, 100))

    # Convert to HSV for better color separation
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Divide into 3 vertical zones (pH, chlorine, alkalinity)
    height, width, _ = img.shape
    zone_width = width // 3

    zones = {
        "pH": hsv[0:height, 0:zone_width],
        "chlorine": hsv[0:height, zone_width:2*zone_width],
        "alkalinity": hsv[0:height, 2*zone_width:width],
    }

    results = {}
    for chem, zone in zones.items():
        avg_color = cv2.mean(zone)[:3]
        hue = avg_color[0]

        # Mock logic based on hue
        if chem == "pH":
            results[chem] = round(map_hue_to_ph(hue), 1)
        elif chem == "chlorine":
            results[chem] = round(map_hue_to_chlorine(hue), 1)
        elif chem == "alkalinity":
            results[chem] = round(map_hue_to_alkalinity(hue))

    return results

def map_hue_to_ph(hue):
    if hue < 20:
        return 6.8
    elif hue < 40:
        return 7.2
    elif hue < 60:
        return 7.6
    else:
        return 8.0

def map_hue_to_chlorine(hue):
    if hue < 20:
        return 0.5
    elif hue < 40:
        return 1.5
    elif hue < 60:
        return 3.0
    else:
        return 5.0

def map_hue_to_alkalinity(hue):
    if hue < 20:
        return 60
    elif hue < 40:
        return 100
    elif hue < 60:
        return 120
    else:
        return 180
