import asyncio
import re
from playwright.async_api import async_playwright
from supabase import create_client, Client

SUPABASE_URL = "https://wimjkvkprixuumnuabjd.supabase.co"
SUPABASE_KEY = "sb_publishable_lS7N-qJOa6davBdF219uHg_x7fjrbZU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. 過去のゴミデータを一括削除
print("🧹 以前の不完全なデータを削除中...")
try:
    supabase.table("products").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("✨ クリーンアップ完了")
except Exception as e:
    print(f"⚠️ 削除通知: {e}")

def save_item(brand, name, price, img, url):
    if not name or not url or not img or price <= 0:
        return False
    data = {
        "brand": brand,
        "product_name": name,
        "price": price,
        "image_url": img,
        "source_url": url,
        "category": "NEW"
    }
    try:
        supabase.table("products").insert(data).execute()
        print(f"👕 [登録完了] {brand} | {name[:18]} | ¥{price:,}")
        return True
    except Exception as e:
        print(f"❌ DBエラー: {e}")
        return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 一般的なPCブラウザに偽装
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        print("🚀 公式ストアから新作アイテム・画像・価格を抽出中...")
        saved_count = 0

        try:
            await page.goto("https://www.beams.co.jp/item/", wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)

            # 画像遅延読み込みを解除するためにスクロール
            for i in range(1, 5):
                await page.evaluate(f"window.scrollTo(0, {i * 1000})")
                await page.wait_for_timeout(1000)

            items = await page.query_selector_all(".item-list-item")
            
            for item in items:
                try:
                    name_el = await item.query_selector(".item-name")
                    price_el = await item.query_selector(".item-price")
                    img_el = await item.query_selector("img")
                    link_el = await item.query_selector("a")

                    if not name_el or not link_el or not img_el:
                        continue

                    name = (await name_el.inner_text()).strip()

                    # 価格のパース
                    price = 0
                    if price_el:
                        p_text = await price_el.inner_text()
                        digits = re.sub(r'[^\d]', '', p_text)
                        if digits:
                            price = int(digits)

                    # 直リンク
                    url = await link_el.get_attribute("href") or ""
                    if url and not url.startswith("http"):
                        url = f"https://www.beams.co.jp{url}"

                    # 画像URLの確実な取得
                    img = ""
                    for attr in ["src", "data-src", "data-original"]:
                        val = await img_el.get_attribute(attr)
                        if val and ("http" in val or val.startswith("//")):
                            img = val.split()[0]
                            break

                    if img.startswith("//"):
                        img = "https:" + img

                    if save_item("BEAMS", name, price, img, url):
                        saved_count += 1
                        if saved_count >= 20:
                            break
                except Exception:
                    continue

        except Exception as e:
            print(f"スクレイピング例外: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
