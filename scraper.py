import asyncio
import re
from playwright.async_api import async_playwright
from supabase import create_client, Client

SUPABASE_URL = "https://wimjkvkprixuumnuabjd.supabase.co"
SUPABASE_KEY = "sb_publishable_lS7N-qJOa6davBdF219uHg_x7fjrbZU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_to_db(brand, product_name, price, image_url, source_url):
    if not product_name or not source_url:
        return

    data = {
        "brand": brand,
        "product_name": product_name,
        "price": price,
        "image_url": image_url,
        "source_url": source_url,
        "category": "NEW"
    }

    try:
        supabase.table("products").upsert(data, on_conflict="source_url").execute()
        print(f"👕 [成功] {brand} | {product_name[:15]} | ¥{price:,} | Img: {image_url[:20]}...")
    except Exception as e:
        print(f"❌ DBエラー: {e}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("🚀 公式ECから画像・価格・商品名をダイレクト取得中...")
        await page.goto("https://www.beams.co.jp/item/", wait_until="networkidle", timeout=60000)
        
        # 画像ローディング用にスクロール
        await page.evaluate("window.scrollTo(0, 1500)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 3000)")
        await page.wait_for_timeout(2000)

        items = await page.query_selector_all(".item-list-item")
        for item in items[:30]:
            try:
                name_el = await item.query_selector(".item-name")
                price_el = await item.query_selector(".item-price")
                img_el = await item.query_selector("img")
                link_el = await item.query_selector("a")

                if not name_el or not link_el or not img_el:
                    continue

                name = (await name_el.inner_text()).strip()

                # 価格取得
                price = 0
                if price_el:
                    price_text = await price_el.inner_text()
                    c_price = re.sub(r'[^\d]', '', price_text)
                    if c_price:
                        price = int(c_price)

                # URL取得
                url = await link_el.get_attribute("href") or ""
                if url and not url.startswith("http"):
                    url = f"https://www.beams.co.jp{url}"

                # 画像URLの確実に取れる属性を順にチェック
                img = ""
                for attr in ["data-src", "src", "data-original", "srcset"]:
                    val = await img_el.get_attribute(attr)
                    if val and "http" in val or val.startswith("//"):
                        img = val.split()[0] # srcset等の場合は最初のURLを取得
                        break

                if img.startswith("//"):
                    img = "https:" + img

                if name and img and price > 0:
                    save_to_db("BEAMS", name, price, img, url)
            except Exception as e:
                continue

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
