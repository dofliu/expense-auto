"""測試：真正存入，攔截 HTTP POST 看伺服器收到什麼資料。

重點：用 Playwright route 攔截送往 STD_SAVE_SE1_Q.asp 的 POST，
看 D_STR / P_STR / A_STR 是否都在 POST body 中。
"""
import json, time, os, urllib.parse
from form_filler import (
    start_browser, login, navigate_to_expense_form,
    fill_expense_form, _js_escape,
)
from config import OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 測試資料 ──
receipt_data = {
    "date": "2026-02-11",
    "vendor": "測試商店-網路攔截",
    "amount": 77,
    "invoice_no": "",
    "items": [
        {"name": "網路測試品", "quantity": 1, "price": 77},
    ],
}

pw, browser, context = start_browser(headless=False)
menu_page = login(context)

# ── 導航 + 填寫（不自動存入）──
frames = navigate_to_expense_form(menu_page, use_project=True, plan_name="定位量測")
fill_expense_form(
    frames, receipt_data,
    menu_page=menu_page, context=context,
    plan_name="定位量測", receipt_seq=88,
    auto_save=False,
)

appy_frame = frames.get("appy")

# ====================================================================
# 攔截 STD_SAVE_SE1_Q.asp 的 POST 請求
# ====================================================================
print("\n" + "="*60)
print("設定 HTTP 攔截...")
print("="*60)

captured_requests = []

def handle_route(route):
    """攔截 POST 到 STD_SAVE_SE1_Q.asp，記錄 body 後放行。"""
    request = route.request
    url = request.url
    method = request.method
    post_data = request.post_data or ""
    headers = request.headers

    print(f"\n  [HTTP] {method} {url[:80]}")
    print(f"  Content-Type: {headers.get('content-type', 'N/A')}")
    print(f"  POST body length: {len(post_data)}")

    # 解析 form data
    parsed = {}
    if post_data:
        try:
            # URL-encoded form data
            pairs = post_data.split('&')
            for pair in pairs:
                if '=' in pair:
                    key, val = pair.split('=', 1)
                    key = urllib.parse.unquote(key, encoding='big5', errors='replace')
                    val_decoded = urllib.parse.unquote(val, encoding='big5', errors='replace')
                    parsed[key] = val_decoded
                    # 特別顯示 D_STR, P_STR, A_STR
                    if key in ('D_STR', 'P_STR', 'A_STR', 'ABSTRACT', 'IsNew', 'APPYSET'):
                        print(f"    {key} = {val_decoded[:200]}")
                    elif key in ('D_STR', 'P_STR', 'A_STR'):
                        print(f"    {key} (raw) = {val[:200]}")
        except Exception as e:
            print(f"    解析 POST 失敗: {e}")

    captured_requests.append({
        "url": url,
        "method": method,
        "content_type": headers.get('content-type', ''),
        "body_length": len(post_data),
        "body_raw": post_data[:5000],
        "parsed": {k: v[:500] for k, v in parsed.items()},
    })

    # 繼續讓請求正常送出
    route.continue_()

# 攔截所有送往 STD_SAVE 的請求
menu_page.route("**/STD_SAVE*", handle_route)
# 也攔截 PR_SAVE
menu_page.route("**/PR_SAVE*", handle_route)

# ====================================================================
# 設定 dialog handler
# ====================================================================
dialog_messages = []
def handle_dialog(dialog):
    msg = dialog.message
    dtype = dialog.type
    dialog_messages.append({"type": dtype, "message": msg})
    print(f"\n  [DIALOG {dtype}] {msg}")

    if dtype == "confirm" and "受款人尚未編輯" in msg:
        dialog.dismiss()  # 不編輯，繼續存
    elif dtype == "confirm" and "受款人尚未輸入" in msg:
        dialog.dismiss()
    else:
        dialog.accept()

menu_page.on("dialog", handle_dialog)

# ====================================================================
# 執行真正的存入
# ====================================================================
print("\n" + "="*60)
print("執行 SUM_ALERT() 存入...")
print("="*60)

# 先確認資料
pre_check = appy_frame.evaluate("""() => ({
    d_amount: FORM1.D_AMOUNT_1 ? FORM1.D_AMOUNT_1.value : '',
    bugetno: FORM1.BUGETNO_1 ? FORM1.BUGETNO_1.value : '',
    bugcode: FORM1.BUGCODE_1 ? FORM1.BUGCODE_1.value : '',
})""")
print(f"  存入前 APPY: {pre_check}")

appp_check = frames["appp"].evaluate("""() => ({
    product1: FORM1.PRODUCT_1 ? FORM1.PRODUCT_1.value : '',
    amount1: FORM1.AMOUNT_1 ? FORM1.AMOUNT_1.value : '',
})""")
print(f"  存入前 APPP: {appp_check}")

appa_check = frames["appa"].evaluate("""() => ({
    venname1: FORM1.VENNAME_1 ? FORM1.VENNAME_1.value : '',
    amount1: FORM1.AMOUNT_1 ? FORM1.AMOUNT_1.value : '',
    vendorid1: (FORM1.VENDORID_1 ? FORM1.VENDORID_1.value : '').substring(0, 30),
})""")
print(f"  存入前 APPA: {appa_check}")

# 呼叫 SUM_ALERT
print("\n  呼叫 SUM_ALERT()...")
try:
    appy_frame.evaluate("SUM_ALERT();")
except Exception as e:
    print(f"  SUM_ALERT 錯誤: {e}")

# 等待 — 給夠時間讓 HTTP 請求完成和任何 dialog 出現
print("  等待 5 秒...")
time.sleep(5)

# 再等一下看有沒有更多 dialog
print("  再等 3 秒...")
time.sleep(3)

# ====================================================================
# 檢查結果
# ====================================================================
print("\n" + "="*60)
print("結果")
print("="*60)

print(f"\n  Dialog 訊息 ({len(dialog_messages)}):")
for d in dialog_messages:
    print(f"    [{d['type']}] {d['message']}")

print(f"\n  攔截到的 HTTP 請求 ({len(captured_requests)}):")
for i, req in enumerate(captured_requests):
    print(f"\n  Request {i+1}: {req['method']} {req['url'][:80]}")
    print(f"    Content-Type: {req['content_type']}")
    print(f"    Body length: {req['body_length']}")
    p = req.get("parsed", {})
    for key in ['D_STR', 'P_STR', 'A_STR', 'ABSTRACT', 'IsNew']:
        if key in p:
            print(f"    {key}: {p[key][:200]}")

# 檢查 PS frame 的狀態
print("\n  PS frame 狀態:")
for f in menu_page.frames:
    if "PR_SAVE" in f.url or "SAVE" in f.url or f.name == "PS":
        print(f"    name={f.name} url={f.url[:100]}")
        try:
            content = f.evaluate("document.body ? document.body.innerText.substring(0, 500) : 'no body'")
            print(f"    body: {content[:300]}")
        except Exception as e:
            print(f"    (無法讀取: {e})")

# 截圖
menu_page.screenshot(path=f"{OUTPUT_DIR}/test_actual_save.png", full_page=True)

# 儲存完整 debug 資訊
with open(f"{OUTPUT_DIR}/actual_save_debug.json", "w", encoding="utf-8") as f:
    json.dump({
        "dialog_messages": dialog_messages,
        "captured_requests": captured_requests,
        "pre_check": {
            "appy": pre_check,
            "appp": appp_check,
            "appa": appa_check,
        },
    }, f, ensure_ascii=False, indent=2)

print(f"\n  Debug: {OUTPUT_DIR}/actual_save_debug.json")
print("  截圖: {OUTPUT_DIR}/test_actual_save.png")

# 清理
menu_page.unroute("**/STD_SAVE*")
menu_page.unroute("**/PR_SAVE*")

print("\n按 Enter 結束...")
try:
    input()
except (EOFError, KeyboardInterrupt):
    pass

browser.close()
pw.stop()
