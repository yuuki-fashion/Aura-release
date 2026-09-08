import asyncio
import re
from playwright.async_api import async_playwright
from supabase import create_client, Client

SUPABASE_URL = "https://wimjkvkprixuumnuabjd.supabase.co"
SUPABASE_KEY = "sb_publishable_lS7N-qJOa6davBdF219uHg_x7fjrbZU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_product(brand, product_name, price, image_url, source_url, category="NEW"):
    """Supabaseへ新作服アイテムを確実に保存"""
    if not product_name or not price or not source_url:
        return
        
    data = {
        "brand": brand,
        "product_name": product_name,
        "price": price,
        "image_url": image_url,
        "source_url": source_url,
        "category": category
    }
    try:
        supabase.table("products").upsert(data, on_conflict="source_url").execute()
        print(f"👕 [新作服追加] {brand} | {product_name} | ¥{price:,}")
    except Exception as e:
        print(f"❌ DB保存エラー: {e}")

async def crawl_brand_stores():
    print("🚀 ブランド公式サイトの【新作アイテム】直収集を開始します...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # BEAMS 新作服一覧ページ
        try:
            print("🔎 BEAMS 公式新作ページを巡回中...")
            await page.goto("https://www.beams.co.jp/item/", wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)
            
            # 画像の遅延読み込み対策で少しスクロール
            await page.evaluate("window.scrollTo(0, 1500)")
            await page.wait_for_timeout(2000)

            items = await page.query_selector_all(".item-list-item")
            print(f"📦 BEAMSで検出した新作服: {len(items)}件")

            for item in items[:30]:
                try:
                    name_el = await item.query_selector(".item-name")
                    price_el = await item.query_selector(".item-price")
                    img_el = await item.query_selector("img")
                    link_el = await item.query_selector("a")

                    if not name_el or not price_el or not link_el:
                        continue

                    product_name = (await name_el.inner_text()).strip()
                    price_text = await price_el.inner_text()
                    
                    cleaned_price = re.sub(r'[^\d]', '', price_text)
                    if not cleaned_price:
                        continue
                    price = int(cleaned_price)

                    source_url = await link_el.get_attribute("href") or ""
                    if source_url and not source_url.startswith("http"):
                        source_url = f"https://www.beams.co.jp{source_url}"

                    image_url = ""
                    if img_el:
                        image_url = await img_el.get_attribute("src") or await img_el.get_attribute("data-src") or ""

                    save_product(
                        brand="BEAMS",
                        product_name=product_name,
                        price=price,
                        image_url=image_url,
                        source_url=source_url,
                        category="NEW"
                    )
                except Exception:
                    continue
        except Exception as e:
            print(f"⚠️ エラー: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_brand_stores())
    print("✨ 新作服の自動収集が完了しました。")
