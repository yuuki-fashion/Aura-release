import asyncio
import re
from playwright.async_api import async_playwright
from supabase import create_client, Client

SUPABASE_URL = "https://wimjkvkprixuumnuabjd.supabase.co"
SUPABASE_KEY = "sb_publishable_lS7N-qJOa6davBdF219uHg_x7fjrbZU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_product(brand, product_name, price, image_url, source_url):
    if not product_name or not source_url:
        return
    data = {
        "brand": brand,
        "product_name": product_name,
        "price": price if price > 0 else 12800,
        "image_url": image_url,
        "source_url": source_url,
        "category": "NEW"
    }
    try:
        supabase.table("products").upsert(data, on_conflict="source_url").execute()
        print(f"👕 [新作取得完了] {brand} | {product_name[:15]}... | ¥{data['price']:,}")
    except Exception as e:
        print(f"❌ DBエラー: {e}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("🚀 BEAMS公式ストアから新作服の画像・価格・URLを直接抽出中...")
        
        try:
            await page.goto("https://www.beams.co.jp/item/", wait_until="networkidle", timeout=60000)
            await page.evaluate("window.scrollTo(0, 2000)")
            await page.wait_for_timeout(3000)

            items = await page.query_selector_all(".item-list-item")
            for item in items[:25]:
                try:
                    name_el = await item.query_selector(".item-name")
                    price_el = await item.query_selector(".item-price")
                    img_el = await item.query_selector("img")
                    link_el = await item.query_selector("a")

                    if not name_el or not link_el:
                        continue

                    name = (await name_el.inner_text()).strip()
                    
                    price = 0
                    if price_el:
                        p_text = await price_el.inner_text()
                        c_price = re.sub(r'[^\d]', '', p_text)
                        if c_price:
                            price = int(c_price)

                    url = await link_el.get_attribute("href") or ""
                    if url and not url.startswith("http"):
                        url = f"https://www.beams.co.jp{url}"

                    img = ""
                    if img_el:
                        img = await img_el.get_attribute("src") or await img_el.get_attribute("data-src") or ""

                    save_product("BEAMS", name, price, img, url)
                except Exception:
                    continue
        except Exception as e:
            print(f"エラー: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
