"""Debug: 填單後嘗試存入，捕捉所有 dialog 訊息。"""
import json, time, os
from form_filler import (
    start_browser, login, navigate_to_expense_form,
    fill_appa_frame, fill_appy_frame, _roc_date, _js_escape,
    generate_receipt_no, _idate_format,
)
from config import APPP_FIELDS, OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 模擬 OCR 結果
receipt_data = {
    "date": "2026-02-11",
    "vendor": "新昇電子材料有限公司",
    "amount": 876,
    "invoice_no": "XC-77759774",
    "items": [
        {"name": "9596D 低溫錫膏 特大6.4/45mmROHS", "quantity": 2, "price": 33},
        {"name": "VWR050-150 500歐/50W 大功率線繞VR", "quantity": 1, "price": 810},
    ],
}

pw, browser, context = start_browser(headless=False)
menu_page = login(context)

# 導航到計畫請購表單
frames = navigate_to_expense_form(menu_page, use_project=True, plan_name="定位量測")

appp_frame = frames.get("appp")
appy_frame = frames.get("appy")
appa_frame = frames.get("appa")

print(f"\nFrames found: appp={appp_frame is not None}, appy={appy_frame is not None}, appa={appa_frame is not None}")

# ── 填 APPP (品名) ──
vendor = receipt_data.get("vendor", "")
items_desc = ", ".join(item.get("name", "") for item in receipt_data.get("items", []))
content_text = f"{vendor} - {items_desc}"
appp_frame.evaluate(f"""() => {{
    const el = document.querySelector('textarea[name="{APPP_FIELDS["content"]}"]');
    if (el) el.value = "{_js_escape(content_text)}";
}}""")

date_str = receipt_data["date"]
roc_y, roc_m, roc_d = _roc_date(date_str)
appp_frame.evaluate(f"""() => {{
    const cb = document.querySelector('input[name="{APPP_FIELDS["receipt_date_checkbox"]}"]');
    if (cb && !cb.checked) cb.click();
    ['RCDAT_Y', 'RCDAT_M', 'RCDAT_D'].forEach((name, i) => {{
        const val = ['{roc_y}', '{roc_m}', '{roc_d}'][i];
        const el = document.querySelector('select[name="' + name + '"]');
        if (el) {{ el.disabled = false; el.value = val; }}
    }});
}}""")

items = receipt_data["items"]
total_amount = receipt_data["amount"]
for i, item in enumerate(items[:15], start=1):
    item_name = _js_escape(str(item.get("name", "")))
    item_qty = item.get("quantity", 1)
    unit_price = item.get("price", 0)
    item_price = unit_price * item_qty
    appp_frame.evaluate(f"""() => {{
        const setVal = (name, val) => {{
            const el = document.querySelector('input[name="' + name + '"]');
            if (el) el.value = val;
        }};
        setVal('PRODUCT_{i}', '{item_name}');
        setVal('SERUNIT_{i}', '式');
        setVal('QUANTITY_{i}', '{item_qty}');
        setVal('AMOUNT_{i}', '{item_price}');
    }}""")
print("APPP filled")

# ── 填 APPY (經費) ──
fill_appy_frame(appy_frame, menu_page, total_amount, plan_name="定位量測")

# ── 填 APPA (受款人) ──
fill_appa_frame(appa_frame, menu_page, context, receipt_data, receipt_seq=1)

# 檢查 APPA 欄位值
time.sleep(2)
appa_values = appa_frame.evaluate("""() => {
    const fields = {};
    ['PROX_1', 'PAYKIND_1', 'INVOICENO_1', 'IDATE_1',
     'VENDORID_S_1', 'VENDORID_1', 'VENNAME_1',
     'BANKNO_1', 'ACCOUNT_1', 'ACCOUNTNAM_1', 'AMOUNT_1'].forEach(name => {
        const el = document.querySelector('[name="' + name + '"]');
        if (el) {
            fields[name] = el.type === 'checkbox' ? el.checked : el.value;
        } else {
            fields[name] = '(NOT FOUND)';
        }
    });
    return fields;
}""")
print("\n=== APPA field values ===")
for k, v in appa_values.items():
    print(f"  {k}: {v}")

# ── 驗證金額 ──
appy_frame.evaluate("""() => {
    if (typeof CHK_APPP === 'function') CHK_APPP();
    if (typeof CHK_APPA === 'function') CHK_APPA();
    if (typeof SUM_SUM === 'function') FORM1.SUM_LIST.click();
}""")
time.sleep(2)

sums = appy_frame.evaluate("""() => ({
    budget: FORM1.SUM_LIST ? FORM1.SUM_LIST.value : '',
    items: FORM1.SUM_APPP ? FORM1.SUM_APPP.value : '',
    payee: FORM1.SUM_APPA ? FORM1.SUM_APPA.value : '',
})""")
print(f"\n=== Sums ===")
print(f"  Budget: {sums.get('budget')}")
print(f"  Items:  {sums.get('items')}")
print(f"  Payee:  {sums.get('payee')}")

# ── 嘗試 SUM_ALERT() 並捕捉所有 dialog ──
dialog_messages = []

def on_dialog(dialog):
    msg = dialog.message
    dtype = dialog.type
    dialog_messages.append({"type": dtype, "message": msg})
    print(f"  [DIALOG {dtype}] {msg}")
    dialog.accept()

# Register dialog handler on ALL pages and frames
menu_page.on("dialog", on_dialog)

print("\n=== Calling SUM_ALERT() ===")
try:
    appy_frame.evaluate("SUM_ALERT();")
except Exception as e:
    print(f"  SUM_ALERT error: {e}")
time.sleep(5)

print(f"\n=== Dialog messages ({len(dialog_messages)}) ===")
for d in dialog_messages:
    print(f"  [{d['type']}] {d['message']}")

# Take screenshot
menu_page.screenshot(path=f"{OUTPUT_DIR}/save_debug.png", full_page=True)
print(f"\nScreenshot: {OUTPUT_DIR}/save_debug.png")

# Save debug info
with open(f"{OUTPUT_DIR}/save_debug.json", "w", encoding="utf-8") as f:
    json.dump({
        "appa_values": appa_values,
        "sums": sums,
        "dialogs": dialog_messages,
    }, f, ensure_ascii=False, indent=2)

browser.close()
pw.stop()
