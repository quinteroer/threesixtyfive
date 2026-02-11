import base64

ICON_PATH = "assets/apple-touch-icon.png" # Path to your icon

def create_mobileconfig():
    with open(ICON_PATH, "rb") as image_file:
        encoded_icon = base64.b64encode(image_file.read()).decode('utf-8')
        with open("icon_base64", "w", encoding="utf-8") as f:
            f.write(encoded_icon)

create_mobileconfig()