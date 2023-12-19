import os
import logging


class Settings:
    TOKEN = os.environ.get("TOKEN") or "6769024027:AAHkoiPjHUCCibNEdEdYYiqb6j3CffiFaHU"
    CHAT_ID = os.environ.get("CHAT_ID") or "Your_chat_id"
    FILE_LOCATION = os.path.join(os.path.expanduser("~"), "ebayklein.db")
    TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&parse_mode=HTML&"""
    LOGGING = os.environ.get("LOGGING") or logging.ERROR
    URL_BASE = "https://www.ebay-kleinanzeigen.de"


settings = Settings()
