import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "garimpo.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def connect():
    con=sqlite3.connect(DB_PATH); con.row_factory=sqlite3.Row; return con

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS offers (
        id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, product_id TEXT NOT NULL,
        title TEXT NOT NULL, price REAL, original_price REAL, discount_percent REAL,
        product_url TEXT NOT NULL, affiliate_url TEXT DEFAULT '', image_url TEXT DEFAULT '',
        status TEXT NOT NULL DEFAULT 'needs_affiliate_link', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(source,product_id))""")

def upsert_offer(item):
    with connect() as con:
        con.execute("""INSERT INTO offers(source,product_id,title,price,original_price,discount_percent,product_url,image_url)
        VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(source,product_id) DO UPDATE SET title=excluded.title,price=excluded.price,
        original_price=excluded.original_price,discount_percent=excluded.discount_percent,product_url=excluded.product_url,image_url=excluded.image_url""",
        (item["source"],item["product_id"],item["title"],item.get("price"),item.get("original_price"),item.get("discount_percent"),item["product_url"],item.get("image_url","")))

def all_offers():
    with connect() as con: return con.execute("SELECT * FROM offers ORDER BY COALESCE(discount_percent,0) DESC, created_at DESC").fetchall()

def get_offer(offer_id):
    with connect() as con: return con.execute("SELECT * FROM offers WHERE id=?",(offer_id,)).fetchone()

def set_affiliate_link(offer_id,link):
    with connect() as con: con.execute("UPDATE offers SET affiliate_url=?,status='ready_for_review' WHERE id=?",(link,offer_id))

def init_sales_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,sale_date TEXT NOT NULL,order_id TEXT NOT NULL,
        source TEXT NOT NULL DEFAULT 'mercadolivre',product_id TEXT DEFAULT '',product_title TEXT DEFAULT '',
        segment TEXT DEFAULT 'Não classificado',units INTEGER DEFAULT 1,gross_sales REAL DEFAULT 0,
        commission REAL DEFAULT 0,status TEXT DEFAULT 'confirmada',imported_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(source,order_id,product_id))""")

def import_sales(rows):
    with connect() as con:
        for r in rows:
            con.execute("""INSERT INTO sales(sale_date,order_id,source,product_id,product_title,segment,units,gross_sales,commission,status)
            VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(source,order_id,product_id) DO UPDATE SET
            sale_date=excluded.sale_date,product_title=excluded.product_title,segment=excluded.segment,units=excluded.units,
            gross_sales=excluded.gross_sales,commission=excluded.commission,status=excluded.status""",
            (r["sale_date"],r["order_id"],r.get("source","mercadolivre"),r.get("product_id",""),r.get("product_title",""),r.get("segment","Não classificado"),r.get("units",1),r.get("gross_sales",0),r.get("commission",0),r.get("status","confirmada")))
    return len(rows)

def sales_summary():
    with connect() as con:
        totals=con.execute("""SELECT COUNT(*) sales_count,COALESCE(SUM(units),0) units,COALESCE(SUM(gross_sales),0) gross_sales,COALESCE(SUM(commission),0) commission FROM sales WHERE lower(status) NOT IN ('cancelada','cancelado','reembolsada','reembolsado')""").fetchone()
        by_product=con.execute("""SELECT product_title,segment,SUM(units) units,COUNT(*) orders,SUM(gross_sales) gross_sales,SUM(commission) commission FROM sales WHERE lower(status) NOT IN ('cancelada','cancelado','reembolsada','reembolsado') GROUP BY product_title,segment ORDER BY commission DESC LIMIT 20""").fetchall()
        by_segment=con.execute("""SELECT segment,SUM(units) units,COUNT(*) orders,SUM(gross_sales) gross_sales,SUM(commission) commission FROM sales WHERE lower(status) NOT IN ('cancelada','cancelado','reembolsada','reembolsado') GROUP BY segment ORDER BY commission DESC""").fetchall()
        recent=con.execute("SELECT * FROM sales ORDER BY sale_date DESC,id DESC LIMIT 100").fetchall()
    return totals,by_product,by_segment,recent
