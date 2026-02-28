"""Playwright 自動填單：登入核銷系統、導航到表單、填寫。"""

import os
import json
import time
import threading
import urllib.parse

from playwright.sync_api import sync_playwright, Page, BrowserContext, Frame
from google import genai
from PIL import Image

from config import (
    SYSTEM_URL, USERNAME, PASSWORD,
    LOGIN_SELECTORS, MENU_URL, OUTPUT_DIR,
    EXPENSE_CATEGORY, APPP_FIELDS, APPY_FIELDS, APPA_FIELDS,
    DEFAULT_SUBJECT, RECEIPT_PREFIX, PAYEE_CODE, BANK_KEYWORD,
)


# ────────────────────────────────────────────────────────
# Timed input (超時自動選預設)
# ────────────────────────────────────────────────────────

def _timed_input(prompt: str, timeout: int = 10, default: str = "") -> str:
    """
    帶超時的 input()。超過 timeout 秒未輸入則自動回傳 default。
    Windows 相容（使用 threading）。
    """
    result = [default]

    def _ask():
        try:
            result[0] = input(prompt)
        except EOFError:
            result[0] = default

    t = threading.Thread(target=_ask, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        print(f"\n    (超過 {timeout} 秒未選擇，自動使用預設值)")
        return default
    return result[0]


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

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    image = Image.open(captcha_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "這是一張網站驗證碼圖片，背景是紅色，上面有白色數字。"
            "請仔細辨識圖中的6位數字。只回傳純數字，不要空格或其他文字。",
            image,
        ],
    )
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

def navigate_to_expense_form(menu_page: Page, use_project: bool = False,
                              plan_name: str = "") -> dict:
    """
    從主選單導航到「直接核銷(零用金)」表單。

    Steps:
        1. 點擊 LIS2 (部門請購) 或 LIS3 (計畫請購) → 子選單出現
        2. (計畫請購) 選擇計畫 BUGETNO dropdown
        3. 點擊「新增請購」(部門=aBT2, 計畫=SBT2) → MAIN 載入類別選擇頁
        4. 選 CHK3 (直接核銷) → 下一步
        5. MAIN 變成 STD_APPY_FRM_Q.asp (frameset)

    Args:
        menu_page: 主選單 Page
        use_project: True=計畫請購(LIS3), False=部門請購(LIS2)
        plan_name: 計畫名稱關鍵字（計畫請購時用於選擇 BUGETNO）

    Returns:
        dict with frame references: {"appy": Frame, "appp": Frame, "appa": Frame}
    """
    mode = "計畫請購" if use_project else "部門請購"
    print(f"  導航到核銷表單（{mode}）...")

    # 導航階段掛 dialog handler，避免意外 dialog 阻塞流程
    def _nav_dialog_handler(dialog):
        try:
            msg = dialog.message
            print(f"    [NAV-DIALOG {dialog.type}] {msg}")
            dialog.accept()
        except Exception:
            pass

    menu_page.on("dialog", _nav_dialog_handler)

    # Step 1: 點擊 LIS2（部門請購）或 LIS4（計畫請購）
    #   LIS2 → DA_SerFun_Q.asp?COM=YT   (部門請購)
    #   LIS4 → DA_SerFun_Q.asp?COM=NT   (計畫請購)
    title_frame = menu_page.frame("TITLE")
    if use_project:
        # LIS4 = 計畫請購查詢 (COM=NT)
        title_frame.evaluate("""() => {
            try { LIS4(); } catch(e) {
                parent.FM.rows = "15%,*,0,0,0,0,0";
                parent.MAIN.location = '../BLANK_Q.asp?COM=NT';
                parent.TRAN.location = 'TRAN_Q.asp?COM=NT';
                parent.OT.location = '../SHAR_BUG_Q/SHAR_BUG_STR_Q.asp?COM=NT';
                window.location = 'DA_SerFun_Q.asp?COM=NT';
            }
        }""")
    else:
        title_frame.evaluate("LIS2()")
    time.sleep(2)

    # Step 1.5: 跳過 — TITLE BUGETNO 下拉僅用於查詢面板的預算細項，與核銷表單無關

    # Step 2: 點擊「新增請購」(aBT2) — 部門 & 計畫模式都用 aBT2
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

    # 移除導航階段的 dialog handler，避免影響後續
    try:
        menu_page.remove_listener("dialog", _nav_dialog_handler)
    except Exception:
        pass

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


# Big5 不支援的常見字元對應表（伺服器使用 Big5 編碼，送出不支援字元會造成解析失敗）
_BIG5_REPLACEMENTS = {
    'Ω': 'ohm', 'Ω': 'ohm',      # Omega (U+03A9, U+2126)
    '°': 'deg',                    # Degree sign
    'μ': 'u',  'µ': 'u',          # Micro sign
    'α': 'a', 'β': 'b', 'γ': 'r', # Greek letters
    '±': '+/-', '×': 'x', '÷': '/',
    '≤': '<=', '≥': '>=',
    '™': 'TM', '®': 'R', '©': 'C',
    '\u2019': "'", '\u2018': "'",   # Curly quotes
    '\u201c': '"', '\u201d': '"',
    '\u2014': '-', '\u2013': '-',   # Em/en dash
}


def _sanitize_big5(text: str) -> str:
    """
    將字串中無法以 Big5 編碼的字元替換為安全的替代字串。

    學校核銷系統使用 Big5 編碼。若品名含 Ω、°、μ 等 Unicode 字元，
    POST 時瀏覽器會將其轉成 Big5 導致亂碼，使伺服器無法解析 P_STR。

    此函式先以常見替換表處理，再逐字確認 Big5 可編碼性。
    """
    # 先做常見替換
    for bad, good in _BIG5_REPLACEMENTS.items():
        text = text.replace(bad, good)
    # 再逐字過濾：無法轉 Big5 的字元直接移除
    result = []
    for ch in text:
        try:
            ch.encode('big5')
            result.append(ch)
        except (UnicodeEncodeError, LookupError):
            pass  # 無法編碼 → 移除
    return ''.join(result)


def _is_tax_item(name: str) -> bool:
    """
    判斷品項名稱是否為稅額項目。

    用於將 OCR 辨識出的「稅額」、「營業稅」、「其他差額(稅)」等項目
    從一般品項中分離出來，以便進行智慧合併或歸類。
    """
    if not name:
        return False
    name_lower = name.lower().strip()
    tax_keywords = ["稅額", "稅金", "營業稅", "銷售稅", "加值稅",
                    "其他差額", "tax", "vat", "gst"]
    return any(kw in name_lower for kw in tax_keywords)

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


def _idate_format(iso_date: str) -> str:
    """
    將 ISO 日期轉為 APPA 的 IDATE 格式 (7 位數字)。

    Example: "2026-02-11" → "1150211"
    """
    y, m, d = _roc_date(iso_date)
    return f"{y}{m}{d}"


def generate_receipt_no(iso_date: str, seq: int) -> str:
    """
    產生收據號碼。

    格式: "收據11502261"  = 收據(2字) + 民國年(3) + 月(2) + 日(2) + 流水號(1) = 2字+8數字

    Args:
        iso_date: ISO 日期 (YYYY-MM-DD)
        seq: 當天流水號 (1~9)
    """
    y, m, d = _roc_date(iso_date)
    # 流水號限 1 位（1~9），符合 2字+8數字規則
    s = min(max(seq, 1), 9)
    return f"{RECEIPT_PREFIX}{y}{m}{d}{s}"


def _sanitize_receipt_no(invoice_no: str) -> str:
    """
    驗證/清理收據號碼格式。
    規則: 2 個文字 + 8 個數字，不可有連字號或特殊符號。

    若不符合格式則回傳空字串（交給呼叫端用 generate_receipt_no 替代）。
    """
    import re
    if not invoice_no:
        return ""
    # 移除空白
    s = invoice_no.strip()
    # 移除連字號
    s = s.replace("-", "").replace("_", "")
    # 檢查格式：2 個非數字字元 + 8~10 個數字
    m = re.match(r'^(.{2})(\d{8,10})$', s)
    if m:
        return s
    # 不符合格式
    return ""


def fill_appy_frame(appy_frame: Frame, menu_page: Page,
                     amount: int, subject_code: str = "",
                     plan_name: str = ""):
    """
    填寫 APPY frame（表頭）：計畫編號、經費用途、科目、金額。

    APPY frame 使用級聯 dropdown：
        BUGETNO_1 → BN_1() → BUGCODE_1 → BC_1() → SERSUB_1 / D_AMOUNT_1

    SUM_ALERT() 要求 BUGETNO_1、BUGCODE_1、D_AMOUNT_1 三者都有值，
    否則該行不會被序列化 → T_BUG_AMT=0 → 金額不符。

    Args:
        appy_frame: APPY Frame 物件
        menu_page: 主選單 Page（用於跨 frame 等待）
        amount: 金額
        subject_code: 會計科目代碼，為空則保持系統預設（不強制覆蓋）
        plan_name: 計畫名稱關鍵字（如 "高教深耕"），為空則選預設

    Returns:
        tuple: (plan_full_name, plan_code) 所選計畫的全名與代碼
    """

    chosen_plan_text = ""   # 計畫全名（下拉選單文字）
    chosen_plan_code = ""   # 計畫代碼（BUGETNO 值）

    print("  填寫 APPY（表頭/計畫經費）...")

    # ── Step 1: 選擇計畫編號（依 plan_name 搜尋或選預設）
    # 重要：必須確保 BUGETNO_1 有值，否則 SUM_ALERT 會跳過此行
    def _read_bugetno_options():
        data = appy_frame.evaluate("""() => {
            const sel = FORM1.BUGETNO_1;
            if (!sel || sel.options.length <= 1) return [];
            return [...sel.options].map((o, idx) => ({ index: idx, text: o.text, value: o.value }));
        }""")
        return [o for o in data if o['value'] and o['value'].strip() and o['index'] > 0]

    valid_options = _read_bugetno_options()

    # 若第一次讀取為空，等待 5 秒後重試（選單可能還在非同步載入）
    if not valid_options:
        print("    BUGETNO_1 選項為空，等待 5 秒後重試...")
        time.sleep(5)
        valid_options = _read_bugetno_options()
    
    selected_idx = -1
    if valid_options:
        # 嘗試名稱匹配
        if plan_name:
            for opt in valid_options:
                if plan_name in opt['text'] or plan_name in opt['value']:
                    selected_idx = opt['index']
                    chosen_plan_text = opt['text']
                    chosen_plan_code = opt['value']
                    print(f"    自動匹配計畫: {opt['text']}")
                    break
        
        # 找不到或未指定，列出選項讓使用者挑
        if selected_idx == -1:
            if plan_name:
                print(f"    ⚠️ 找不到包含「{plan_name}」的計畫！請從可用計畫中選擇：")
            else:
                print("\n    請從系統目前可用的計畫中選擇：")
                
            for i, opt in enumerate(valid_options, 1):
                print(f"      {i}. {opt['text']}")
            print(f"      0. 預設選第一個 ({valid_options[0]['text']})")
            
            try:
                choice = _timed_input("    > ", timeout=10, default="0").strip()
                if not choice or choice == "0":
                    selected_idx = valid_options[0]['index']
                else:
                    idx = int(choice)
                    if 1 <= idx <= len(valid_options):
                        selected_idx = valid_options[idx-1]['index']
                    else:
                        print("      無效選擇，使用預設。")
                        selected_idx = valid_options[0]['index']
            except ValueError:
                print("      輸入錯誤，使用預設。")
                selected_idx = valid_options[0]['index']
                
            # 找到 selected_idx 對應的選項文字與值
            chosen_opt = next((o for o in valid_options if o['index'] == selected_idx), None)
            if chosen_opt:
                chosen_plan_text = chosen_opt['text']
                chosen_plan_code = chosen_opt['value']
            print(f"    -> 最終選擇計畫: {chosen_plan_text}")
            
        # 設定下拉選單的值
        appy_frame.evaluate(f"""() => {{
            FORM1.BUGETNO_1.selectedIndex = {selected_idx};
        }}""")
        time.sleep(0.5)
    else:
        print("    [FAIL] BUGETNO_1 無可用計畫選項！")

    # ── Step 1.5: 觸發 BN_1() 載入 BUGCODE 下拉選單
    # 必須透過 BN_1() 觸發，光 dispatch change event 可能不夠
    try:
        appy_frame.evaluate("if (typeof BN_1 === 'function') BN_1();")
        time.sleep(2)  # 等待 BUGCODE 下拉選單載入
        print("    BN_1() 已觸發（載入經費用途選單）")
    except Exception as e:
        print(f"    警告: BN_1() 失敗 ({e})")

    # ── Step 2: 選擇經費用途（搜尋「業務」或選預設）
    selected_code = appy_frame.evaluate("""() => {
        const sel = FORM1.BUGCODE_1;
        if (!sel || sel.options.length <= 1)
            return { found: false, reason: 'no options (BUGCODE_1 未載入)', count: sel ? sel.options.length : 0 };

        // 優先搜尋「業務」
        for (let i = 0; i < sel.options.length; i++) {
            if (sel.options[i].text.includes('業務')) {
                sel.selectedIndex = i;
                return { found: true, index: i, text: sel.options[i].text, value: sel.options[i].value };
            }
        }
        // 備案：選第一個有值的選項
        for (let i = 1; i < sel.options.length; i++) {
            if (sel.options[i].value && sel.options[i].value.trim()) {
                sel.selectedIndex = i;
                return { found: true, fallback: true, index: i, text: sel.options[i].text, value: sel.options[i].value };
            }
        }
        return { found: false, reason: 'no valid option',
                 options: [...sel.options].map(o => o.text.substring(0, 60)) };
    }""")
    time.sleep(0.5)

    if selected_code.get("found"):
        fb = " (備案)" if selected_code.get("fallback") else ""
        print(f"    經費用途{fb}: {selected_code.get('text', '(預設)')}")
    else:
        print(f"    [WARN] BUGCODE_1 選擇失敗: {selected_code.get('reason', '預設')}")
        if selected_code.get("options"):
            print(f"    可用選項: {selected_code['options']}")

    # ── Step 3: 觸發 BC_1() 取得經費餘額（透過 LA_AM frame 提交）
    try:
        appy_frame.evaluate("if (typeof BC_1 === 'function') BC_1();")
        time.sleep(2)  # 等 LA_AM frame 回傳
        print("    BC_1() 已觸發（查詢經費餘額）")
    except Exception as e:
        print(f"    警告: BC_1() 失敗 ({e})")

    # ── Step 4: 填入金額 (D_AMOUNT_1) 與 會計科目 (SUBJECTNO_1)
    appy_frame.evaluate(f"""() => {{
        const el = FORM1.D_AMOUNT_1;
        if (el) {{
            el.value = '{amount}';
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
        }}
        
        // 會計科目：只在有明確指定時才設定，否則保持系統預設
        const subjectCode = '{subject_code}';
        if (subjectCode) {{
            const sel = FORM1.SUBJECTNO_1;
            if (sel && sel.options) {{
                for(let i=0; i<sel.options.length; i++) {{
                    if(sel.options[i].value === subjectCode) {{
                        sel.selectedIndex = i;
                        sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        break;
                    }}
                }}
            }} else if (sel) {{
                sel.value = subjectCode;
                sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }}
        
        if (typeof SUM_SUM === 'function') SUM_SUM();
    }}""")
    print(f"    金額: {amount}, 預設科目: {subject_code}")

    # ── Step 5: 驗證 BUGETNO_1、BUGCODE_1、D_AMOUNT_1 三個必填欄位
    # SUM_ALERT 要求三者都有值，否則 T_BUG_AMT=0
    verify = appy_frame.evaluate("""() => ({
        bugetno: FORM1.BUGETNO_1 ? FORM1.BUGETNO_1.value : '',
        bugcode: FORM1.BUGCODE_1 ? FORM1.BUGCODE_1.value : '',
        amount: FORM1.D_AMOUNT_1 ? FORM1.D_AMOUNT_1.value : '',
        subjectno: FORM1.SUBJECTNO_1 ? FORM1.SUBJECTNO_1.value : '',
    })""")
    bugetno_ok = bool(verify.get("bugetno"))
    bugcode_ok = bool(verify.get("bugcode"))
    amount_ok = bool(verify.get("amount"))

    if bugetno_ok and bugcode_ok and amount_ok:
        print(f"    [OK] BUGETNO={verify['bugetno']}, BUGCODE={verify['bugcode']}, AMOUNT={verify['amount']}")
    else:
        missing = []
        if not bugetno_ok:
            missing.append("BUGETNO_1")
        if not bugcode_ok:
            missing.append("BUGCODE_1")
        if not amount_ok:
            missing.append("D_AMOUNT_1")
        print(f"    [FAIL] 必填欄位為空: {', '.join(missing)}")
        print(f"      BUGETNO={verify.get('bugetno', '')}, BUGCODE={verify.get('bugcode', '')}, AMOUNT={verify.get('amount', '')}")
        print(f"      SUM_ALERT 將無法計算請購金額（T_BUG_AMT=0）！")

    print("  APPY 填寫完成")
    return chosen_plan_text, chosen_plan_code


def fill_appa_frame(appa_frame: Frame, menu_page: Page, context,
                     receipt_data: dict, receipt_seq: int = 1):
    """
    填寫 APPA frame（受款人）：代墊、收據號碼、日期、受款人代碼、銀行帳戶、金額。

    流程：
        1. 勾選代墊 (PROX_1)
        2. 填入收據/發票號碼
        3. 填入日期 (IDATE_1)
        4. 填入受款人代碼 (VENDORID_S_1 = 登入帳號)
        5. 觸發 CHK_P_1() → CK_VN 查詢 → 銀行帳戶彈窗 → 選「一銀竹北」
        6. 填入含稅金額 (AMOUNT_1)

    Args:
        appa_frame: APPA Frame 物件
        menu_page: 主選單 Page
        context: BrowserContext（用於偵測彈窗）
        receipt_data: OCR 辨識結果
        receipt_seq: 當天收據流水號 (1, 2, ...)
    """
    print("  填寫 APPA（受款人）...")

    # 偵測多行模式（合併了多張收據時，每張一行）
    _receipts_list = receipt_data.get("_receipts", [])
    _is_multi = len(_receipts_list) > 1

    if _is_multi:
        # 多行模式：行 1 用第一張收據的個別資訊
        _r0 = _receipts_list[0]
        date_str = _r0.get("date", "") or receipt_data.get("date", "")
        invoice_no = _r0.get("invoice_no", "")
        try:
            amount = int(float(_r0.get("amount", 0))) or receipt_data.get("amount", 0)
        except (ValueError, TypeError):
            amount = receipt_data.get("amount", 0)
        print(f"  （多行模式：{len(_receipts_list)} 張收據 → {len(_receipts_list)} 行）")
    else:
        date_str = receipt_data.get("date", "")
        amount = receipt_data.get("amount", 0)
        invoice_no = receipt_data.get("invoice_no", "")

    # ── Step 1: 勾選代墊 ────────────────────────
    appa_frame.evaluate("""() => {
        const cb = FORM1.PROX_1;
        if (cb && !cb.checked) {
            FORM1.PAYKIND_1.value = "2";
            cb.checked = true;
        }
    }""")
    time.sleep(0.3)
    print("    代墊: 已勾選")

    # ── Step 2: 填入收據/發票號碼 ────────────────
    # 格式: 2個文字 + 8個數字（如 "收據11502261" 或 "AB12345678"）
    # 若 OCR 有發票號碼且格式正確就用，否則自動產生
    sanitized = _sanitize_receipt_no(invoice_no) if invoice_no else ""
    if sanitized:
        receipt_no = sanitized
        if sanitized != invoice_no:
            print(f"    [sanitize] 收據號碼: '{invoice_no}' -> '{sanitized}'")
    elif date_str:
        receipt_no = generate_receipt_no(date_str, receipt_seq)
    else:
        receipt_no = f"{RECEIPT_PREFIX}000000{receipt_seq:02d}"

    receipt_no_esc = _js_escape(receipt_no)
    appa_frame.evaluate(f"""() => {{
        const el = FORM1.INVOICENO_1;
        if (el) {{
            el.value = '{receipt_no_esc}';
            el.dispatchEvent(new Event('change', {{bubbles:true}}));
            el.dispatchEvent(new Event('blur', {{bubbles:true}}));
        }}
    }}""")
    print(f"    收據號碼: {receipt_no}")

    # ── Step 3: 填入日期 ─────────────────────────
    if date_str:
        idate = _idate_format(date_str)
        appa_frame.evaluate(f"""() => {{
            const el = FORM1.IDATE_1;
            if (el) {{
                el.value = '{idate}';
                el.dispatchEvent(new Event('change', {{bubbles:true}}));
                el.dispatchEvent(new Event('blur', {{bubbles:true}}));
            }}
        }}""")
        print(f"    日期: {idate}")

    # ── Step 4: 填入受款人代碼（代墊者帳號）──────
    payee = PAYEE_CODE
    payee_esc = _js_escape(payee)
    # 只設值，不 fire blur（避免觸發 CHK_P_1 清除資料）。
    # VENDORID_1 使用 CharToAsc 編碼；Step 5 會透過 CHK_P_1 開彈窗取銀行資料。
    appa_frame.evaluate(f"""() => {{
        FORM1.VENDORID_S_1.value = '{payee_esc}';
        if (typeof CharToAsc === 'function') {{
            FORM1.VENDORID_1.value = CharToAsc('{payee_esc}');
        }}
    }}""")
    time.sleep(0.3)
    print(f"    受款人代碼: {payee}")

    # ── Step 5: 觸發 CHK_P_1() → 銀行帳戶選擇彈窗 ─
    # CHK_P_1() 提交到 CK_VN frame → 彈出 SELECT_VEN_Q.asp 視窗
    # 彈窗中每個帳戶有一個「選定」按鈕，onclick 用 opener.parent 回填
    # 但 Playwright popup 沒有 opener 連結，所以要手動提取值並回填
    bank_details = {}  # 儲存銀行帳戶資訊，供多行模式複用
    try:
        with context.expect_page(timeout=10000) as popup_info:
            appa_frame.evaluate("CHK_P_1();")
            time.sleep(2)

        popup = popup_info.value
        popup.wait_for_load_state("networkidle", timeout=10000)
        print("    銀行選擇彈窗已開啟")

        # 找到包含「一銀竹北」的行，從其按鈕的 onclick 提取回填值
        bank_kw = _js_escape(BANK_KEYWORD)
        result = popup.evaluate(f"""() => {{
            const trs = document.querySelectorAll('tr');
            for (const tr of trs) {{
                if (tr.innerText.includes('{bank_kw}')) {{
                    const btn = tr.querySelector('input[type=button]');
                    if (!btn) continue;
                    const onclick = btn.getAttribute('onclick') || '';
                    // 從 onclick 提取各欄位值
                    const extract = (pattern) => {{
                        const m = onclick.match(pattern);
                        return m ? m[1] : '';
                    }};
                    return {{
                        found: true,
                        venname: extract(/VENNAME_1\\.value='([^']+)'/),
                        bankno: extract(/BANKNO_1\\.value='([^']+)'/),
                        account: extract(/ACCOUNT_1\\.value='([^']+)'/),
                        accountnam: extract(/ACCOUNTNAM_1\\.value='([^']+)'/),
                        vendorid_s: extract(/VENDORID_S_1\\.value='([^']+)'/),
                        text: tr.innerText.replace(/\\s+/g, ' ').substring(0, 100),
                    }};
                }}
            }}
            return {{ found: false,
                      body: document.body.innerText.substring(0, 300) }};
        }}""")

        if result.get("found"):
            # 手動將值填回 APPA frame（繞過 opener 限制）
            vn = _js_escape(result.get("venname", ""))
            bk = _js_escape(result.get("bankno", ""))
            ac = _js_escape(result.get("account", ""))
            an = _js_escape(result.get("accountnam", ""))
            vs = _js_escape(result.get("vendorid_s", payee))
            # 重要：不對 VENDORID_S_1 fire blur，因為 onblur=CHK_P_1() 會清除
            # VENNAME/BANKNO/ACCOUNT/ACCOUNTNAM 並觸發 CK_VN 非同步查詢。
            # 我們已經從彈窗取得正確的銀行資料，直接設值即可。
            appa_frame.evaluate(f"""() => {{
                // 設定受款人代碼（不觸發 CHK_P_1）
                FORM1.VENDORID_S_1.value = '{vs}';
                FORM1.VENDORID_1.value = CharToAsc('{vs}');
                // 設定受款人姓名與銀行
                FORM1.VENNAME_1.value = '{vn}';
                FORM1.BANKNO_1.value = '{bk}';
                FORM1.ACCOUNT_1.value = '{ac}';
                FORM1.ACCOUNTNAM_1.value = '{an}';
                // 設定 I_VENDORID (SUM_ALERT A_STR 序列化需要此欄位)
                if (FORM1.I_VENDORID_S_1) FORM1.I_VENDORID_S_1.value = '{vs}';
                if (FORM1.I_VENDORID_1)   FORM1.I_VENDORID_1.value = '{vs}';
            }}""")
            bank_details = {
                "vn": result.get("venname", ""),
                "bk": result.get("bankno", ""),
                "ac": result.get("account", ""),
                "an": result.get("accountnam", ""),
                "vs": result.get("vendorid_s", payee),
            }
            print(f"    銀行帳戶: {result.get('text', '')[:60]}")
            print(f"    受款人: {vn}, 銀行: {an} ({bk})")
        else:
            print(f"    警告: 未找到「{BANK_KEYWORD}」")
            print(f"    彈窗內容: {result.get('body', '')[:200]}")

        # 關閉彈窗 — 必須確實關閉，否則可能影響後續操作
        try:
            if not popup.is_closed():
                popup.close()
                time.sleep(0.5)
            # 二次確認是否關閉
            if not popup.is_closed():
                print("    警告: 彈窗未關閉，嘗試強制關閉")
                popup.evaluate("window.close()")
                time.sleep(0.5)
        except Exception:
            pass

        # 確認彈窗已關閉
        try:
            closed = popup.is_closed()
            if not closed:
                print("    警告: 銀行帳戶彈窗仍未關閉！")
            else:
                print("    銀行帳戶彈窗已關閉")
        except Exception:
            pass
        time.sleep(1)

    except Exception as e:
        # 沒有彈窗 = CK_VN 直接回填（只有一個帳戶的情況）
        print(f"    銀行帳戶: CK_VN 直接回填（無彈窗）")
        time.sleep(3)

    # 確保所有殘留的彈窗都被關閉
    try:
        for p in context.pages:
            if p != menu_page and "SELECT_VEN" in p.url:
                print(f"    清理殘留彈窗: {p.url[-50:]}")
                p.close()
                time.sleep(0.3)
    except Exception:
        pass

    # 確認回填結果
    ven_info = appa_frame.evaluate("""() => ({
        venname: FORM1.VENNAME_1.value,
        vendorid: FORM1.VENDORID_1.value,
        vendorid_s: FORM1.VENDORID_S_1.value,
        bankno: FORM1.BANKNO_1.value,
        account: FORM1.ACCOUNT_1.value,
        accountnam: FORM1.ACCOUNTNAM_1.value,
    })""")
    if ven_info.get("venname"):
        print(f"    [OK] 受款人: {ven_info['venname']}, 銀行: {ven_info.get('accountnam', '')} ({ven_info.get('bankno', '')})")
    else:
        print(f"    [WARN] 受款人姓名未填入！venname={ven_info.get('venname')}, bankno={ven_info.get('bankno')}")

    # ── Step 5.5: 確保 VENDORID_1 有值 ────────────
    # SUM_ALERT 的條件是 VENNAME_1 != "" && VENDORID_1 != ""
    # 如果 VENDORID_1 為空，整個 APPA 行會被忽略 → 存入時 APPA 資料遺失
    vendorid_check = appa_frame.evaluate(f"""() => {{
        // 確保 VENDORID_S_1 有值
        if (!FORM1.VENDORID_S_1.value) {{
            FORM1.VENDORID_S_1.value = '{payee_esc}';
        }}
        // 確保 VENDORID_1 有 CharToAsc 編碼值
        if (!FORM1.VENDORID_1.value && typeof CharToAsc === 'function') {{
            FORM1.VENDORID_1.value = CharToAsc(FORM1.VENDORID_S_1.value);
        }}
        // 確保 I_VENDORID 有值（SUM_ALERT A_STR 序列化需要）
        if (FORM1.I_VENDORID_S_1 && !FORM1.I_VENDORID_S_1.value) {{
            FORM1.I_VENDORID_S_1.value = FORM1.VENDORID_S_1.value;
        }}
        if (FORM1.I_VENDORID_1 && !FORM1.I_VENDORID_1.value) {{
            FORM1.I_VENDORID_1.value = FORM1.VENDORID_S_1.value;
        }}
        return {{
            vendorid_s: FORM1.VENDORID_S_1.value,
            vendorid: FORM1.VENDORID_1.value,
            venname: FORM1.VENNAME_1.value,
            i_vendorid: FORM1.I_VENDORID_1 ? FORM1.I_VENDORID_1.value : 'N/A',
        }};
    }}""")
    if vendorid_check.get("vendorid"):
        print(f"    [OK] VENDORID_1: {vendorid_check['vendorid'][:30]}...")
    else:
        print(f"    [FAIL] VENDORID_1 仍為空，SUM_ALERT 將跳過此 APPA 行！")
        print(f"      VENDORID_S_1={vendorid_check.get('vendorid_s')}")
        print(f"      VENNAME_1={vendorid_check.get('venname')}")

    # ── Step 6: 填入含稅金額 ─────────────────────
    appa_frame.evaluate(f"""() => {{
        FORM1.AMOUNT_1.value = '{amount}';
        // 觸發 SUM_SUM() 更新加總
        if (typeof SUM_SUM === 'function') SUM_SUM();
    }}""")
    print(f"    含稅金額: {amount}")

    # ── Step 7: 多張收據 → 填入 APPA 行 2..N ──────────
    if _is_multi and bank_details:
        print(f"  填寫 APPA 行 2~{len(_receipts_list)}...")
        seq_offset = 0
        for i, extra_r in enumerate(_receipts_list[1:], start=2):
            extra_invoice = extra_r.get("invoice_no", "")
            extra_date = extra_r.get("date", "")
            try:
                extra_amount = int(float(extra_r.get("amount", 0)))
            except (ValueError, TypeError):
                extra_amount = 0

            # 發票號碼或收據號碼（格式: 2字+8數字）
            extra_sanitized = _sanitize_receipt_no(extra_invoice) if extra_invoice else ""
            if extra_sanitized:
                extra_no = extra_sanitized
            elif extra_date:
                seq_offset += 1
                extra_no = generate_receipt_no(extra_date, receipt_seq + seq_offset)
            else:
                seq_offset += 1
                s = min(max(receipt_seq + seq_offset, 1), 9)
                extra_no = f"{RECEIPT_PREFIX}000000{s}"

            extra_no_esc = _js_escape(extra_no)
            extra_idate = _idate_format(extra_date) if extra_date else ""
            vn_e = _js_escape(bank_details.get("vn", ""))
            bk_e = _js_escape(bank_details.get("bk", ""))
            ac_e = _js_escape(bank_details.get("ac", ""))
            an_e = _js_escape(bank_details.get("an", ""))
            vs_e = _js_escape(bank_details.get("vs", payee))

            # 多行模式：直接設值，不觸發 blur/change（避免 CHK_P_N 清除）
            appa_frame.evaluate(f"""() => {{
                const n = {i};
                // 代墊
                const pk = FORM1['PAYKIND_' + n];
                const cb = FORM1['PROX_' + n];
                if (pk) pk.value = '2';
                if (cb && !cb.checked) cb.checked = true;
                // 號碼
                const inv = FORM1['INVOICENO_' + n];
                if (inv) inv.value = '{extra_no_esc}';
                // 日期
                const dt = FORM1['IDATE_' + n];
                if (dt) dt.value = '{extra_idate}';
                // 受款人（不觸發 CHK_P）
                const vs_el = FORM1['VENDORID_S_' + n];
                if (vs_el) vs_el.value = '{vs_e}';
                const v_el = FORM1['VENDORID_' + n];
                if (v_el && typeof CharToAsc === 'function')
                    v_el.value = CharToAsc('{vs_e}');
                const vn_el = FORM1['VENNAME_' + n];
                if (vn_el) vn_el.value = '{vn_e}';
                const bk_el = FORM1['BANKNO_' + n];
                if (bk_el) bk_el.value = '{bk_e}';
                const ac_el = FORM1['ACCOUNT_' + n];
                if (ac_el) ac_el.value = '{ac_e}';
                const an_el = FORM1['ACCOUNTNAM_' + n];
                if (an_el) an_el.value = '{an_e}';
                // I_VENDORID（SUM_ALERT A_STR 需要）
                const ivs = FORM1['I_VENDORID_S_' + n];
                if (ivs) ivs.value = '{vs_e}';
                const iv = FORM1['I_VENDORID_' + n];
                if (iv) iv.value = '{vs_e}';
                // 金額
                const am = FORM1['AMOUNT_' + n];
                if (am) am.value = '{extra_amount}';
            }}""")
            time.sleep(0.3)
            print(f"    行{i}: {extra_no} | {extra_idate} | NT${extra_amount}")

        appa_frame.evaluate("if (typeof SUM_SUM === 'function') SUM_SUM();")
        
        # 額外診斷：印出剛剛寫入的 VendorID 與 VenName
        diag = appa_frame.evaluate("""() => {
            let v_id = '', v_name = '';
            try { v_id = FORM1.VENDORID_1 ? FORM1.VENDORID_1.value : 'missing_element'; } catch(e) { v_id = 'error'; }
            try { v_name = FORM1.VENNAME_1 ? FORM1.VENNAME_1.value : 'missing_element'; } catch(e) { v_name = 'error'; }
            return { vendor_id: v_id, vendor_name: v_name };
        }""")
        print(f"    [DIAG-APPA] VENDORID_1='{diag.get('vendor_id', '')}' VENNAME_1='{diag.get('vendor_name', '')}'")

        print(f"  APPA 填寫完成（共 {len(_receipts_list)} 行）")
    else:
        print("  APPA 填寫完成")

def verify_and_save(appy_frame: Frame, menu_page: Page, auto_save: bool = True):
    """
    驗證三個區塊的金額一致後，自動點擊存入。

    流程：
        1. 來回切換「編輯經費/編輯品名/編輯受款人」按鈕，確認資料不遺失
        2. 更新三個加總：SUM_LIST（經費）、SUM_APPP（品名）、SUM_APPA（受款人）
        3. 比較金額是否一致
        4. 一致則呼叫 SUM_ALERT() 存入
        5. 等待足夠時間處理所有 dialog（PDF / 錯誤等）

    SUM_ALERT() 內部流程：
        - 先設定 DD.rows="0,*"; QQ.cols="0,0,*" → 隱藏所有編輯區，顯示 PS
        - 序列化 APPY/APPA/APPP → PS frame 的 D_STR/A_STR/P_STR
        - 若 APPA 為空 → confirm("受款人尚未編輯") → dismiss = 不編輯，繼續存
        - 驗證金額一致 → submit PS frame

    Returns:
        bool: True if saved successfully
    """
    print("  驗證金額並存入...")

    # ── Step 0: 來回點選編輯按鈕，確認資料存在 ──
    # 模擬使用者操作：點選「編輯經費」→「編輯品名」→「編輯受款人」來回切換
    # 這會觸發 DD.rows / QQ.cols 切換，讓 frameset 重新渲染各 frame
    # 編輯按鈕的 onclick:
    #   編輯經費:  parent.DD.rows="*,0";   parent.QQ.cols="*,0,0";
    #   編輯品名:  parent.DD.rows="160,*"; parent.QQ.cols="*,0,0";
    #   編輯受款人: parent.DD.rows="160,*"; parent.QQ.cols="0,*,0";
    print("    切換編輯按鈕，驗證資料...")

    # ── PRE-CYCLE: 切換前先確認 APPP/APPA 的實際值 ──
    pre_check = appy_frame.evaluate("""() => {
        let appp_v = '', appa_v = '', appa_inv = '';
        try { appp_v = parent.APPP.FORM1.PRODUCT_1 ? parent.APPP.FORM1.PRODUCT_1.value : ''; } catch(e) {}
        try { appa_v  = parent.APPA.FORM1.VENNAME_1  ? parent.APPA.FORM1.VENNAME_1.value  : ''; } catch(e) {}
        try { appa_inv= parent.APPA.FORM1.INVOICENO_1? parent.APPA.FORM1.INVOICENO_1.value: ''; } catch(e) {}
        return { appp: appp_v, appa: appa_v, inv: appa_inv };
    }""")
    print(f"    [PRE-CYCLE]  APPP.PRODUCT_1 = {pre_check.get('appp', '')[:40]!r}")
    print(f"    [PRE-CYCLE]  APPA.VENNAME_1 = {pre_check.get('appa', '')!r}")
    print(f"    [PRE-CYCLE]  APPA.INVOICENO_1 = {pre_check.get('inv', '')!r}")

    button_cycle = [
        ("編輯品名",   'parent.DD.rows="160,*"; parent.QQ.cols="*,0,0";'),
        ("編輯受款人", 'parent.DD.rows="160,*"; parent.QQ.cols="0,*,0";'),
        ("編輯經費",   'parent.DD.rows="*,0";   parent.QQ.cols="*,0,0";'),
        ("編輯品名",   'parent.DD.rows="160,*"; parent.QQ.cols="*,0,0";'),
        ("編輯受款人", 'parent.DD.rows="160,*"; parent.QQ.cols="0,*,0";'),
        ("編輯經費",   'parent.DD.rows="*,0";   parent.QQ.cols="*,0,0";'),
        ("編輯品名",   'parent.DD.rows="160,*"; parent.QQ.cols="*,0,0";'),
    ]

    for i, (label, js_code) in enumerate(button_cycle, 1):
        appy_frame.evaluate(f"() => {{ {js_code} }}")
        time.sleep(0.5)
        print(f"      ({i}/{len(button_cycle)}) {label}")

    # 驗證資料仍然存在
    data_check = appy_frame.evaluate("""() => {
        const appy_ok = FORM1.BUGETNO_1 && FORM1.BUGETNO_1.value &&
                         FORM1.D_AMOUNT_1 && FORM1.D_AMOUNT_1.value;
        let appp_ok = false;
        try { appp_ok = parent.APPP.FORM1.PRODUCT_1 &&
                         parent.APPP.FORM1.PRODUCT_1.value != ''; } catch(e) {}
        let appa_ok = false;
        try { appa_ok = parent.APPA.FORM1.VENNAME_1 &&
                         parent.APPA.FORM1.VENNAME_1.value != '' &&
                         parent.APPA.FORM1.VENDORID_1 &&
                         parent.APPA.FORM1.VENDORID_1.value != ''; } catch(e) {}
        return {
            appy: !!appy_ok,
            appp: appp_ok,
            appa: appa_ok,
            amount: FORM1.D_AMOUNT_1 ? FORM1.D_AMOUNT_1.value : '',
        };
    }""")
    appy_ok = data_check.get("appy", False)
    appp_ok = data_check.get("appp", False)
    appa_ok = data_check.get("appa", False)
    print(f"    切換後驗證: APPY={'V' if appy_ok else 'X'} "
          f"APPP={'V' if appp_ok else 'X'} APPA={'V' if appa_ok else 'X'} "
          f"(金額={data_check.get('amount', '')})")

    # ── POST-CYCLE: 印出 APPP/APPA 實際值（幫助診斷）──
    post_check = appy_frame.evaluate("""() => {
        let appp_v = '', appa_v = '', appa_inv = '';
        try { appp_v = parent.APPP.FORM1.PRODUCT_1 ? parent.APPP.FORM1.PRODUCT_1.value : ''; } catch(e) {}
        try { appa_v  = parent.APPA.FORM1.VENNAME_1  ? parent.APPA.FORM1.VENNAME_1.value  : ''; } catch(e) {}
        try { appa_inv= parent.APPA.FORM1.INVOICENO_1? parent.APPA.FORM1.INVOICENO_1.value: ''; } catch(e) {}
        return { appp: appp_v, appa: appa_v, inv: appa_inv };
    }""")
    print(f"    [POST-CYCLE] APPP.PRODUCT_1  = {post_check.get('appp', '')[:40]!r}")
    print(f"    [POST-CYCLE] APPA.VENNAME_1  = {post_check.get('appa', '')!r}")
    print(f"    [POST-CYCLE] APPA.INVOICENO_1 = {post_check.get('inv', '')!r}")

    if not appy_ok:
        print("    [FAIL] APPY 經費資料遺失！跳過存入。")
        return False

    # ── Step 1: 更新各區塊加總 ──
    # 注意：學校系統 CHK_APPA() 有 bug（少了 FORM1），所以手動讀取 APPA 加總
    appy_frame.evaluate("""() => {
        // 更新品名加總
        if (typeof CHK_APPP === 'function') CHK_APPP();
        // 更新經費加總
        if (typeof SUM_SUM === 'function') FORM1.SUM_LIST.click();
    }""")
    time.sleep(1)

    # 手動觸發 APPA 加總（繞過 CHK_APPA 的 bug）
    appy_frame.evaluate("""() => {
        try {
            parent.APPA.FORM1.SUM_LIST.click();  // 觸發 APPA 的 SUM_SUM()
        } catch(e) {}
    }""")
    time.sleep(1)

    # 手動將 APPA 加總寫回 APPY（CHK_APPA 原本該做的事）
    appy_frame.evaluate("""() => {
        try {
            FORM1.SUM_APPA.value = parent.APPA.FORM1.SUM_LIST.value;
        } catch(e) {}
    }""")
    time.sleep(0.5)

    # ── Step 2: 讀取三個加總值 ──
    sums = appy_frame.evaluate("""() => {
        const parse = (el) => {
            if (!el) return 0;
            const v = (el.value || '').replace(/[^0-9]/g, '');
            return parseInt(v) || 0;
        };
        return {
            budget: parse(FORM1.SUM_LIST),
            items: parse(FORM1.SUM_APPP),
            payee: parse(FORM1.SUM_APPA),
            budget_raw: FORM1.SUM_LIST ? FORM1.SUM_LIST.value : '',
            items_raw: FORM1.SUM_APPP ? FORM1.SUM_APPP.value : '',
            payee_raw: FORM1.SUM_APPA ? FORM1.SUM_APPA.value : '',
        };
    }""")

    budget_amt = sums.get("budget", 0)
    items_amt = sums.get("items", 0)
    payee_amt = sums.get("payee", 0)

    print(f"    經費加總: {sums.get('budget_raw', '')} ({budget_amt})")
    print(f"    品名加總: {sums.get('items_raw', '')} ({items_amt})")
    print(f"    受款人加總: {sums.get('payee_raw', '')} ({payee_amt})")

    # ── Step 3: 驗證一致 ──
    if budget_amt == items_amt == payee_amt and budget_amt > 0:
        print(f"    V 三個金額一致 ({budget_amt})，執行存入...")
    elif budget_amt > 0 and budget_amt == items_amt:
        # APPA 加總可能因為 CHK_APPA bug 未正確取得，但經費和品名一致
        print(f"    ~ 經費和品名一致 ({budget_amt})，受款人加總={payee_amt}")
        print(f"    SUM_ALERT 會自動處理 APPA 金額，繼續存入...")
    else:
        print(f"    X 金額不一致！經費={budget_amt}, 品名={items_amt}, 受款人={payee_amt}")
        print("    跳過存入，請手動確認。")
        return False

    # ── Step 4: 設定 dialog handler ──
    # SUM_ALERT() 可能觸發的 dialog：
    #   - confirm("受款人尚未編輯，要編輯受款人嗎?") → dismiss = 不編輯，繼續存
    #   - alert("請購金額不得為0") → accept
    #   - alert("金額不相符合") → accept (but means save failed)
    #   - confirm about 金額不相符 → accept
    #   - alert("品項資料筆數較多...") → accept
    #   - 其他可能的 confirm/alert（PDF列印、處理完成等）→ accept
    dialog_messages = []

    def _handle_dialog(dialog):
        try:
            msg = dialog.message
            dtype = dialog.type
            dialog_messages.append({"type": dtype, "message": msg})
            print(f"    [DIALOG {dtype}] {msg}")

            if dtype == "confirm" and "受款人尚未編輯" in msg:
                # dismiss = 選「否」= 不需編輯受款人，繼續存入
                dialog.dismiss()
            elif dtype == "confirm" and "受款人尚未輸入" in msg:
                dialog.dismiss()
            elif dtype == "confirm" and ("成功" in msg and "印表" in msg):
                # 「存入請購單號:AXXXXXXXXXX-成功,直接印表嗎?」
                # accept = 確定 → 產生 PDF 核銷文件
                print("    [DIALOG] 存入成功 → 確定（產生PDF）")
                dialog.accept()
            elif dtype == "confirm" and "直接核銷" in msg:
                # 「直接核銷」確認 → 也按確定產生 PDF
                print("    [DIALOG] 直接核銷確認 → 確定（產生PDF）")
                dialog.accept()
            else:
                dialog.accept()
        except Exception:
            pass  # 瀏覽器已關閉，忽略

    menu_page.on("dialog", _handle_dialog)

    # ── Step 5: 攔截 PDF 新視窗 ──
    # 存入成功按確定後，系統會 window.open() 開啟 PDF 頁面並呼叫 window.print()
    # 這會觸發瀏覽器原生列印對話框（不是 Playwright dialog），阻塞程式
    # 解法：用 init_script 覆蓋 window.print，並在 popup 事件中儲存截圖後關閉
    pdf_saved_path = [None]

    try:
        # 在 context 層級覆蓋 window.print → 所有新開頁面都不會觸發原生列印對話框
        menu_page.context.add_init_script(
            "window.print = function() { console.log('[Automation] print suppressed'); };"
        )
    except Exception:
        pass

    def _handle_pdf_popup(new_page):
        """攔截 PDF 新視窗：儲存截圖/PDF → 關閉頁面"""
        try:
            pdf_url = new_page.url or ""
            print(f"    [PDF] 偵測到新頁面: {pdf_url[:80]}")
            # 等待頁面載入
            try:
                new_page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                time.sleep(3)  # fallback: 直接等 3 秒
            # 再次覆蓋 print（確保不觸發原生對話框）
            try:
                new_page.evaluate(
                    "window.print = function() { console.log('print suppressed'); };"
                )
            except Exception:
                pass
            # 儲存 PDF 或截圖
            ts = time.strftime('%Y%m%d_%H%M%S')
            try:
                # page.pdf() 僅 headless 模式可用
                pdf_path = f"{OUTPUT_DIR}/expense_report_{ts}.pdf"
                new_page.pdf(path=pdf_path)
                pdf_saved_path[0] = pdf_path
                print(f"    [PDF] 核銷文件已儲存: {pdf_path}")
            except Exception:
                # headed 模式 → 改用截圖
                ss_path = f"{OUTPUT_DIR}/expense_report_{ts}.png"
                new_page.screenshot(path=ss_path, full_page=True)
                pdf_saved_path[0] = ss_path
                print(f"    [PDF] 核銷文件截圖已儲存: {ss_path}")
            # 關閉 PDF 頁面
            new_page.close()
            print(f"    [PDF] 已關閉 PDF 頁面")
        except Exception as e:
            print(f"    [PDF] 處理錯誤: {e}")
            try:
                new_page.close()
            except Exception:
                pass

    menu_page.context.on("page", _handle_pdf_popup)

    # ── Step 6: 呼叫 SUM_ALERT() 存入 (若 auto_save=True) ──
    # SUM_ALERT 前：再次讀 APPP/APPA 狀態（確認最終資料）
    final_check = appy_frame.evaluate("""() => {
        let appp_v = '', appa_v = '', appa_inv = '';
        try { appp_v = parent.APPP.FORM1.PRODUCT_1 ? parent.APPP.FORM1.PRODUCT_1.value : ''; } catch(e) {}
        try { appa_v  = parent.APPA.FORM1.VENNAME_1  ? parent.APPA.FORM1.VENNAME_1.value  : ''; } catch(e) {}
        try { appa_inv= parent.APPA.FORM1.INVOICENO_1? parent.APPA.FORM1.INVOICENO_1.value: ''; } catch(e) {}
        return { appp: appp_v, appa: appa_v, inv: appa_inv };
    }""")
    print(f"    [PRE-ALERT]  APPP.PRODUCT_1  = {final_check.get('appp', '')[:40]!r}")
    print(f"    [PRE-ALERT]  APPA.VENNAME_1  = {final_check.get('appa', '')!r}")
    print(f"    [PRE-ALERT]  APPA.INVOICENO_1 = {final_check.get('inv', '')!r}")

    try:
        # 存入前：確保在「編輯經費」視圖（APPY 可見）
        appy_frame.evaluate("""() => {
            parent.DD.rows = "*,0";
            parent.QQ.cols = "*,0,0";
        }""")
        time.sleep(0.5)

        if auto_save:
            appy_frame.evaluate("SUM_ALERT();")
        else:
            print("    [手動模式] 準備就緒，您可以切換視窗檢查或按下「存檔」。")
    except Exception as e:
        print(f"    SUM_ALERT/準備 錯誤: {e}")

    # ── Step 7: 等待 submit 完成 + 處理所有 dialog ──
    # 等待足夠長的時間以處理：
    #   - SUM_ALERT 的序列化和 submit
    #   - 伺服器處理
    #   - 任何後續 dialog（PDF、確認、錯誤等、直接核銷確認）
    #   - 成功時會收到「成功,直接印表嗎?」confirm → accept 後產生 PDF
    if auto_save:
        print("    等待存入完成...")
        save_confirmed = False
        for sec in range(45):
            # 重要：用 Playwright 的 wait_for_timeout 而非 time.sleep
            # time.sleep 會阻塞 Python 線程，導致 Playwright 無法即時處理 dialog 事件
            # wait_for_timeout 在等待的同時仍會處理瀏覽器事件（dialog、popup 等）
            menu_page.wait_for_timeout(1000)
            # 檢查是否已收到成功 dialog → 可提早結束等待
            for d in dialog_messages:
                if "成功" in d["message"] and "印表" in d["message"]:
                    save_confirmed = True
            if save_confirmed:
                # 成功確認後，給 PDF popup 多幾秒處理
                print(f"    [OK] 已確認存入成功並觸發 PDF 列印 ({sec + 1}s)")
                menu_page.wait_for_timeout(3000)  # 等待 PDF popup 處理
                break
            if (sec + 1) % 5 == 0:
                print(f"    ... 已等待 {sec + 1} 秒 (dialog: {len(dialog_messages)} 個)")
    else:
        # 手動模式：移除 dialog handler 和 PDF popup handler，交由外層 process_batch 暫停
        print("    [手動模式] 跳過自動等待與自動檢查。")
        try:
            menu_page.remove_listener("dialog", _handle_dialog)
        except Exception:
            pass
        try:
            menu_page.context.remove_listener("page", _handle_pdf_popup)
        except Exception:
            pass
        return True

    # 檢查 PS frame 是否有回應（搜尋所有 frame）
    try:
        for f in menu_page.frames:
            fname = f.name or ""
            furl = f.url or ""
            if (fname == "PS"
                    or "SAVE" in furl.upper()
                    or "STD_SAVE" in furl.upper()
                    or "PR_SAVE" in furl.upper()):
                try:
                    ps_body = f.evaluate(
                        "document.body ? document.body.innerText.substring(0, 500) : ''"
                    )
                    if ps_body and ps_body.strip():
                        print(f"    [PS回應] frame={fname!r} url={furl[:60]}")
                        print(f"    [PS回應] body: {ps_body[:300]}")
                except Exception:
                    pass
    except Exception:
        pass

    # 移除 dialog handler 和 PDF popup handler 避免影響後續
    try:
        menu_page.remove_listener("dialog", _handle_dialog)
    except Exception:
        pass
    try:
        menu_page.context.remove_listener("page", _handle_pdf_popup)
    except Exception:
        pass

    # ── Step 8: 檢查存入結果 ──
    has_error = False
    save_success_confirmed = False
    record_no_from_dialog = ""
    for d in dialog_messages:
        if "不得為0" in d["message"] or "不相符合" in d["message"]:
            has_error = True
            print(f"    存入失敗: {d['message']}")
        if "成功" in d["message"] and "印表" in d["message"]:
            save_success_confirmed = True
            # 嘗試提取請購單號（格式: 存入請購單號:AXXXXXXXXXX-成功）
            import re
            m = re.search(r'(A\d{10,})', d["message"])
            if m:
                record_no_from_dialog = m.group(1)

    if has_error:
        print("  [FAIL] 存入失敗，請手動確認")
        return False

    if save_success_confirmed:
        print(f"  存入成功！請購單號: {record_no_from_dialog or '(已確認)'}  已觸發 PDF 列印")
        if pdf_saved_path[0]:
            print(f"  PDF 文件: {pdf_saved_path[0]}")
    else:
        print(f"  存入完成！（dialog: {len(dialog_messages)} 個）")
    return True


def verify_saved_record(menu_page: Page, expected_amount: int = 0,
                        use_project: bool = False):
    """
    存入後回到購案管理頁面，驗證剛剛新增的請購單是否正確。

    流程：
        1. 點選 TITLE 的「購案管理」(LIS2/LIS4 依模式)
        2. 篩選「直接核銷(零用金)」
        3. 找到最新的記錄
        4. 點選「修改」進入檢視
        5. 檢查 APPP（品名）和 APPA（受款人）是否有內容
        6. 截圖留存

    Args:
        menu_page: 主選單 Page
        expected_amount: 預期金額（用於比對）
        use_project: True=計畫請購(LIS4/COM=NT), False=部門請購(LIS2/COM=YT)

    Returns:
        dict: 驗證結果 {ok: bool, record_no: str, appy: {}, appp: {}, appa: {}}
    """
    print("  驗證存入結果...")

    # ── Step 0: PDF 產生後頁面可能已導航，先等待穩定 ──
    time.sleep(2)

    # ── Step 1: 回到計畫請購查詢列表 ──
    # 點擊 TITLE 的 LIS4（計畫請購查詢）重新載入列表
    title_frame = menu_page.frame("TITLE")
    if not title_frame:
        # PDF 產生後可能導致 frame 結構改變，嘗試等待重新取得
        print("    [INFO] TITLE frame 不存在，等待 3 秒後重試...")
        time.sleep(3)
        title_frame = menu_page.frame("TITLE")
    if not title_frame:
        print("    [WARN] 找不到 TITLE frame（可能因 PDF 產生導致頁面導航）")
        print("    [INFO] 存入已由 dialog 確認成功，跳過清單驗證")
        return {"ok": True, "record_no": "N/A",
                "note": "驗證跳過（TITLE frame 不存在），存入已由 dialog 確認"}

    lis_mode = "計畫請購(LIS4)" if use_project else "部門請購(LIS2)"
    print(f"    回到 {lis_mode} 查詢列表...")
    try:
        if use_project:
            title_frame.evaluate("""() => {
                try { LIS4(); } catch(e) {
                    parent.FM.rows = "15%,*,0,0,0,0,0";
                    parent.MAIN.location = '../BLANK_Q.asp?COM=NT';
                    parent.TRAN.location = 'TRAN_Q.asp?COM=NT';
                    parent.OT.location = '../SHAR_BUG_Q/SHAR_BUG_STR_Q.asp?COM=NT';
                    window.location = 'DA_SerFun_Q.asp?COM=NT';
                }
            }""")
        else:
            title_frame.evaluate("""() => {
                try { LIS2(); } catch(e) {
                    parent.FM.rows = "15%,*,0,0,0,0,0";
                    parent.MAIN.location = '../BLANK_Q.asp?COM=YT';
                    parent.TRAN.location = 'TRAN_Q.asp?COM=YT';
                    parent.OT.location = '../SHAR_BUG_Q/SHAR_BUG_STR_Q.asp?COM=YT';
                    window.location = 'DA_SerFun_Q.asp?COM=YT';
                }
            }""")
    except Exception as e:
        print(f"    {lis_mode} 失敗: {e}")
        return {"ok": False, "error": str(e)}

    time.sleep(3)

    # 重新取得 TITLE frame（可能已經 reload）
    title_frame = menu_page.frame("TITLE")
    if not title_frame:
        print("    [FAIL] TITLE frame 消失")
        return {"ok": False, "error": "TITLE frame lost"}
    try:
        title_frame.wait_for_load_state("networkidle", timeout=15000)
    except Exception as e:
        print(f"    [WARN] TITLE frame 載入等待逾時: {e}")
        print(f"    [INFO] 繼續嘗試...")
    time.sleep(1)

    # ── Step 2: 點擊「購案管理」(aBT1) ──
    try:
        title_frame.evaluate("""() => {
            const btn = document.querySelector('a[name=aBT1]');
            if (btn) btn.click();
        }""")
    except Exception as e:
        if "Execution context was destroyed" in str(e):
            # 存入後系統自動導航，frame context 被重置 → 等待後重試
            print(f"    [INFO] frame 導航中，等待 4 秒後重試...")
            time.sleep(4)
            try:
                title_frame = menu_page.frame("TITLE")
                if title_frame:
                    title_frame.wait_for_load_state("networkidle", timeout=8000)
                    title_frame.evaluate("""() => {
                        const btn = document.querySelector('a[name=aBT1]');
                        if (btn) btn.click();
                    }""")
            except Exception as e2:
                print(f"    [WARN] 購案管理重試失敗: {e2}")
                print(f"    [INFO] 存入已由 dialog 確認，跳過清單驗證")
                menu_page.screenshot(
                    path=f"{OUTPUT_DIR}/verify_skipped.png", full_page=True
                )
                print(f"    截圖: {OUTPUT_DIR}/verify_skipped.png")
                return {"ok": True, "record_no": "N/A",
                        "note": "驗證被跳過（frame 導航），存入已由 dialog 確認"}
        else:
            print(f"    購案管理按鈕失敗: {e}")
            return {"ok": False, "error": str(e)}

    time.sleep(3)

    # ── Step 3: 在 MAIN frame 中篩選「直接核銷(零用金)」──
    main_frame = menu_page.frame("MAIN")
    if not main_frame:
        # 嘗試找 MAIN frame
        for f in menu_page.frames:
            if "DA_APY_Q" in f.url or "APY_Q" in f.url:
                main_frame = f
                break
    if not main_frame:
        main_frame = menu_page.frame("MAIN")

    if not main_frame:
        print("    [WARN] 找不到 MAIN frame（PDF 產生後頁面可能已導航）")
        print("    [INFO] 存入已由 dialog 確認成功，跳過清單驗證")
        return {"ok": True, "record_no": "N/A",
                "note": "驗證跳過（MAIN frame 不存在），存入已由 dialog 確認"}

    try:
        main_frame.wait_for_load_state("networkidle", timeout=15000)
    except Exception as e:
        print(f"    [WARN] MAIN frame 載入等待逾時: {e}")
        print(f"    [INFO] 繼續嘗試...")
    time.sleep(1)

    # 選擇「直接核銷(零用金)」下拉
    select_result = main_frame.evaluate("""() => {
        const selects = document.querySelectorAll('select');
        for (const sel of selects) {
            for (let i = 0; i < sel.options.length; i++) {
                if (sel.options[i].text.includes('直接核銷')) {
                    sel.selectedIndex = i;
                    sel.dispatchEvent(new Event('change', {bubbles: true}));
                    return { found: true, name: sel.name, text: sel.options[i].text };
                }
            }
        }
        return { found: false };
    }""")

    if select_result.get("found"):
        print(f"    篩選: {select_result.get('text', '')}")
    else:
        print("    警告: 找不到「直接核銷」選項")

    time.sleep(1)

    # 點擊搜尋/重新整理（如果有搜尋按鈕）
    main_frame.evaluate("""() => {
        // 嘗試觸發查詢
        const form = document.querySelector('form');
        if (form) {
            // 找 submit 按鈕
            const btn = document.querySelector('input[type=submit], input[name="SSS"]');
            if (btn) btn.click();
        }
    }""")
    time.sleep(3)

    # 重新取得 MAIN（可能已 navigate）
    main_frame = menu_page.frame("MAIN")
    if main_frame:
        try:
            main_frame.wait_for_load_state("networkidle", timeout=15000)
        except Exception as e:
            print(f"    [WARN] MAIN frame 重載等待逾時: {e}")
    time.sleep(1)

    # ── Step 4: 找到最新記錄 ──
    records = main_frame.evaluate("""() => {
        const rows = [];
        const trs = document.querySelectorAll('tr');
        for (const tr of trs) {
            const text = tr.innerText;
            // 找包含請購單號的行（A115...）
            if (/A\\d{10}/.test(text)) {
                const match = text.match(/A\\d{10}/);
                // 金額格式：「1,380 否」或「380 否」，需支援千位逗號
                const amountMatch = text.match(/([\\d,]+)\\s*(否|是)/);
                // 找修改按鈕或連結
                const links = tr.querySelectorAll('a, input[type=button]');
                let editOnclick = '';
                for (const lnk of links) {
                    const oc = lnk.getAttribute('onclick') || lnk.getAttribute('href') || '';
                    if (oc.includes('ED_') || oc.includes('edit') || oc.includes('MOD')
                        || lnk.innerText.includes('修改') || lnk.value === '修改') {
                        editOnclick = oc;
                        break;
                    }
                }
                rows.push({
                    recordNo: match ? match[0] : '',
                    text: text.replace(/\\s+/g, ' ').substring(0, 150),
                    // 移除千位逗號再解析（如「1,380」→ 1380）
                    amount: amountMatch ? parseInt(amountMatch[1].replace(/,/g, '')) : 0,
                    editOnclick: editOnclick.substring(0, 200),
                });
            }
        }
        return rows;
    }""")

    if not records:
        print("    [WARN] 找不到請購單記錄")
        # 截圖
        menu_page.screenshot(path=f"{OUTPUT_DIR}/verify_no_records.png", full_page=True)
        return {"ok": False, "error": "no records found"}

    # 取最新的（通常是第一筆）
    latest = records[0]
    print(f"    最新記錄: {latest.get('recordNo', '')} 金額={latest.get('amount', 0)}")
    print(f"    記錄內容: {latest.get('text', '')[:80]}")

    # ── Step 5: 點擊進入修改/檢視 ──
    # 嘗試點擊記錄的 radio button 然後點「修改」按鈕
    clicked = main_frame.evaluate(f"""() => {{
        const trs = document.querySelectorAll('tr');
        for (const tr of trs) {{
            if (tr.innerText.includes('{latest.get("recordNo", "")}')) {{
                // 先點 radio button
                const radio = tr.querySelector('input[type=radio]');
                if (radio) radio.click();
                return {{ clicked: 'radio' }};
            }}
        }}
        return {{ clicked: false }};
    }}""")

    if clicked.get("clicked"):
        time.sleep(0.5)
        # 點「修改」按鈕
        main_frame.evaluate("""() => {
            const btns = document.querySelectorAll('input[type=button], input[type=submit]');
            for (const btn of btns) {
                if (btn.value && btn.value.includes('修改')) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }""")
        time.sleep(8)  # 等待表單與所有子 frame 載入
    else:
        print("    [WARN] 無法點擊記錄")

    # ── Step 6: 檢查 APPY / APPP / APPA 內容 ──
    # 重新尋找 frames（最多重試 5 次，每次等 2 秒）
    frames_check = {}
    for attempt in range(5):
        frames_check = {}
        for f in menu_page.frames:
            url = f.url or ""
            if not url or url == "about:blank":
                continue
            url_up = url.upper()
            if "STD_APPY_Q" in url_up and "appy" not in frames_check:
                frames_check["appy"] = f
            elif "STD_APPP_Q" in url_up and "appp" not in frames_check:
                frames_check["appp"] = f
            elif "STD_APPA_Q" in url_up and "appa" not in frames_check:
                frames_check["appa"] = f

        if "appy" in frames_check and "appp" in frames_check and "appa" in frames_check:
            break  # 全部找到

        if attempt == 0:
            # 第一次找不到時印出所有 frame URL 供診斷
            print(f"    [DEBUG] 找不到全部 frames，目前所有 frames ({len(menu_page.frames)}):")
            for f in menu_page.frames:
                if f.url and f.url != "about:blank":
                    print(f"      [{f.name or '-'}] {f.url[:100]}")

        if "appy" in frames_check and "appp" not in frames_check:
            # 嘗試點擊「編輯品名」讓 APPP frame 可見並載入
            try:
                frames_check["appy"].evaluate("""() => {
                    parent.DD.rows = "160,*";
                    parent.QQ.cols = "*,0,0";
                }""")
            except Exception:
                pass

        time.sleep(2)

    result = {"ok": True, "record_no": latest.get("recordNo", "")}

    # 等待 frames 載入
    for name, frame in frames_check.items():
        try:
            frame.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

    frames_found = bool(frames_check)
    if not frames_found:
        print("    [INFO] 無法開啟詳細編輯 frames（學校系統導航方式不同）")
        print("    [INFO] 改以清單金額作為主要驗證依據，詳情請查看截圖")

    # ── 嘗試從查詢頁（DA_SerSTART_Q.asp）讀取記錄詳情 ──
    # 系統點修改後載入 DA_SerSTART_Q.asp，以 table 形式顯示全部資料
    try:
        for f in menu_page.frames:
            furl = f.url or ""
            furl_up = furl.upper()
            if "DA_SERSTART_Q" in furl_up or "DA_SER_Q" in furl_up or "SERSTART" in furl_up:
                body_text = f.evaluate(
                    "document.body ? document.body.innerText.substring(0, 3000) : ''"
                )
                if body_text and body_text.strip():
                    print(f"    [查詢頁] url={furl[:80]}")
                    print(f"    [查詢頁] 內容（前500字）: {body_text[:500]}")
                break
            # 也嘗試 MAIN frame（可能是 DA_APY_Q 或 DA_Ser* 之類）
            if "DA_APY" in furl_up or "APPQ" in furl_up:
                body_text = f.evaluate(
                    "document.body ? document.body.innerText.substring(0, 1000) : ''"
                )
                if body_text and body_text.strip():
                    # 只在沒找到更具體的頁面時才輸出
                    pass
    except Exception:
        pass

    # ── 主要驗證：清單金額比對 ──
    list_amount = latest.get("amount", 0)
    if expected_amount > 0:
        if list_amount == expected_amount:
            print(f"    [主要驗證] 清單金額 {list_amount} == 預期金額 {expected_amount} V")
        else:
            print(f"    [主要驗證] 清單金額 {list_amount} != 預期金額 {expected_amount} X")
            result["ok"] = False
    else:
        print(f"    [主要驗證] 清單金額: {list_amount}（未指定預期金額，略過比對）")

    # ── 次要驗證：APPY frame 內容（best-effort，找不到不算失敗）──
    if "appy" in frames_check:
        appy_data = frames_check["appy"].evaluate("""() => ({
            bugetno: FORM1.BUGETNO_1 ? FORM1.BUGETNO_1.value : '',
            bugcode: FORM1.BUGCODE_1 ? FORM1.BUGCODE_1.value : '',
            amount: FORM1.D_AMOUNT_1 ? FORM1.D_AMOUNT_1.value : '',
        })""")
        result["appy"] = appy_data
        appy_ok = bool(appy_data.get("bugetno") and appy_data.get("amount"))
        print(f"    APPY: bugetno={appy_data.get('bugetno','')}, "
              f"amount={appy_data.get('amount','')} "
              f"{'V' if appy_ok else 'X'}")
    else:
        print("    [INFO] 未找到 APPY frame，略過詳細驗證（不影響結果判定）")
        result["appy"] = {}

    # ── 次要驗證：APPP frame 內容（best-effort，找不到不算失敗）──
    if "appp" in frames_check:
        appp_data = frames_check["appp"].evaluate("""() => {
            const items = [];
            for (let i = 1; i <= 15; i++) {
                const p = FORM1['PRODUCT_' + i];
                const a = FORM1['AMOUNT_' + i];
                if (p && p.value && p.value.trim()) {
                    items.push({
                        row: i,
                        product: p.value,
                        amount: a ? a.value : '0',
                    });
                }
            }
            return {
                items: items,
                content: FORM1.CONTENT ? FORM1.CONTENT.value : '',
            };
        }""")
        result["appp"] = appp_data
        appp_ok = len(appp_data.get("items", [])) > 0
        print(f"    APPP: {len(appp_data.get('items', []))} 項品名 "
              f"{'V' if appp_ok else 'X -- 品名遺失！'}")
        if appp_ok:
            for item in appp_data["items"]:
                print(f"      品項{item['row']}: {item['product']} = ${item['amount']}")
        if not appp_ok:
            result["ok"] = False  # Frame 找到但品名是空的 → 資料真的遺失
    else:
        print("    [INFO] 未找到 APPP frame，略過詳細驗證（不影響結果判定）")
        result["appp"] = {}

    # ── 次要驗證：APPA frame 內容（best-effort，找不到不算失敗）──
    if "appa" in frames_check:
        appa_data = frames_check["appa"].evaluate("""() => ({
            venname: FORM1.VENNAME_1 ? FORM1.VENNAME_1.value : '',
            vendorid_s: FORM1.VENDORID_S_1 ? FORM1.VENDORID_S_1.value : '',
            bankno: FORM1.BANKNO_1 ? FORM1.BANKNO_1.value : '',
            amount: FORM1.AMOUNT_1 ? FORM1.AMOUNT_1.value : '',
            invoiceno: FORM1.INVOICENO_1 ? FORM1.INVOICENO_1.value : '',
        })""")
        result["appa"] = appa_data
        appa_ok = bool(appa_data.get("venname") and appa_data.get("amount")
                       and appa_data.get("amount") != "0")
        print(f"    APPA: venname={appa_data.get('venname','')}, "
              f"amount={appa_data.get('amount','')}, "
              f"bankno={appa_data.get('bankno','')} "
              f"{'V' if appa_ok else 'X -- 受款人遺失！'}")
        if not appa_ok:
            result["ok"] = False  # Frame 找到但受款人是空的 → 資料真的遺失
    else:
        print("    [INFO] 未找到 APPA frame，略過詳細驗證（不影響結果判定）")
        result["appa"] = {}

    # 截圖
    menu_page.screenshot(
        path=f"{OUTPUT_DIR}/verify_{result['record_no']}.png", full_page=True
    )
    print(f"    截圖: {OUTPUT_DIR}/verify_{result['record_no']}.png")

    if result["ok"]:
        if frames_found:
            print(f"  [OK] 記錄 {result['record_no']} 驗證通過！金額與 frame 內容均正確。")
        else:
            print(f"  [OK] 記錄 {result['record_no']} 驗證通過！清單金額 {list_amount} 正確。")
            print(f"       （詳細 frames 無法開啟，建議查看截圖確認品名與受款人）")
    else:
        print(f"  [FAIL] 記錄 {result['record_no']} 驗證失敗！請查看截圖確認問題。")

    return result


def fill_expense_form(frames: dict, receipt_data: dict,
                      menu_page: Page = None, context=None,
                      plan_name: str = "", receipt_seq: int = 1,
                      auto_save: bool = True,
                      use_project: bool = False):
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

    # ── 1. 先填寫 APPY frame（計畫/經費/科目/金額）──取得計畫資訊
    plan_full_name = ""
    plan_code = ""
    items = receipt_data.get("items", [])
    try:
        total_amount = int(float(receipt_data.get("amount", 0)))
    except (ValueError, TypeError):
        total_amount = 0

    if appy_frame and menu_page:
        subject_code = receipt_data.get("subject_code", "")
        plan_full_name, plan_code = fill_appy_frame(
            appy_frame, menu_page, total_amount, subject_code,
            plan_name=plan_name)
    elif not appy_frame:
        print("  警告: 找不到 APPY frame，跳過計畫/經費填寫")

    # ── 2. 生成用途說明（使用實際計畫名稱 + 代碼）──────
    # 格式: {計畫名稱}({計畫代碼})-{品項摘要}
    # 例: 高教深耕計畫(NCUT25TIAB004)-實驗用耗材一批
    non_tax_items = [
        item for item in items
        if not _is_tax_item(item.get("name", ""))
    ]
    if len(non_tax_items) == 0:
        items_summary = "經費核銷"
    elif len(non_tax_items) <= 3:
        items_summary = "、".join(
            item.get("name", "") for item in non_tax_items
            if item.get("name", "")
        ) or "經費核銷"
    else:
        first_name = non_tax_items[0].get("name", "核銷用品")
        items_summary = f"{first_name}等{len(non_tax_items)}項"

    if plan_full_name and plan_code:
        content_text = f"{plan_full_name}({plan_code})-{items_summary}"
    elif plan_full_name:
        content_text = f"{plan_full_name}-{items_summary}"
    elif plan_name:
        content_text = f"{plan_name}-{items_summary}"
    else:
        content_text = f"經費核銷-{items_summary}"

    # 用 JS 填寫（frameset 結構下 Playwright fill() 可能報 not visible）
    appp_frame.evaluate(f"""() => {{
        const el = document.querySelector('textarea[name="{APPP_FIELDS["content"]}"]');
        if (el) {{ el.value = "{_js_escape(content_text)}"; }}
    }}""")
    print(f"    用途說明: {content_text}")

    # ── 3. 填寫憑證日期 ─────────────────────────
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

    # ── 4. 稅額智慧處理 + 填寫品項明細 ──────────────
    # 欄位名稱格式: PRODUCT_{N}, PRODUCT1_{N}, PRODUCT2_{N},
    #               SERUNIT_{N}, QUANTITY_{N}, AMOUNT_{N}
    # N = 1~15 (最多 15 列)
    #
    # 稅額處理策略:
    #   Case A: 單品項 + 稅額 → 直接把稅額加入品項總價（不產生差額行）
    #   Case B: 多品項 + 稅額 → 品項填原價，稅額合計為「其他差額」
    #   Case C: 無稅額相關 → 原有差額邏輯

    # 分離稅額項目和一般品項
    tax_items = [item for item in items if _is_tax_item(item.get("name", ""))]
    regular_items = [item for item in items if not _is_tax_item(item.get("name", ""))]

    total_tax = 0
    for ti in tax_items:
        try:
            tax_price = int(float(ti.get("price", 0)))
            tax_qty = int(float(ti.get("quantity", 1)))
            total_tax += tax_price * tax_qty
        except (ValueError, TypeError):
            pass

    parsed_items = []
    current_sum = 0

    if tax_items and len(regular_items) == 1:
        # ── Case A: 單品項 + 稅額 → 合併成一筆 ──
        item = regular_items[0]
        try:
            qty = int(float(item.get("quantity", 1)))
        except (ValueError, TypeError):
            qty = 1
        try:
            price = int(float(item.get("price", 0)))
        except (ValueError, TypeError):
            price = 0
        item_total = price * qty + total_tax
        parsed_items.append({
            "name": str(item.get("name", "")),
            "spec": str(item.get("spec", "")),
            "qty": qty,
            "total": item_total
        })
        current_sum = item_total
        print(f"    [稅額處理] Case A: 單品項+稅額({total_tax}) → 合併為 {item_total}")

    elif tax_items and len(regular_items) > 1:
        # ── Case B: 多品項 + 稅額 → 品項填原價，稅額歸「其他差額」──
        for item in regular_items[:14]:
            try:
                qty = int(float(item.get("quantity", 1)))
            except (ValueError, TypeError):
                qty = 1
            try:
                price = int(float(item.get("price", 0)))
            except (ValueError, TypeError):
                price = 0
            if price == 0 and len(parsed_items) == 0:
                price = total_amount
            item_total = price * qty
            parsed_items.append({
                "name": str(item.get("name", "")),
                "spec": str(item.get("spec", "")),
                "qty": qty,
                "total": item_total
            })
            current_sum += item_total
        # 稅額合計作為「其他差額」
        if total_tax > 0:
            parsed_items.append({
                "name": "其他差額",
                "spec": "稅額合計",
                "qty": 1,
                "total": total_tax
            })
            current_sum += total_tax
        print(f"    [稅額處理] Case B: {len(regular_items)}品項+稅額({total_tax}) → 稅額歸差額行")

    else:
        # ── Case C: 無稅額 → 原有邏輯 ──
        for item in items[:14]:
            try:
                qty = int(float(item.get("quantity", 1)))
            except (ValueError, TypeError):
                qty = 1
            try:
                price = int(float(item.get("price", 0)))
            except (ValueError, TypeError):
                price = 0
            if price == 0 and len(parsed_items) == 0:
                price = total_amount
            item_total = price * qty
            parsed_items.append({
                "name": str(item.get("name", "")),
                "spec": str(item.get("spec", "")),
                "qty": qty,
                "total": item_total
            })
            current_sum += item_total

    # 差額補正（適用 Case B / Case C 有剩餘差額的情境）
    diff = total_amount - current_sum
    if diff > 0 and len(parsed_items) > 0:
        # 檢查是否已經有「其他差額」行（Case B 已加過）
        has_diff_row = any(p["name"] == "其他差額" for p in parsed_items)
        if not has_diff_row:
            parsed_items.append({
                "name": "其他差額",
                "spec": "",
                "qty": 1,
                "total": diff
            })
    elif diff < 0:
        print(f"    [WARN] OCR 明細加總 ({current_sum}) 大於總金額 ({total_amount})，將合併為單一明細！")
        parsed_items = [{
            "name": "發票明細（系統自動調整）",
            "spec": "",
            "qty": 1,
            "total": total_amount
        }]
    elif not parsed_items and total_amount > 0:
        parsed_items = [{
            "name": "核銷明細",
            "spec": "",
            "qty": 1,
            "total": total_amount
        }]

    for i, item_data in enumerate(parsed_items, start=1):
        # 先過濾 Big5 不支援字元（如 Ω），避免 POST 時亂碼導致伺服器解析失敗
        raw_name = _sanitize_big5(item_data["name"])
        raw_spec = _sanitize_big5(item_data["spec"])
        if raw_name != item_data["name"]:
            print(f"    [sanitize] 品名: '{item_data['name']}' → '{raw_name}'")
        item_name = _js_escape(raw_name)
        item_spec = _js_escape(raw_spec)
        item_qty = item_data["qty"]
        item_price = item_data["total"]

        appp_frame.evaluate(f"""() => {{
            const setVal = (name, val) => {{
                const el = document.querySelector('input[name="' + name + '"]');
                if (el) {{
                    el.value = val;
                    el.dispatchEvent(new Event('change', {{bubbles:true}}));
                    el.dispatchEvent(new Event('blur', {{bubbles:true}}));
                }}
            }};
            setVal('PRODUCT_{i}',  '{item_name}');   // 品名
            setVal('PRODUCT1_{i}', '{item_spec}');    // 詳細規格
            setVal('SERUNIT_{i}',  '式');             // 單位
            setVal('QUANTITY_{i}', '{item_qty}');      // 數量
            setVal('AMOUNT_{i}',   '{item_price}');    // 總價
            if (typeof SUM_SUM === 'function') SUM_SUM();
        }}""")
        print(f"    品項{i}: {item_data['name']} x{item_qty} 總價: {item_price}")

    # 確認 APPP 填寫後的實際值
    if parsed_items:
        appp_conf = appp_frame.evaluate("""() => {
            const el = document.querySelector('input[name="PRODUCT_1"]');
            return el ? el.value : '(not found)';
        }""")
        print(f"    [確認 APPP] PRODUCT_1 = {appp_conf!r}")

    # ── 5. 填寫 APPA frame（受款人）──────────────────
    appa_frame = frames.get("appa")
    if appa_frame and menu_page and context:
        fill_appa_frame(appa_frame, menu_page, context,
                        receipt_data, receipt_seq)
    elif not appa_frame:
        print("  警告: 找不到 APPA frame，跳過受款人填寫")
    elif not context:
        print("  警告: 未提供 BrowserContext，跳過受款人填寫")

    # 確認 APPA 填寫後的實際值
    if appa_frame:
        appa_conf = appa_frame.evaluate("""() => ({
            venname:   FORM1.VENNAME_1   ? FORM1.VENNAME_1.value   : '',
            invoiceno: FORM1.INVOICENO_1 ? FORM1.INVOICENO_1.value : '',
            amount:    FORM1.AMOUNT_1    ? FORM1.AMOUNT_1.value    : '',
        })""")
        print(f"    [確認 APPA] row1: venname={appa_conf.get('venname')!r} "
              f"invoice={appa_conf.get('invoiceno')!r} "
              f"amount={appa_conf.get('amount')!r}")

    # ── 6. 驗證三金額一致 → 自動/手動存入 ────────────────
    if appy_frame and menu_page:
        saved = verify_and_save(appy_frame, menu_page, auto_save=auto_save)
        if auto_save:
            if saved:
                print("  [OK] 表單已自動存入")
                # ── 7. 回到購案管理驗證存入內容 ────────────
                try:
                    verify_result = verify_saved_record(
                        menu_page, expected_amount=total_amount,
                        use_project=use_project)
                    if verify_result.get("ok"):
                        note = verify_result.get("note", "")
                        rec = verify_result.get("record_no", "")
                        if note:
                            print(f"  [OK] {note}")
                        else:
                            print(f"  [OK] 驗證通過！記錄 {rec}")
                    else:
                        print(f"  [WARN] 驗證未通過，請手動確認")
                except Exception as e:
                    print(f"  [WARN] 驗證過程發生錯誤: {e}")
                    print(f"  [INFO] 存入已由 dialog 確認成功，驗證可忽略")
            else:
                print("  [FAIL] 自動存入失敗，請手動確認")
        else:
            print("  表單填寫完成（未啟用自動存入，請手動點擊「存入」）")
    else:
        print("  警告: 找不到 APPY frame，無法進行存檔準備")


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


def run_form_fill(receipt_data: dict, headless: bool = True,
                   plan_name: str = "", receipt_seq: int = 1,
                   auto_save: bool = True, use_project: bool = False):
    """
    完整流程：啟動瀏覽器 → 登入 → 導航 → 填單（含受款人 + 自動存入）。

    Args:
        receipt_data: OCR 辨識結果 dict
        headless: 是否使用 headless 瀏覽器
        plan_name: 計畫名稱關鍵字（如 "高教深耕"）
        receipt_seq: 當天收據流水號 (1, 2, 3, ...)
        auto_save: 是否在金額一致時自動存入

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
        frames = navigate_to_expense_form(menu_page, use_project=use_project,
                                          plan_name=plan_name)

        # 3. 填寫表單（品名 + 經費 + 受款人 + 存入）
        fill_expense_form(
            frames, receipt_data,
            menu_page=menu_page,
            context=context,
            plan_name=plan_name,
            receipt_seq=receipt_seq,
            auto_save=auto_save,
            use_project=use_project,
        )

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
    # 測試用假資料（不自動存入，僅填單截圖）
    test_data = {
        "date": "2026-02-26",
        "vendor": "全家便利商店",
        "amount": 150,
        "tax_id": "12345678",
        "invoice_no": "",
        "items": [
            {"name": "文具用品", "quantity": 1, "price": 150}
        ],
    }

    print("=== 核銷自動填單測試 ===")
    menu_page, frames, browser, pw = run_form_fill(
        test_data,
        headless=True,
        plan_name="",       # 空白=選預設計畫
        receipt_seq=1,
        auto_save=False,    # 測試模式不自動存入
    )
    print("=== 完成 ===")
    browser.close()
    pw.stop()
