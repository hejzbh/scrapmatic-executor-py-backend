import base64

def generateDownloadURL(content: str, mime_type: str = "text/plain"):
    # Encode string to Base64
    base64_content = base64.b64encode(content.encode()).decode()

    # Create the data URL
    return f"data:{mime_type};base64,{base64_content}"