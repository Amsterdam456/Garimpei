import requests

def send_text(config,recipient,message):
    if not config["wa_token"] or not config["wa_phone_number_id"]:
        raise RuntimeError("Configure WHATSAPP_ACCESS_TOKEN e WHATSAPP_PHONE_NUMBER_ID.")
    if recipient not in config["wa_recipients"]:
        raise RuntimeError("Destinatário não está na lista de opt-in.")
    url=f"https://graph.facebook.com/{config['wa_graph_version']}/{config['wa_phone_number_id']}/messages"
    headers={"Authorization":f"Bearer {config['wa_token']}","Content-Type":"application/json"}
    payload={"messaging_product":"whatsapp","recipient_type":"individual","to":recipient,"type":"text","text":{"preview_url":True,"body":message}}
    response=requests.post(url,headers=headers,json=payload,timeout=20)
    if not response.ok: raise RuntimeError(f"WhatsApp API retornou HTTP {response.status_code}: {response.text[:300]}")
    return response.json()
