import asyncio
import re
from playwright.async_api import async_playwright
from supabase import create_client, Client

SUPABASE_URL = "https://wimjkvkprixuumnuabjd.supabase.co"
SUPABASE_KEY = "sb_publishable_lS7N-qJOa6davBdF219uHg_x7fjrbZU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 古いゴミデータを全削除
print("🧹 以前の古いデータをデータベースから削除中...")
try:
    supabase.table("products").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("✨ データベースのクリーンアップが完了しました。")
except Exception as e:
    print(f"⚠️ 清掃スキップ: {e}")

def save_to_db(brand, product_name, price, image_url, source_url):
    data = {
        "brand": brand,
        "product_name": product_name,
        "price": price,
        "image_url": image_url,
        "source_url": source_url,
        "category": "NEW"
    }
    try:
        supabase.table("products").insert(data).execute()
        print(f"👕 [登録成功] {brand} | {product_name[:15]} | ¥{price:,}")
    except Exception as e:
        print(f"❌ 保存エラー: {e}")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("🚀 BEAMS公式サイトから新作アイテムを抽出中...")
        await page.goto("https://www.beams.co.jp/item/", wait_until="networkidle", timeout=60000)
        
        # 画像読み込み用スクロール
        await page.evaluate("window.scrollTo(0, 1500)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 3000)")
        await page.wait_for_timeout(2000)

        items = await page.query_selector_all(".item-list-item")
        for item in items[:20]:
            try:
                name_el = await item.query_selector(".item-name")
                price_el = await item.query_selector(".item-price")
                img_el = await item.query_selector("img")
                link_el = await item.query_selector("a")

                if not name_el or not link_el or not img_el:
                    continue

                name = (await name_el.inner_text()).strip()

                # 価格
                price = 0
                if price_el:
                    p_text = await price_el.inner_text()
                    nums = re.sub(r'[^\d]', '', p_text)
                    if nums:
                        price = int(nums)

                # URL
                url = await link_el.get_attribute("href") or ""
                if url and not url.startswith("http"):
                    url = f"https://www.beams.co.jp{url}"

                # 画像
                img = ""
                for attr in ["data-src", "src", "srcset"]:
                    val = await img_el.get_attribute(attr)
                    if val:
                        img = val.split()[0]
                        if img.startswith("//"):
                            img = "https:" + img
                        if "http" in img and "placeholder" not in img:
                            break

                if name and img and price > 0:
                    save_to_db("BEAMS", name, price, img, url)
            except Exception:
                continue

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
