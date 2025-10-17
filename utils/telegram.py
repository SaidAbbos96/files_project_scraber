def detect_telegram_type(mime):
    if not mime:
        return "document"
    if mime.startswith("video/"):
        return "video"
    if mime.startswith("image/"):
        return "photo"
    if mime.startswith("audio/"):
        return "audio"
    return "document"
