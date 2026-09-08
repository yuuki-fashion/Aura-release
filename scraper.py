import asyncio
import re
from playwright.async_api import async_playwright
from supabase import create_client, Client

SUPABASE_URL = "https://wimjkvkprixuumnuabjd.supabase.co"
SUPABASE_KEY = "sb_publishable_lS7N-qJOa6davBdF219uHg_x7fjrbZU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_product(brand, product_name, price, image_url, source_url, category="アウター"):
    """Supabaseに新着商品を保存"""
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
        print(f"✅ [保存成功] {brand} | {product_name} | ¥{price:,}")
    except Exception as e:
        print(f"❌ DB保存エラー: {e}")

async def crawl_official_stores():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("🚀 ブランド公式サイト・公式ECからの新着アイテム直収集を開始します...")

        # 収集対象の公式ECリスト（順次拡張可能）
        # 各サイトのHTML/DOM構造に合わせて正確に抽出
        targets = [
            {
                "brand_default": "BEAMS",
                "url": "https://www.beams.co.jp/item/",
                "item_selector": ".item-list-item",
                "name_selector": ".item-name",
                "price_selector": ".item-price",
                "img_selector": "img",
                "link_selector": "a"
            }
        ]

        for target in targets:
            try:
                print(f"🔎 巡回中: {target['url']}")
                await page.goto(target['url'], wait_until="networkidle", timeout=60000)
                await page.wait_for_timeout(3000)

                # スクロールして画像を読み込ませる
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
                await page.wait_for_timeout(2000)

                items = await page.query_selector_all(target['item_selector'])
                print(f"📦 検出アイテム数: {len(items)}件")

                for item in items:
                    try:
                        name_el = await item.query_selector(target['name_selector'])
                        price_el = await item.query_selector(target['price_selector'])
                        img_el = await item.query_selector(target['img_selector'])
                        link_el = await item.query_selector(target['link_selector'])

                        if not name_el or not price_el or not link_el:
                            continue

                        product_name = (await name_el.inner_text()).strip()
                        price_text = await price_el.inner_text()
                        
                        # 価格から数値抽出 (例: "¥12,800" -> 12800)
                        cleaned_price = re.sub(r'[^\d]', '', price_text)
                        if not cleaned_price:
                            continue
                        price = int(cleaned_price)

                        source_url = await link_el.get_attribute("href")
                        if source_url and not source_url.startswith("http"):
                            source_url = f"https://www.beams.co.jp{source_url}"

                        image_url = ""
                        if img_el:
                            image_url = await img_el.get_attribute("src") or await img_el.get_attribute("data-src") or ""

                        save_product(
                            brand=target['brand_default'],
                            product_name=product_name,
                            price=price,
                            image_url=image_url,
                            source_url=source_url,
                            category="トップス"
                        )
                    except Exception as item_err:
                        continue

            except Exception as e:
                print(f"⚠️ エラー ({target['url']}): {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(crawl_official_stores())
    print("✨ 全クロール処理が完了しました。")
