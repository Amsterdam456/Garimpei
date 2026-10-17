from html import escape
import requests
API_BASE="https://api.telegram.org/bot{token}/{method}"

def send_message(token,chat_id,text,parse_mode=None):
    token=(token or "").strip(); chat_id=(chat_id or "").strip()
    if not token or not chat_id: raise ValueError("Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID.")
    payload={"chat_id":chat_id,"text":text,"disable_web_page_preview":False}
    if parse_mode: payload["parse_mode"]=parse_mode
    response=requests.post(API_BASE.format(token=token,method="sendMessage"),json=payload,timeout=20)
    data=response.json()
    if not response.ok or not data.get("ok"): raise RuntimeError(data.get("description",f"HTTP {response.status_code}"))
    return data["result"]

def format_offer(offer,brl):
    title=escape(str(offer["title"])); price=escape(brl(offer["price"]))
    lines=["🔥 <b>GARIMPO DE OFERTAS</b>","",f"<b>{title}</b>",f"💸 <b>{price}</b>"]
    if offer["original_price"]: lines.append(f"De <s>{escape(brl(offer['original_price']))}</s>")
    if offer["discount_percent"]: lines.append(f"🏷️ Desconto informado: <b>{offer['discount_percent']}%</b>")
    lines += [f"🛒 <a href=\"{escape(str(offer['affiliate_url']),quote=True)}\">Ver oferta</a>","","⚠️ Preço e estoque podem mudar. Link de afiliado: podemos receber comissão por compras elegíveis, sem custo adicional para você."]
    return "\n".join(lines)

def get_bot_info(token):
    if not token: raise ValueError("Configure TELEGRAM_BOT_TOKEN.")
    response=requests.get(API_BASE.format(token=token,method="getMe"),timeout=15); data=response.json()
    if not response.ok or not data.get("ok"): raise RuntimeError(data.get("description","Falha ao validar o bot."))
    return data["result"]
