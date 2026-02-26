"""分析登入頁和登入後頁面結構。"""

import json
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os

load_dotenv("credentials.env")


def inspect_all():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # ===== 1. 登入頁面 =====
        page.goto("https://account.ncut.edu.tw/APSWIS_Q/Login_L_Q.asp")
        page.wait_for_load_state("networkidle")

        # 找驗證碼圖片
        captcha_info = page.evaluate("""() => {
            const imgs = document.querySelectorAll('img');
            return Array.from(imgs).map(img => ({
                src: img.src,
                alt: img.alt,
                id: img.id,
                name: img.name,
                width: img.width,
                height: img.height,
                onclick: img.getAttribute('onclick'),
            }));
        }""")
        print("=" * 60)
        print("ALL IMAGES ON LOGIN PAGE")
        print("=" * 60)
        print(json.dumps(captcha_info, ensure_ascii=False, indent=2))

        # 取得完整 HTML source 看驗證碼區塊
        captcha_html = page.evaluate("""() => {
            // 找 CheckCode 附近的 HTML
            const input = document.getElementById('CheckCode') || document.querySelector('input[name="CheckCode"]');
            if (input) {
                return input.parentElement.parentElement.innerHTML;
            }
            return 'CheckCode not found';
        }""")
        print("\n--- CheckCode 附近 HTML ---")
        print(captcha_html)

        # 取得整份 HTML (前 5000 字)
        full_html = page.evaluate("() => document.documentElement.outerHTML.substring(0, 8000)")
        print("\n--- Page HTML (first 8000 chars) ---")
        print(full_html)

        # ===== 2. 嘗試登入，監聽新視窗 =====
        print("\n" + "=" * 60)
        print("ATTEMPTING LOGIN...")
        print("=" * 60)

        page.fill('input[name="ID"]', os.getenv("USERNAME", ""))
        page.fill('input[name="PWD"]', os.getenv("PASSWORD", ""))

        # 先看驗證碼圖片 - 截圖驗證碼區域
        captcha_img = page.query_selector('img[src*="ValidCode"]') or page.query_selector('img[src*="valid"]') or page.query_selector('img[src*="check"]') or page.query_selector('img[src*="Check"]')
        if captcha_img:
            captcha_img.screenshot(path="output/captcha.png")
            print("Captcha screenshot saved to output/captcha.png")
        else:
            print("No captcha image found with common patterns")
            # 列出所有圖片的 src
            all_srcs = page.evaluate("() => Array.from(document.images).map(i => i.src)")
            print("All image srcs:", all_srcs)

        # 截圖填完帳密的畫面
        page.screenshot(path="output/login_filled.png", full_page=True)
        print("Filled login screenshot saved to output/login_filled.png")

        # 監聽 popup（新視窗）
        print("\nListening for popup window...")

        # 嘗試不填驗證碼直接送出，看看系統反應
        with context.expect_page(timeout=5000) as new_page_info:
            try:
                page.click('input[name="Enter"]', timeout=3000)
            except Exception:
                page.click('input[name="xEnter"]', timeout=3000)

        try:
            new_page = new_page_info.value
            new_page.wait_for_load_state("networkidle", timeout=10000)
            print(f"\nNew window URL: {new_page.url}")
            print(f"New window title: {new_page.title()}")

            # 分析新視窗
            new_page_html = new_page.evaluate("() => document.documentElement.outerHTML.substring(0, 10000)")
            print("\n--- New Window HTML (first 10000 chars) ---")
            print(new_page_html)

            new_page.screenshot(path="output/post_login.png", full_page=True)
            print("Post-login screenshot saved to output/post_login.png")
        except Exception as e:
            print(f"No popup detected or error: {e}")

            # 可能停留在同一頁面，看看有沒有錯誤訊息
            current_url = page.url
            print(f"Current URL after click: {current_url}")
            page.screenshot(path="output/after_click.png", full_page=True)
            print("After-click screenshot saved to output/after_click.png")

            # 看看是否有 alert
            page_text = page.evaluate("() => document.body.innerText.substring(0, 2000)")
            print(f"Page text: {page_text}")

        browser.close()


if __name__ == "__main__":
    inspect_all()
