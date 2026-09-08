import asyncio
import re
from playwright.async_api import async_playwright
from supabase import create_client, Client

SUPABASE_URL = "https://wimjkvkprixuumnuabjd.supabase.co"
SUPABASE_KEY = "sb_publishable_lS7N-qJOa6davBdF219uHg_x7fjrbZU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_to_db(brand, product_name, price, image_url, source_url):
    """公式サイトから取得した一次情報のみをSupabaseへ保存"""
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
        print(f"👕 [公式新着追加] {brand} | {product_name[:20]} | ¥{price:,} | {image_url[:30]}...")
    except Exception as e:
        print(f"❌ DB保存エラー: {e}")

async def fetch_beams_new_arrivals(page):
    """BEAMS公式ECの新作商品データ抽出"""
    print("🔎 BEAMS公式サイトのNew Arrivalsを取得中...")
    await page.goto("https://www.beams.co.jp/item/", wait_until="domcontentloaded", timeout=60000)
    await page.evaluate("window.scrollTo(0, 2000)")
    await page.wait_for_timeout(3000)

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
            
            # 価格抽出 (例: "¥15,400" -> 15400)
            price_text = await price_el.inner_text() if price_el else ""
            cleaned_price = re.sub(r'[^\d]', '', price_text)
            price = int(cleaned_price) if cleaned_price else 0

            # 直リンクURL
            url = await link_el.get_attribute("href") or ""
            if url and not url.startswith("http"):
                url = f"https://www.beams.co.jp{url}"

            # 公式画像を確実に取得 (Lazy load属性にも対応)
            img = await img_el.get_attribute("src") or await img_el.get_attribute("data-src") or ""
            if img.startswith("//"):
                img = "https:" + img

            if name and price > 0 and img:
                save_to_db("BEAMS", name, price, img, url)
        except Exception:
            continue

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await fetch_beams_new_arrivals(page)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
