import requests
import os

def send_file_by_url_via_bot(token: str, chat_id: str, file_url: str, caption: str = None, as_video: bool = True):
    """
    Telegram Bot API orqali 2GB gacha bo'lgan faylni URL orqali yuboradi.
    as_video=True bo'lsa sendVideo, aks holda sendDocument ishlatiladi.
    """
    method = "sendVideo" if as_video else "sendDocument"
    api_url = f"https://api.telegram.org/bot{token}/{method}"
    payload = {
        "chat_id": chat_id,
        "caption": caption or "",
    }
    if as_video:
        payload["video"] = file_url
    else:
        payload["document"] = file_url
    resp = requests.post(api_url, data=payload)
    try:
        return resp.json()
    except Exception:
        return {"ok": False, "error": "Invalid response", "raw": resp.text}
