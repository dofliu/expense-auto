"""設定檔：系統網址、欄位對應、核銷類別等。"""

import os
from dotenv import load_dotenv

load_dotenv("credentials.env")

# ── 學校核銷系統帳密 ──────────────────────────────────
SYSTEM_URL = os.getenv("SYSTEM_URL", "https://account.ncut.edu.tw/APSWIS_Q/Login_L_Q.asp")
USERNAME = os.getenv("NCUT_USERNAME", "")
PASSWORD = os.getenv("NCUT_PASSWORD", "")

# ── 登入頁面元素 selector ─────────────────────────────
LOGIN_SELECTORS = {
    "user_id": 'input[name="ID"]',
    "password": 'input[name="PWD"]',
    "captcha_input": 'input[name="CheckCode"]',
    "captcha_image": 'img[src*="ValidCode"]',
    "submit_button": 'input[name="xEnter"]',
    "confirm_button": 'input[name="Enter"]',
}

# ── URL ──────────────────────────────────────────────
CAPTCHA_URL = "https://account.ncut.edu.tw/ValidCode_2.asp"
MENU_URL = "https://account.ncut.edu.tw/APSWIS_Q/Dept_Add_Q/DA_SerBug_Menu_Q.asp?Firstload=Y"

# ── 檔案路徑 ─────────────────────────────────────────
RECEIPTS_DIR = "receipts"
OUTPUT_DIR = "output"

# ── 頁面 Frame 結構 ──────────────────────────────────
# 主選單 frameset (DA_SerBug_Menu_Q.asp)
#   ├─ TITLE  : 功能選單列 (DA_SerFun_Q.asp)
#   ├─ MAIN   : 主內容區
#   ├─ OT     : 共用功能 (hidden)
#   ├─ CK_VN  : 廠商檢核 (hidden)
#   ├─ LA_AM  : 金額相關 (hidden)
#   ├─ TRAN   : 傳輸相關 (hidden)
#   └─ OTHER  : 空白頁 (hidden)
#
# 核銷表單 frameset (STD_APPY_FRM_Q.asp, loads in MAIN)
#   ├─ APPY   : 表頭 (STD_APPY_Q.asp) ── 用途說明、計畫經費、金額
#   ├─ APPP   : 品項明細 (STD_APPP_Q.asp) ── 品名、數量、單價
#   ├─ APPA   : 預算分攤 (STD_APPA_Q.asp) (hidden)
#   └─ PS     : 存檔 handler (PR_SAVE_Q.asp) (hidden)

# ── 購案類別設定（直接核銷 / 零用金）───────────────────
EXPENSE_CATEGORY = {
    "checkbox": "CHK3",             # 直接核銷(零用金) 的 checkbox name
    "APPYSET": "13",
    "MOVETYPE": "6",
    "SETNAME": "直接核銷(零用金)",
    "ISAPPY": "True",
    "ISVOUC": "True",
    "ISTEMP": "False",
    "ISCASH": "True",
    "ISPURC": "False",
    "SHOWVEN": "True",
    "SHOWPRO": "True",
    "ISPERIOD": "False",
}

# ── APPP frame (品項明細) 欄位 ────────────────────────
# 每一列有品名/規格/廠牌/單位/數量/總價/置放地點/保管人
# 欄位 name 格式需進一步確認 (可能是 PNAME_1, PQTY_1 等)
APPP_FIELDS = {
    "content": "CONTENT",           # 用途說明 textarea
    "receipt_date_y": "RCDAT_Y",    # 憑證日期-年 (ROC, e.g. 115)
    "receipt_date_m": "RCDAT_M",    # 憑證日期-月
    "receipt_date_d": "RCDAT_D",    # 憑證日期-日
    "receipt_date_checkbox": "RCDAT_1",  # 啟用憑證日期 checkbox
    "end_date_y": "RCDATB_Y",      # 結束日期-年
    "end_date_m": "RCDATB_M",      # 結束日期-月
    "end_date_d": "RCDATB_D",      # 結束日期-日
    "end_date_checkbox": "RCDATB_1",
    "approval_date_y": "RCDATE_Y", # 核定日期-年
    "approval_date_m": "RCDATE_M", # 核定日期-月
    "approval_date_d": "RCDATE_D", # 核定日期-日
}

# ── APPY frame (表頭) 欄位 ────────────────────────────
# 每行 N (1~20):
#   BUGETNO_N   — 計畫編號 (SELECT, onchange=BN_N())
#   BUGCODE_N   — 經費用途 (SELECT, onclick→SERSUB_N.click())
#   D_APYKIND_N — 分類     (SELECT)
#   SERSUB_N    — 科目     (SELECT, onclick→SS_N(); SUBJECTNO_N.value=this.value)
#   SUBJECTNO_N — 科目代碼 (INPUT text, 可直接輸入)
#   D_AMOUNT_N  — 金額     (INPUT text)
#   MOVETYPE_N  — hidden=6
#   A9_N        — 經費餘額 (hidden, by BC_N() from LA_AM)
APPY_FIELDS = {
    "bugetno": "BUGETNO",       # 計畫編號 select
    "bugcode": "BUGCODE",       # 經費用途 select
    "apykind": "D_APYKIND",     # 分類 select
    "sersub": "SERSUB",         # 科目 select (all subjects)
    "subjectno": "SUBJECTNO",   # 科目代碼 text input
    "amount": "D_AMOUNT",       # 金額 text input
}

# ── 預設會計科目 ──────────────────────────────────────
# 常用科目對照：
#   110704-8012 管理及總務費用-材料及用品費 (辦公用品、文具)
#   110704-8013 管理及總務費用-服務費用 (印刷、廣告)
#   110704-8014 管理及總務費用-維護費
#   110704-8016 管理及總務費用-郵電費
#   110704-8023 教學研究及訓輔費用-材料及用品費
#   110704-8022 教學研究及訓輔費用-服務費用
DEFAULT_SUBJECT = "110704-8012"  # 材料及用品費（一般辦公/文具支出）

# ── OCR 結果到表單的欄位對映 ──────────────────────────
# OCR 回傳 dict 的 key → 表單欄位名稱
FIELD_MAPPING = {
    "date": "receipt_date",    # 發票日期 → RCDAT_Y/M/D
    "vendor": "content",       # 廠商名稱 → 用途說明
    "amount": "total_price",   # 金額
    "tax_id": "",              # 統一編號（表單內可能不需要）
    "invoice_no": "",          # 發票號碼（表單內可能不需要）
    "item_desc": "item_name",  # 品名
}
