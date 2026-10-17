import csv, io
from flask import Flask, render_template, request, redirect, url_for, flash
from garimpo.config import get_config
from garimpo.db import init_db, all_offers, upsert_offer, get_offer, set_affiliate_link, init_sales_db, import_sales, sales_summary
from garimpo.mercadolivre import search_products
from garimpo.telegram import send_message, format_offer, get_bot_info

config = get_config()
app = Flask(__name__)
app.secret_key = config["app_secret_key"]
init_db()
init_sales_db()

def brl(value):
    if value is None: return "—"
    return ("R$ {:,.2f}".format(value)).replace(",", "X").replace(".", ",").replace("X", ".")
app.jinja_env.filters["brl"] = brl

@app.get("/")
def index():
    totals, by_product, by_segment, recent_sales = sales_summary()
    return render_template("index.html", offers=all_offers(), config=config, totals=totals, by_product=by_product, by_segment=by_segment, recent_sales=recent_sales)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/search")
def search():
    total, errors = 0, []
    for term in config["search_terms"]:
        try:
            for item in search_products(term, config["ml_site_id"], config["max_price"], config["min_discount"]):
                if item.get("product_id") and item.get("product_url"):
                    upsert_offer(item); total += 1
        except Exception as exc: errors.append(f"{term}: {exc}")
    flash(f"Busca concluída: {total} ofertas encontradas/atualizadas.", "success")
    if errors: flash("Algumas buscas falharam: " + " | ".join(errors), "error")
    return redirect(url_for("index"))

@app.post("/affiliate/<int:offer_id>")
def affiliate(offer_id):
    link = request.form.get("affiliate_url","").strip()
    if not (link.startswith("https://") and any(d in link for d in ("mercadolivre.com","meli.la","amazon.com.br"))):
        flash("Cole um link HTTPS gerado pela ferramenta oficial de afiliados.", "error")
    else:
        set_affiliate_link(offer_id, link); flash("Link salvo. Revise antes de publicar.", "success")
    return redirect(url_for("index"))

@app.post("/telegram/test")
def telegram_test():
    try:
        bot = get_bot_info(config["telegram_bot_token"])
        flash(f"Conexão validada: @{bot.get('username','bot')}", "success")
    except Exception as exc: flash(f"Falha ao validar Telegram: {exc}", "error")
    return redirect(url_for("index"))

@app.post("/telegram/send/<int:offer_id>")
def telegram_send(offer_id):
    offer = get_offer(offer_id)
    if not offer or not offer["affiliate_url"]:
        flash("Publicação bloqueada: registre o link oficial de afiliado primeiro.", "error")
    elif not config["telegram_bot_token"] or not config["telegram_chat_id"]:
        flash("Configure TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID nas variáveis do Render.", "error")
    else:
        try:
            send_message(config["telegram_bot_token"], config["telegram_chat_id"], format_offer(offer, brl), parse_mode="HTML")
            flash("Oferta publicada no Telegram.", "success")
        except Exception as exc: flash(f"Erro no Telegram: {exc}", "error")
    return redirect(url_for("index"))

@app.post("/sales/import")
def sales_import():
    file=request.files.get("sales_csv")
    if not file or not file.filename.lower().endswith(".csv"):
        flash("Selecione um CSV oficial de vendas/comissões.", "error"); return redirect(url_for("index"))
    try:
        reader=csv.DictReader(io.StringIO(file.stream.read().decode("utf-8-sig")))
        aliases={"sale_date":["data","sale_date","data_venda"],"order_id":["pedido","order_id","id_pedido"],"commission":["comissao","comissão","commission"],"source":["marketplace","origem","source"],"product_id":["id_produto","product_id","sku"],"product_title":["produto","product_title"],"segment":["segmento","segment"],"units":["quantidade","units"],"gross_sales":["valor_venda","venda_bruta","gross_sales"],"status":["status"]}
        headers={str(k).strip().lower():k for k in (reader.fieldnames or [])}
        mapping={key:next((headers[x] for x in names if x in headers),None) for key,names in aliases.items()}
        if not mapping["sale_date"] or not mapping["order_id"] or not mapping["commission"]:
            flash("CSV precisa conter data, pedido e comissão.", "error"); return redirect(url_for("index"))
        rows=[]
        for raw in reader:
            def val(k,default=""): return (raw.get(mapping[k],"") or default).strip() if mapping.get(k) else default
            def num(k,default=0):
                s=val(k,str(default)).replace("R$","").replace(" ","")
                if "," in s and "." in s: s=s.replace(".","").replace(",",".")
                elif "," in s: s=s.replace(",",".")
                try: return float(s)
                except ValueError: return default
            if val("sale_date") and val("order_id"):
                rows.append({"sale_date":val("sale_date")[:10],"order_id":val("order_id"),"source":val("source","mercadolivre").lower(),"product_id":val("product_id"),"product_title":val("product_title","Produto não identificado"),"segment":val("segment","Não classificado"),"units":int(num("units",1)),"gross_sales":num("gross_sales"),"commission":num("commission"),"status":val("status","confirmada")})
        flash(f"Importação concluída: {import_sales(rows)} linhas processadas.", "success")
    except Exception as exc: flash(f"Erro na importação: {exc}", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host=config["host"], port=config["port"])
