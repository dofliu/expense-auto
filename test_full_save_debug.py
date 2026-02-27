"""
完整存入測試：
1. 填寫三個區塊
2. 點選編輯按鈕來回切換，驗證資料不遺失
3. 攔截 HTTP POST 觀察 D_STR / P_STR / A_STR 的內容與編碼
4. 真正存入 + 長時間等待對話框
5. 讀取 PS frame 回應
"""
import json, time, os, urllib.parse, binascii
from form_filler import (
    start_browser, login, navigate_to_expense_form,
    fill_expense_form, _js_escape,
)
from config import OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 測試資料 ──
receipt_data = {
    "date": "2026-02-11",
    "vendor": "測試商店-完整測試",
    "amount": 120,
    "invoice_no": "",
    "items": [
        {"name": "測試品項A", "quantity": 1, "price": 80},
        {"name": "測試品項B", "quantity": 1, "price": 40},
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
appp_frame = frames.get("appp")
appa_frame = frames.get("appa")

# ====================================================================
# Step 1: 檢查 PS frame 的 FORM1 charset / encoding
# ====================================================================
print("\n" + "="*60)
print("Step 1: 檢查 PS frame 表單設定")
print("="*60)

ps_info = appy_frame.evaluate("""() => {
    try {
        const ps = parent.PS;
        const form = ps.FORM1;
        const doc = ps.document;
        return {
            // 表單屬性
            form_action: form.action || '',
            form_method: form.method || '',
            form_enctype: form.enctype || '',
            form_encoding: form.encoding || '',
            form_acceptCharset: form.acceptCharset || '',
            // 文件 charset
            doc_charset: doc.charset || doc.characterSet || '',
            doc_contentType: doc.contentType || '',
            // meta charset
            meta_charset: (() => {
                const meta = doc.querySelector('meta[charset]');
                if (meta) return meta.getAttribute('charset');
                const meta2 = doc.querySelector('meta[http-equiv="Content-Type"]');
                if (meta2) return meta2.getAttribute('content');
                return '';
            })(),
            // 所有 hidden fields
            hidden_fields: [...form.querySelectorAll('input[type=hidden], textarea')]
                .map(el => ({
                    name: el.name,
                    type: el.type,
                    valueLen: (el.value || '').length,
                    valueSample: (el.value || '').substring(0, 50),
                })),
            // PS frame URL
            ps_url: ps.location.href.substring(0, 200),
        };
    } catch(e) {
        return { error: e.message };
    }
}""")

print(f"  PS URL: {ps_info.get('ps_url', '')}")
print(f"  form action: {ps_info.get('form_action', '')}")
print(f"  form method: {ps_info.get('form_method', '')}")
print(f"  form enctype: {ps_info.get('form_enctype', '')}")
print(f"  form encoding: {ps_info.get('form_encoding', '')}")
print(f"  form acceptCharset: {ps_info.get('form_acceptCharset', '')}")
print(f"  doc charset: {ps_info.get('doc_charset', '')}")
print(f"  doc contentType: {ps_info.get('doc_contentType', '')}")
print(f"  meta charset: {ps_info.get('meta_charset', '')}")
print(f"\n  Hidden fields ({len(ps_info.get('hidden_fields', []))}):")
for hf in ps_info.get('hidden_fields', []):
    print(f"    {hf['name']} ({hf['type']}) len={hf['valueLen']} val={hf['valueSample']}")

# ====================================================================
# Step 2: 驗證填入的資料
# ====================================================================
print("\n" + "="*60)
print("Step 2: 驗證各區塊資料")
print("="*60)

def verify_all_frames():
    """讀取三個 frame 的關鍵欄位值"""
    appy_data = appy_frame.evaluate("""() => ({
        bugetno: FORM1.BUGETNO_1 ? FORM1.BUGETNO_1.value : '',
        bugcode: FORM1.BUGCODE_1 ? FORM1.BUGCODE_1.value : '',
        amount: FORM1.D_AMOUNT_1 ? FORM1.D_AMOUNT_1.value : '',
        sum_list: FORM1.SUM_LIST ? FORM1.SUM_LIST.value : '',
        appybuy: FORM1.APPYBUY ? FORM1.APPYBUY.value : 'N/A',
        no_math: FORM1.NO_MATH ? FORM1.NO_MATH.value : 'N/A',
    })""")

    appp_data = appp_frame.evaluate("""() => {
        const items = [];
        for (let i = 1; i <= 5; i++) {
            const p = FORM1['PRODUCT_' + i];
            const a = FORM1['AMOUNT_' + i];
            if (p && p.value) {
                items.push({
                    row: i,
                    product: p.value,
                    quantity: FORM1['QUANTITY_' + i] ? FORM1['QUANTITY_' + i].value : '',
                    serunit: FORM1['SERUNIT_' + i] ? FORM1['SERUNIT_' + i].value : '',
                    amount: a ? a.value : '',
                });
            }
        }
        return {
            items: items,
            content: FORM1.CONTENT ? FORM1.CONTENT.value : '',
            sum: FORM1.SUM_LIST ? FORM1.SUM_LIST.value : '',
        };
    }""")

    appa_data = appa_frame.evaluate("""() => ({
        venname: FORM1.VENNAME_1 ? FORM1.VENNAME_1.value : '',
        vendorid_s: FORM1.VENDORID_S_1 ? FORM1.VENDORID_S_1.value : '',
        vendorid: FORM1.VENDORID_1 ? (FORM1.VENDORID_1.value || '').substring(0, 30) : '',
        bankno: FORM1.BANKNO_1 ? FORM1.BANKNO_1.value : '',
        account: FORM1.ACCOUNT_1 ? FORM1.ACCOUNT_1.value : '',
        accountnam: FORM1.ACCOUNTNAM_1 ? FORM1.ACCOUNTNAM_1.value : '',
        amount: FORM1.AMOUNT_1 ? FORM1.AMOUNT_1.value : '',
        invoiceno: FORM1.INVOICENO_1 ? FORM1.INVOICENO_1.value : '',
        idate: FORM1.IDATE_1 ? FORM1.IDATE_1.value : '',
        paykind: FORM1.PAYKIND_1 ? FORM1.PAYKIND_1.value : '',
        sum: FORM1.SUM_LIST ? FORM1.SUM_LIST.value : '',
    })""")

    return appy_data, appp_data, appa_data

appy_data, appp_data, appa_data = verify_all_frames()
print(f"  APPY: bugetno={appy_data['bugetno']}, bugcode={appy_data['bugcode']}, "
      f"amount={appy_data['amount']}, appybuy={appy_data.get('appybuy','')}")
print(f"  APPP: {len(appp_data['items'])} items, content='{appp_data['content'][:30]}'")
for item in appp_data.get("items", []):
    print(f"    row{item['row']}: {item['product']} qty={item['quantity']} "
          f"unit={item['serunit']} amt={item['amount']}")
print(f"  APPA: venname={appa_data['venname']}, amount={appa_data['amount']}, "
      f"bankno={appa_data['bankno']}, invoiceno={appa_data['invoiceno']}")

# ====================================================================
# Step 3: 來回切換編輯按鈕，每次驗證資料
# ====================================================================
print("\n" + "="*60)
print("Step 3: 切換編輯按鈕，驗證資料不遺失")
print("="*60)

# 編輯按鈕 onclick 邏輯（從 APPY frame 執行）:
#   編輯經費: parent.DD.rows="*,0"; parent.QQ.cols="*,0,0";   → 只顯示 APPY
#   編輯品名: parent.DD.rows="160,*"; parent.QQ.cols="*,0,0"; → 上方 APPY + 下方 APPP
#   編輯受款人: parent.DD.rows="160,*"; parent.QQ.cols="0,*,0"; → 上方 APPY + 下方 APPA

button_actions = [
    ("編輯經費", 'parent.DD.rows="*,0"; parent.QQ.cols="*,0,0";'),
    ("編輯品名", 'parent.DD.rows="160,*"; parent.QQ.cols="*,0,0";'),
    ("編輯受款人", 'parent.DD.rows="160,*"; parent.QQ.cols="0,*,0";'),
    ("編輯品名", 'parent.DD.rows="160,*"; parent.QQ.cols="*,0,0";'),
    ("編輯經費", 'parent.DD.rows="*,0"; parent.QQ.cols="*,0,0";'),
    ("編輯受款人", 'parent.DD.rows="160,*"; parent.QQ.cols="0,*,0";'),
    ("編輯經費", 'parent.DD.rows="*,0"; parent.QQ.cols="*,0,0";'),
]

for i, (label, js_code) in enumerate(button_actions, 1):
    print(f"\n  [{i}/{len(button_actions)}] 點擊「{label}」...")
    appy_frame.evaluate(f"() => {{ {js_code} }}")
    time.sleep(1)

    # 驗證資料
    ad, pd, rd = verify_all_frames()
    appy_ok = bool(ad['bugetno'] and ad['amount'])
    appp_ok = len(pd['items']) > 0
    appa_ok = bool(rd['venname'] and rd['amount'])
    status = "OK" if (appy_ok and appp_ok and appa_ok) else "FAIL"
    print(f"    APPY: amount={ad['amount']}, bugetno={'V' if ad['bugetno'] else 'X'}")
    print(f"    APPP: {len(pd['items'])} items {'V' if appp_ok else 'X'}")
    print(f"    APPA: venname={rd['venname'][:10]}, amount={rd['amount']} {'V' if appa_ok else 'X'}")
    print(f"    -> [{status}]")

# 回到正常顯示（編輯經費視圖）
appy_frame.evaluate('() => { parent.DD.rows="*,0"; parent.QQ.cols="*,0,0"; }')
time.sleep(1)

# ====================================================================
# Step 4: 攔截 HTTP POST 並真正存入
# ====================================================================
print("\n" + "="*60)
print("Step 4: 攔截 HTTP POST + 真正存入")
print("="*60)

captured_requests = []

def handle_route(route):
    """攔截 POST，記錄 raw body 的 hex 和解碼結果"""
    request = route.request
    url = request.url
    method = request.method
    post_data = request.post_data or ""
    post_body_bytes = request.post_data_buffer  # raw bytes
    headers = request.headers

    print(f"\n  [HTTP] {method} {url[-60:]}")
    print(f"  Content-Type: {headers.get('content-type', 'N/A')}")
    print(f"  POST text length: {len(post_data)}")
    if post_body_bytes:
        print(f"  POST raw bytes: {len(post_body_bytes)} bytes")

    # 嘗試多種解碼
    parsed_utf8 = {}
    parsed_big5 = {}
    raw_hex_samples = {}

    if post_data:
        # 用 urllib 解析 form data (假設 URL-encoded)
        pairs = post_data.split('&')
        for pair in pairs:
            if '=' in pair:
                key, val = pair.split('=', 1)
                key_dec = urllib.parse.unquote(key)
                # UTF-8 解碼
                try:
                    val_utf8 = urllib.parse.unquote(val, encoding='utf-8', errors='replace')
                    parsed_utf8[key_dec] = val_utf8
                except:
                    parsed_utf8[key_dec] = '(decode error)'
                # Big5 解碼
                try:
                    val_big5 = urllib.parse.unquote(val, encoding='big5', errors='replace')
                    parsed_big5[key_dec] = val_big5
                except:
                    parsed_big5[key_dec] = '(decode error)'

                # 印出關鍵欄位
                if key_dec in ('D_STR', 'P_STR', 'A_STR'):
                    raw_hex_samples[key_dec] = val[:500]
                    print(f"\n    === {key_dec} ===")
                    print(f"    URL-encoded (raw): {val[:200]}")
                    print(f"    UTF-8 decode: {parsed_utf8.get(key_dec, '')[:200]}")
                    print(f"    Big5 decode:  {parsed_big5.get(key_dec, '')[:200]}")
                    # 檢查是否有非 ASCII 的 percent-encoded 部分
                    pct_parts = [p for p in val.split('%') if len(p) >= 2]
                    hex_bytes = []
                    for part in pct_parts[:30]:
                        try:
                            hex_bytes.append(part[:2])
                        except:
                            pass
                    if hex_bytes:
                        print(f"    First hex bytes: {' '.join(hex_bytes[:20])}")

    captured_requests.append({
        "url": url,
        "method": method,
        "content_type": headers.get('content-type', ''),
        "body_text_length": len(post_data),
        "body_bytes_length": len(post_body_bytes) if post_body_bytes else 0,
        "parsed_utf8": {k: v[:500] for k, v in parsed_utf8.items()},
        "parsed_big5": {k: v[:500] for k, v in parsed_big5.items()},
        "raw_hex_samples": raw_hex_samples,
        "body_raw_first2000": post_data[:2000],
    })

    # 放行
    route.continue_()

# 攔截所有存入相關的 POST
menu_page.route("**/STD_SAVE*", handle_route)
menu_page.route("**/PR_SAVE*", handle_route)

# ====================================================================
# Step 5: dialog handler
# ====================================================================
dialog_messages = []

def handle_dialog(dialog):
    msg = dialog.message
    dtype = dialog.type
    dialog_messages.append({"type": dtype, "message": msg, "time": time.time()})
    print(f"\n  [DIALOG {dtype}] {msg}")

    if dtype == "confirm" and "受款人尚未編輯" in msg:
        dialog.dismiss()  # 不去編輯，繼續存
    elif dtype == "confirm" and "受款人尚未輸入" in msg:
        dialog.dismiss()
    else:
        dialog.accept()

menu_page.on("dialog", handle_dialog)

# ====================================================================
# Step 6: 更新加總 + 存入前最終確認
# ====================================================================
print("\n" + "="*60)
print("Step 5: 更新加總值")
print("="*60)

# 觸發 APPP 和 APPA 加總
appy_frame.evaluate("""() => {
    try { if (typeof CHK_APPP === 'function') CHK_APPP(); } catch(e) {}
}""")
time.sleep(1)

# 手動觸發 APPA 加總（CHK_APPA 有 bug）
appy_frame.evaluate("""() => {
    try { parent.APPA.FORM1.SUM_LIST.click(); } catch(e) {}
}""")
time.sleep(1)

# 拷回 APPA 加總到 APPY
appy_frame.evaluate("""() => {
    try { FORM1.SUM_APPA.value = parent.APPA.FORM1.SUM_LIST.value; } catch(e) {}
}""")
time.sleep(0.5)

# 讀取三個加總
sums = appy_frame.evaluate("""() => ({
    budget: FORM1.SUM_LIST ? FORM1.SUM_LIST.value : '',
    items: FORM1.SUM_APPP ? FORM1.SUM_APPP.value : '',
    payee: FORM1.SUM_APPA ? FORM1.SUM_APPA.value : '',
})""")
print(f"  經費(SUM_LIST): {sums['budget']}")
print(f"  品名(SUM_APPP): {sums['items']}")
print(f"  受款人(SUM_APPA): {sums['payee']}")

# ====================================================================
# Step 7: 呼叫 SUM_ALERT() 存入
# ====================================================================
print("\n" + "="*60)
print("Step 6: 呼叫 SUM_ALERT() 存入")
print("="*60)

# 先做一次序列化預覽（不 submit）
print("  [預覽] 先攔截序列化結果...")
preview = appy_frame.evaluate("""() => {
    const origSubmit = parent.PS.FORM1.submit;
    let captured = null;
    parent.PS.FORM1.submit = function() {
        captured = {
            D_STR: parent.PS.FORM1.D_STR ? parent.PS.FORM1.D_STR.value : null,
            P_STR: parent.PS.FORM1.P_STR ? parent.PS.FORM1.P_STR.value : null,
            A_STR: parent.PS.FORM1.A_STR ? parent.PS.FORM1.A_STR.value : null,
        };
        // 不 submit - 只是預覽
    };
    const origAlert = window.alert;
    const origConfirm = window.confirm;
    window.alert = function(msg) { return; };
    window.confirm = function(msg) { return true; };

    try { SUM_ALERT(); } catch(e) { captured = captured || {}; captured.error = e.message; }

    parent.PS.FORM1.submit = origSubmit;
    window.alert = origAlert;
    window.confirm = origConfirm;
    return captured;
}""")

if preview:
    d = preview.get('D_STR') or ''
    p = preview.get('P_STR') or ''
    a = preview.get('A_STR') or ''
    print(f"  D_STR ({len(d)} chars): {d[:150]}")
    print(f"  P_STR ({len(p)} chars): {p[:150]}")
    print(f"  A_STR ({len(a)} chars): {a[:150]}")
    if preview.get('error'):
        print(f"  ERROR: {preview['error']}")

    # 重要：檢查 P_STR 裡的特殊字元 ◎ 和 ○
    if p:
        has_circle = '\u25ce' in p  # ◎
        has_circle2 = '\u25cb' in p  # ○
        print(f"  P_STR 包含 ◎(U+25CE): {has_circle}")
        print(f"  P_STR 包含 ○(U+25CB): {has_circle2}")
        # 印出每個字元的 Unicode code point
        unique_nonascii = set()
        for ch in p:
            if ord(ch) > 127:
                unique_nonascii.add(f"U+{ord(ch):04X} ({ch})")
        print(f"  P_STR 非 ASCII 字元: {unique_nonascii}")

    if a:
        unique_nonascii_a = set()
        for ch in a:
            if ord(ch) > 127:
                unique_nonascii_a.add(f"U+{ord(ch):04X} ({ch})")
        print(f"  A_STR 非 ASCII 字元: {unique_nonascii_a}")
else:
    print("  [WARN] 序列化預覽失敗！")

# 恢復 DD/QQ 到編輯經費狀態（SUM_ALERT 會改掉它們）
appy_frame.evaluate('() => { parent.DD.rows="*,0"; parent.QQ.cols="*,0,0"; }')
time.sleep(1)

# ── 再次驗證資料還在 ──
print("\n  存入前最終驗證...")
ad2, pd2, rd2 = verify_all_frames()
print(f"  APPY: amount={ad2['amount']}")
print(f"  APPP: {len(pd2['items'])} items")
print(f"  APPA: venname={rd2['venname']}, amount={rd2['amount']}")

# ── 真正存入 ──
print("\n  [!] 真正呼叫 SUM_ALERT() 存入...")
try:
    appy_frame.evaluate("SUM_ALERT();")
except Exception as e:
    print(f"  SUM_ALERT 錯誤: {e}")

# ====================================================================
# Step 8: 長時間等待 — 觀察對話框和網路回應
# ====================================================================
print("\n" + "="*60)
print("Step 7: 等待（最長 30 秒）")
print("="*60)

for sec in range(30):
    time.sleep(1)
    if (sec + 1) % 5 == 0:
        print(f"  已等待 {sec + 1} 秒... (dialog: {len(dialog_messages)}, HTTP: {len(captured_requests)})")

# ====================================================================
# Step 9: 結果匯總
# ====================================================================
print("\n" + "="*60)
print("結果匯總")
print("="*60)

# Dialog 訊息
print(f"\n  Dialog 訊息 ({len(dialog_messages)}):")
for d in dialog_messages:
    print(f"    [{d['type']}] {d['message']}")

# 攔截到的 HTTP 請求
print(f"\n  攔截到的 HTTP 請求 ({len(captured_requests)}):")
for i, req in enumerate(captured_requests):
    print(f"\n  Request {i+1}: {req['method']} {req['url'][-60:]}")
    print(f"    Content-Type: {req['content_type']}")
    print(f"    Text length: {req['body_text_length']}, Bytes length: {req['body_bytes_length']}")

    # 比較 UTF-8 和 Big5 解碼結果
    for key in ['D_STR', 'P_STR', 'A_STR']:
        utf8_val = req.get('parsed_utf8', {}).get(key, '')
        big5_val = req.get('parsed_big5', {}).get(key, '')
        raw_val = req.get('raw_hex_samples', {}).get(key, '')

        if utf8_val or big5_val or raw_val:
            print(f"\n    {key}:")
            print(f"      UTF-8: {utf8_val[:200]}")
            print(f"      Big5:  {big5_val[:200]}")
            # 比較兩者是否相同
            if utf8_val == big5_val:
                print(f"      (兩者相同 - 可能全是 ASCII)")
            else:
                print(f"      (兩者不同 - 有非 ASCII 字元，編碼問題！)")
                # 找出差異
                for j, (u, b) in enumerate(zip(utf8_val, big5_val)):
                    if u != b:
                        print(f"      第{j}字元不同: UTF8='{u}'(U+{ord(u):04X}) Big5='{b}'(U+{ord(b):04X})")
                        break

# PS frame 狀態
print("\n  PS frame 狀態:")
for f in menu_page.frames:
    if f.name == "PS" or "PR_SAVE" in f.url or "STD_SAVE" in f.url or "SAVE" in f.url.upper():
        print(f"    name={f.name} url={f.url[-80:]}")
        try:
            content = f.evaluate("document.body ? document.body.innerText.substring(0, 500) : 'no body'")
            print(f"    body: {content[:300]}")
        except Exception as e:
            print(f"    (read error: {e})")

# 截圖
menu_page.screenshot(path=f"{OUTPUT_DIR}/test_full_save.png", full_page=True)

# 儲存完整 debug
debug_data = {
    "ps_info": ps_info,
    "initial_appy": appy_data,
    "initial_appp": appp_data,
    "initial_appa": appa_data,
    "sums": sums,
    "serialization_preview": preview,
    "dialog_messages": dialog_messages,
    "captured_requests": [{
        "url": r["url"],
        "method": r["method"],
        "content_type": r["content_type"],
        "text_length": r["body_text_length"],
        "bytes_length": r["body_bytes_length"],
        "parsed_utf8": r.get("parsed_utf8", {}),
        "parsed_big5": r.get("parsed_big5", {}),
        "raw_hex_samples": r.get("raw_hex_samples", {}),
    } for r in captured_requests],
}
with open(f"{OUTPUT_DIR}/full_save_debug.json", "w", encoding="utf-8") as fout:
    json.dump(debug_data, fout, ensure_ascii=False, indent=2)

print(f"\n  Debug: {OUTPUT_DIR}/full_save_debug.json")
print(f"  截圖: {OUTPUT_DIR}/test_full_save.png")

# 清理
menu_page.unroute("**/STD_SAVE*")
menu_page.unroute("**/PR_SAVE*")
try:
    menu_page.remove_listener("dialog", handle_dialog)
except:
    pass

print("\n按 Enter 結束...")
try:
    input()
except (EOFError, KeyboardInterrupt):
    pass

browser.close()
pw.stop()
