"""Playwright 自動填單：登入核銷系統、導航到表單、填寫。"""

import os
import json
import time

from playwright.sync_api import sync_playwright, Page, BrowserContext, Frame
import google.generativeai as genai
from PIL import Image

from config import (
    SYSTEM_URL, USERNAME, PASSWORD,
    LOGIN_SELECTORS, MENU_URL, OUTPUT_DIR,
    EXPENSE_CATEGORY, APPP_FIELDS, APPY_FIELDS,
    DEFAULT_SUBJECT,
)


# ────────────────────────────────────────────────────────
# Captcha OCR
# ────────────────────────────────────────────────────────

def solve_captcha(page: Page) -> str:
    """截圖驗證碼圖片，用 Gemini 辨識回傳數字字串。"""
    captcha_img = page.query_selector(LOGIN_SELECTORS["captcha_image"])
    if not captcha_img:
        raise RuntimeError("找不到驗證碼圖片")

    captcha_path = f"{OUTPUT_DIR}/captcha_tmp.png"
    captcha_img.screenshot(path=captcha_path)

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-3.1-pro-preview")
    image = Image.open(captcha_path)

    response = model.generate_content([
        "這是一張網站驗證碼圖片，背景是紅色，上面有白色數字。"
        "請仔細辨識圖中的6位數字。只回傳純數字，不要空格或其他文字。",
        image,
    ])
    code = response.text.strip()
    print(f"  驗證碼辨識結果: {code}")
    return code


# ────────────────────────────────────────────────────────
# Login
# ────────────────────────────────────────────────────────

def login(context: BrowserContext, max_retries: int = 5) -> Page:
    """
    登入核銷系統，處理驗證碼和新視窗彈出。

    Returns:
        登入後的新視窗 Page 物件（主選單頁面）
    """
    page = context.pages[0]
    page.on("dialog", lambda d: d.accept())

    for attempt in range(1, max_retries + 1):
        print(f"  登入嘗試 {attempt}/{max_retries}...")

        page.goto(SYSTEM_URL)
        page.wait_for_load_state("networkidle")

        # 填入帳號密碼
        page.fill(LOGIN_SELECTORS["user_id"], USERNAME)
        page.fill(LOGIN_SELECTORS["password"], PASSWORD)

        # 辨識並填入驗證碼
        captcha_code = solve_captcha(page)
        page.fill(LOGIN_SELECTORS["captcha_input"], captcha_code)

        # 用 JS 點擊隱藏的 xEnter 按鈕提交表單
        try:
            with context.expect_page(timeout=15000) as new_page_info:
                page.evaluate("document.getElementById('xEnter').click()")

            new_page = new_page_info.value
            new_page.wait_for_load_state("networkidle", timeout=15000)
            print(f"  登入成功！新視窗: {new_page.url}")
            return new_page

        except Exception:
            time.sleep(1)
            body = page.content()
            if "帳號密碼錯誤" in body:
                print(f"  帳號密碼錯誤（第 {attempt} 次）")
            elif "驗證碼" in body:
                print(f"  驗證碼錯誤（第 {attempt} 次）")
            else:
                print(f"  登入失敗，未知原因（第 {attempt} 次）")

            if attempt == max_retries:
                raise RuntimeError(f"登入失敗，已嘗試 {max_retries} 次")
            print("  重新嘗試...")

    raise RuntimeError("登入失敗")


# ────────────────────────────────────────────────────────
# Navigate to expense form
# ────────────────────────────────────────────────────────

def navigate_to_expense_form(menu_page: Page) -> dict:
    """
    從主選單導航到「直接核銷(零用金)」表單。

    Steps:
        1. 點擊 LIS2 (部門請購查詢) → 子選單出現
        2. 點擊「新增請購」(aBT2) → MAIN 載入類別選擇頁
        3. 選 CHK3 (直接核銷) → 下一步
        4. MAIN 變成 STD_APPY_FRM_Q.asp (frameset)

    Returns:
        dict with frame references: {"appy": Frame, "appp": Frame, "appa": Frame}
    """
    print("  導航到核銷表單...")

    # Step 1: 點擊 LIS2（部門請購查詢）
    title_frame = menu_page.frame("TITLE")
    title_frame.evaluate("LIS2()")
    time.sleep(2)

    # Step 2: 點擊「新增請購」
    title_frame = menu_page.frame("TITLE")
    title_frame.wait_for_load_state("networkidle", timeout=10000)
    title_frame.evaluate("""() => {
        parent.FM.rows="15%,*,0,0,0,0,0";
        document.querySelector('a[name=aBT2]').click();
    }""")
    time.sleep(3)

    # 取得 MAIN frame（此時是 DA_APP_Q.asp 類別選擇頁）
    main_frame = None
    for f in menu_page.frames:
        if "DA_APP_Q" in f.url:
            main_frame = f
            break
    if not main_frame:
        main_frame = menu_page.frame("MAIN")

    main_frame.wait_for_load_state("networkidle", timeout=15000)

    # Step 3: 選 CHK3 (直接核銷) + 提交
    chk_name = EXPENSE_CATEGORY["checkbox"]
    main_frame.evaluate(f"document.querySelector('input[name={chk_name}]').click()")
    time.sleep(1)

    with main_frame.expect_navigation(timeout=15000):
        main_frame.evaluate("document.querySelector('input[name=SSS]').click()")
    time.sleep(3)

    # Step 4: 找到 nested frames (APPY, APPP, APPA)
    frames = {}
    for f in menu_page.frames:
        if "STD_APPY_Q" in f.url:
            frames["appy"] = f
        elif "STD_APPP_Q" in f.url:
            frames["appp"] = f
        elif "STD_APPA_Q" in f.url:
            frames["appa"] = f

    # 等待 frames 載入
    for name, frame in frames.items():
        try:
            frame.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            print(f"  警告: {name} frame 載入超時")

    print(f"  核銷表單已開啟 (找到 {len(frames)} 個 frame)")
    return frames


# ────────────────────────────────────────────────────────
# Fill expense form
# ────────────────────────────────────────────────────────

def _js_escape(text: str) -> str:
    """Escape text for safe insertion into JS string literals."""
    return (text
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace("\n", "\\n")
            .replace("\r", "\\r"))


def _roc_date(iso_date: str) -> tuple:
    """
    將 ISO 日期 (YYYY-MM-DD) 轉為 ROC (民國) 年/月/日 tuple。

    Example: "2025-03-15" → ("114", "03", "15")
    """
    parts = iso_date.split("-")
    year = int(parts[0]) - 1911
    month = parts[1]
    day = parts[2]
    return (str(year), month, day)


def fill_appy_frame(appy_frame: Frame, menu_page: Page,
                     amount: int, subject_code: str = ""):
    """
    填寫 APPY frame（表頭）：計畫編號、經費用途、科目、金額。

    APPY frame 使用級聯 dropdown：
        BUGETNO_1 → BN_1() → BUGCODE_1 → BC_1() → SERSUB_1 / D_AMOUNT_1

    對於零用金（直接核銷），BUGET 只有一個預設選項（空值）。
    關鍵是選擇正確的會計科目 (SERSUB_1) 和填入金額 (D_AMOUNT_1)。

    Args:
        appy_frame: APPY Frame 物件
        menu_page: 主選單 Page（用於跨 frame 等待）
        amount: 金額
        subject_code: 會計科目代碼（如 "110704-8012"），為空則用 DEFAULT_SUBJECT
    """
    if not subject_code:
        subject_code = DEFAULT_SUBJECT

    print("  填寫 APPY（表頭/計畫經費）...")

    # ── Step 1: 選擇計畫編號（BUGETNO_1 index 1 = 預設空值）
    appy_frame.evaluate("""() => {
        const sel = FORM1.BUGETNO_1;
        if (sel && sel.options.length > 1) {
            sel.selectedIndex = 1;
            // 觸發 onchange → BN_1() 以填充 BUGCODE_1
            sel.dispatchEvent(new Event('change'));
        }
    }""")
    time.sleep(0.5)
    print("    計畫編號: 已選擇預設")

    # ── Step 2: 選擇經費用途（BUGCODE_1 index 1 = 預設）
    appy_frame.evaluate("""() => {
        const sel = FORM1.BUGCODE_1;
        if (sel && sel.options.length > 1) {
            sel.selectedIndex = 1;
        }
    }""")
    time.sleep(0.5)
    print("    經費用途: 已選擇預設")

    # ── Step 3: 觸發 BC_1() 取得經費餘額（透過 LA_AM frame 提交）
    try:
        appy_frame.evaluate("BC_1()")
        time.sleep(2)  # 等 LA_AM frame 回傳
        print("    經費餘額: 已查詢")
    except Exception as e:
        print(f"    警告: BC_1() 失敗 ({e})")

    # ── Step 4: 填充科目 (SERSUB_1) 並選擇
    # 先呼叫 SS_1() 填充 SERSUB_1 的 option list
    appy_frame.evaluate("SS_1()")
    time.sleep(0.5)

    # 選擇指定的科目
    subject_esc = _js_escape(subject_code)
    selected = appy_frame.evaluate(f"""() => {{
        const sel = FORM1.SERSUB_1;
        if (!sel) return {{error: 'SERSUB_1 not found'}};

        // 找到匹配的科目
        for (let i = 0; i < sel.options.length; i++) {{
            if (sel.options[i].value === '{subject_esc}') {{
                sel.selectedIndex = i;
                // 同步到 SUBJECTNO_1
                FORM1.SUBJECTNO_1.value = sel.value;
                return {{
                    found: true,
                    index: i,
                    value: sel.value,
                    text: sel.options[i].text,
                }};
            }}
        }}
        return {{
            found: false,
            totalOptions: sel.options.length,
            searchedFor: '{subject_esc}',
        }};
    }}""")

    if isinstance(selected, dict) and selected.get("found"):
        print(f"    科目: {selected['text']}")
    else:
        print(f"    警告: 找不到科目 {subject_code}，選項數: {selected}")

    # ── Step 5: 填入金額 (D_AMOUNT_1)
    appy_frame.evaluate(f"""() => {{
        const el = FORM1.D_AMOUNT_1;
        if (el) el.value = '{amount}';
    }}""")
    print(f"    金額: {amount}")

    print("  APPY 填寫完成")


def fill_expense_form(frames: dict, receipt_data: dict,
                      menu_page: Page = None):
    """
    將 OCR 辨識結果填入核銷表單。

    Args:
        frames: navigate_to_expense_form() 回傳的 frame dict
        receipt_data: ocr.py 回傳的發票資料，格式:
            {
                "date": "2025-03-15",
                "vendor": "全家便利商店",
                "amount": 150,
                "tax_id": "12345678",
                "invoice_no": "AB-12345678",
                "items": [{"name": "文具用品", "quantity": 1, "price": 150}],
                "subject_code": "110704-8012"  # 選填，會計科目
            }
        menu_page: 主選單 Page（用於 APPY frame 跨 frame 操作）
    """
    appp_frame = frames.get("appp")
    appy_frame = frames.get("appy")

    if not appp_frame:
        raise RuntimeError("找不到 APPP frame（品項明細）")

    print("  填寫核銷表單...")

    # ── 1. 填寫用途說明 ──────────────────────────
    vendor = receipt_data.get("vendor", "")
    items_desc = ", ".join(
        item.get("name", "") for item in receipt_data.get("items", [])
    )
    content_text = f"{vendor} - {items_desc}" if items_desc else vendor

    # 用 JS 填寫（frameset 結構下 Playwright fill() 可能報 not visible）
    appp_frame.evaluate(f"""() => {{
        const el = document.querySelector('textarea[name="{APPP_FIELDS["content"]}"]');
        if (el) {{ el.value = "{_js_escape(content_text)}"; }}
    }}""")
    print(f"    用途說明: {content_text}")

    # ── 2. 填寫憑證日期 ─────────────────────────
    date_str = receipt_data.get("date", "")
    if date_str:
        roc_y, roc_m, roc_d = _roc_date(date_str)

        # 先勾選啟用 checkbox，再填日期 selects（全部用 JS）
        appp_frame.evaluate(f"""() => {{
            // 啟用憑證日期
            const cb = document.querySelector('input[name="{APPP_FIELDS["receipt_date_checkbox"]}"]');
            if (cb && !cb.checked) cb.click();

            // 設定年月日
            ['RCDAT_Y', 'RCDAT_M', 'RCDAT_D'].forEach((name, i) => {{
                const val = ['{roc_y}', '{roc_m}', '{roc_d}'][i];
                const el = document.querySelector('select[name="' + name + '"]');
                if (el) {{ el.disabled = false; el.value = val; }}
            }});
        }}""")
        time.sleep(0.5)
        print(f"    憑證日期: 民國{roc_y}/{roc_m}/{roc_d}")

    # ── 3. 填寫品項明細 ─────────────────────────
    # 欄位名稱格式: PRODUCT_{N}, PRODUCT1_{N}, PRODUCT2_{N},
    #               SERUNIT_{N}, QUANTITY_{N}, AMOUNT_{N}
    # N = 1~15 (最多 15 列)
    items = receipt_data.get("items", [])
    total_amount = receipt_data.get("amount", 0)

    for i, item in enumerate(items[:15], start=1):
        item_name = _js_escape(str(item.get("name", "")))
        item_spec = _js_escape(str(item.get("spec", "")))
        item_qty = item.get("quantity", 1)
        item_price = item.get("price", total_amount if i == 1 else 0)

        appp_frame.evaluate(f"""() => {{
            const setVal = (name, val) => {{
                const el = document.querySelector('input[name="' + name + '"]');
                if (el) el.value = val;
            }};
            setVal('PRODUCT_{i}',  '{item_name}');   // 品名
            setVal('PRODUCT1_{i}', '{item_spec}');    // 詳細規格
            setVal('SERUNIT_{i}',  '式');             // 單位
            setVal('QUANTITY_{i}', '{item_qty}');      // 數量
            setVal('AMOUNT_{i}',   '{item_price}');    // 總價
        }}""")
        print(f"    品項{i}: {item.get('name', '')} x{item_qty} = {item_price}")

    if not items and total_amount:
        # 沒有明細品項時，只填金額到第一列
        appp_frame.evaluate(f"""() => {{
            const el = document.querySelector('input[name="AMOUNT_1"]');
            if (el) el.value = '{total_amount}';
        }}""")
        print(f"    金額: {total_amount}")

    # ── 4. 填寫 APPY frame（計畫/經費/科目/金額）──────
    if appy_frame and menu_page:
        subject_code = receipt_data.get("subject_code", "")
        fill_appy_frame(appy_frame, menu_page, total_amount, subject_code)
    elif not appy_frame:
        print("  警告: 找不到 APPY frame，跳過計畫/經費填寫")

    print("  表單填寫完成（部分欄位可能需要手動確認）")


# ────────────────────────────────────────────────────────
# Main entry point
# ────────────────────────────────────────────────────────

def start_browser(headless: bool = True):
    """
    啟動 Playwright 瀏覽器，回傳 (playwright, browser, context)。

    呼叫者負責關閉瀏覽器和 Playwright：
        pw, browser, context = start_browser()
        ...
        browser.close()
        pw.stop()
    """
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    context = browser.new_context()
    context.new_page()
    return pw, browser, context


def run_form_fill(receipt_data: dict, headless: bool = True):
    """
    完整流程：啟動瀏覽器 → 登入 → 導航 → 填單。

    Returns:
        (menu_page, frames, browser, pw) 以便後續操作。
        呼叫者負責 browser.close() 和 pw.stop()。
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    pw, browser, context = start_browser(headless=headless)

    try:
        # 1. 登入
        menu_page = login(context)

        # 2. 導航到核銷表單
        frames = navigate_to_expense_form(menu_page)

        # 3. 填寫表單
        fill_expense_form(frames, receipt_data, menu_page=menu_page)

        # 截圖
        menu_page.screenshot(
            path=f"{OUTPUT_DIR}/filled_form.png", full_page=True
        )
        print(f"  截圖已存: {OUTPUT_DIR}/filled_form.png")

        return menu_page, frames, browser, pw

    except Exception:
        browser.close()
        pw.stop()
        raise


if __name__ == "__main__":
    # 測試用假資料
    test_data = {
        "date": "2025-03-15",
        "vendor": "全家便利商店",
        "amount": 150,
        "tax_id": "12345678",
        "invoice_no": "AB-12345678",
        "items": [
            {"name": "文具用品", "quantity": 1, "price": 150}
        ],
    }

    print("=== 核銷自動填單測試 ===")
    menu_page, frames, browser, pw = run_form_fill(test_data, headless=True)
    print("=== 完成 ===")
    browser.close()
    pw.stop()
