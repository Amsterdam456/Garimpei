import requests
SEARCH_URL="https://api.mercadolibre.com/sites/{site_id}/search"

def search_products(term,site_id="MLB",max_price=1000,min_discount=15):
    response=requests.get(SEARCH_URL.format(site_id=site_id),params={"q":term,"limit":50},timeout=20)
    response.raise_for_status()
    results=[]
    for p in response.json().get("results",[]):
        price=p.get("price"); original=p.get("original_price")
        if price is None or float(price)>max_price: continue
        discount=None
        if original and float(original)>float(price)>0:
            discount=round((float(original)-float(price))/float(original)*100,1)
        if discount is None or discount<min_discount: continue
        results.append({"source":"mercadolivre","product_id":str(p.get("id","")),"title":p.get("title","Produto sem título"),
            "price":float(price),"original_price":float(original) if original else None,"discount_percent":discount,
            "product_url":p.get("permalink",""),"image_url":p.get("thumbnail","")})
    return results
