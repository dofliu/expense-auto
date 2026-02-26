"""測試登入：驗證修復後的登入流程。"""

import json
from playwright.sync_api import sync_playwright
from form_filler import login
from config import OUTPUT_DIR


def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.new_page()

        try:
            menu_page = login(context)
            print(f"\n=== 登入成功 ===")
            print(f"  URL: {menu_page.url}")
            print(f"  Title: {menu_page.title()}")

            # 截圖
            menu_page.screenshot(path=f"{OUTPUT_DIR}/post_login.png", full_page=True)

            # 分析頁面結構
            info = menu_page.evaluate("""() => ({
                url: location.href,
                title: document.title,
                frames: [...document.querySelectorAll('frame,iframe')].map(f => ({
                    src: f.src, name: f.name, id: f.id
                })),
                links: [...document.querySelectorAll('a')].slice(0, 20).map(a => ({
                    href: a.href, text: a.innerText.trim()
                })),
                bodyText: document.body?.innerText?.substring(0, 500),
            })""")
            print(json.dumps(info, ensure_ascii=False, indent=2))

            # 如果有 frame，檢查 frameset 結構
            frameset = menu_page.evaluate("""() => {
                const fs = document.querySelector('frameset');
                if (!fs) return null;
                return {
                    outerHTML: fs.outerHTML.substring(0, 2000),
                    frames: [...fs.querySelectorAll('frame')].map(f => ({
                        name: f.name, src: f.src
                    }))
                };
            }""")
            if frameset:
                print(f"\n=== Frameset 結構 ===")
                print(json.dumps(frameset, ensure_ascii=False, indent=2))

        except Exception as e:
            print(f"登入失敗: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    test_login()
