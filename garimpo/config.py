import os
from dotenv import load_dotenv
load_dotenv()

def get_config():
    return {
        "app_secret_key": os.getenv("APP_SECRET_KEY","dev-only-change-me"),
        "host": os.getenv("APP_HOST","0.0.0.0"),
        "port": int(os.getenv("APP_PORT","8080")),
        "ml_site_id": os.getenv("ML_SITE_ID","MLB"),
        "search_terms": [x.strip() for x in os.getenv("ML_SEARCH_TERMS","fone bluetooth;aspirador vertical").split(";") if x.strip()],
        "min_discount": float(os.getenv("MIN_DISCOUNT_PERCENT","15")),
        "max_price": float(os.getenv("MAX_PRICE_BRL","1000")),
        "wa_token": os.getenv("WHATSAPP_ACCESS_TOKEN","").strip(),
        "wa_phone_number_id": os.getenv("WHATSAPP_PHONE_NUMBER_ID","").strip(),
        "wa_graph_version": os.getenv("WHATSAPP_GRAPH_VERSION","v23.0").strip(),
        "wa_recipients": [x.strip() for x in os.getenv("WHATSAPP_OPT_IN_RECIPIENTS","").split(",") if x.strip()],
        "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN","").strip(),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID","").strip(),
        "auto_publish": os.getenv("AUTO_PUBLISH","false").lower()=="true",
    }
