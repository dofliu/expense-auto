"""測試：找到編輯按鈕，來回切換確認資料，然後存入。

流程：
1. 登入 → 導航到計畫請購表單
2. 填寫三個區塊（APPY/APPP/APPA）
3. 找到「編輯經費」「編輯品名」「編輯受款人」按鈕
4. 來回點選，每次驗證資料
5. 按存入 + 等待對話框
"""
import json, time, os
from form_filler import (
    start_browser, login, navigate_to_expense_form,
    fill_appy_frame, fill_appa_frame, fill_expense_form,
    _js_escape, _roc_date, _idate_format, generate_receipt_no,
)
from config import OUTPUT_DIR, APPP_FIELDS

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 測試資料 ──
receipt_data = {
    "date": "2026-02-11",
    "vendor": "測試商店-按鈕測試",
    "amount": 120,
    "invoice_no": "",
    "items": [
        {"name": "測試品項A", "quantity": 1, "price": 80},
        {"name": "測試品項B", "quantity": 1, "price": 40},
    ],
}

pw, browser, context = start_browser(headless=False)
menu_page = login(context)

# ── 導航 ──
frames = navigate_to_expense_form(menu_page, use_project=True, plan_name="定位量測")
appy_frame = frames.get("appy")
appp_frame = frames.get("appp")
appa_frame = frames.get("appa")

print(f"\nFrames: appy={appy_frame is not None}, appp={appp_frame is not None}, appa={appa_frame is not None}")

# ── 填寫三個區塊（不自動存入）──
fill_expense_form(
    frames, receipt_data,
    menu_page=menu_page,
    context=context,
    plan_name="定位量測",
    receipt_seq=99,
    auto_save=False,  # 不自動存入！
)

# ====================================================================
# Step 1: 找到編輯按鈕（可能在 APPY frame 或父層 frameset）
# ====================================================================
print("\n" + "="*60)
print("Step 1: 尋找編輯按鈕")
print("="*60)

# 先在 APPY frame 找
appy_buttons = appy_frame.evaluate("""() => {
    const buttons = [];
    // input[type=button]
    document.querySelectorAll('input[type=button], input[type=submit]').forEach(b => {
        buttons.push({
            tag: 'INPUT',
            name: b.name,
            value: b.value,
            onclick: (b.getAttribute('onclick') || '').substring(0, 200),
            type: b.type,
        });
    });
    // <a> links
    document.querySelectorAll('a').forEach(a => {
        const text = a.innerText.trim();
        if (text.includes('編輯') || text.includes('存入') || text.includes('取消')) {
            buttons.push({
                tag: 'A',
                name: a.name || '',
                value: text,
                onclick: (a.getAttribute('onclick') || '').substring(0, 200),
                href: (a.href || '').substring(0, 200),
            });
        }
    });
    // <button>
    document.querySelectorAll('button').forEach(b => {
        buttons.push({
            tag: 'BUTTON',
            name: b.name || '',
            value: b.innerText.trim(),
            onclick: (b.getAttribute('onclick') || '').substring(0, 200),
        });
    });
    return buttons;
}""")

print(f"\n  APPY frame 按鈕 ({len(appy_buttons)}):")
for b in appy_buttons:
    print(f"    [{b['tag']}] name='{b.get('name','')}' value='{b.get('value','')}' onclick='{b.get('onclick','')}'")

# 在 APPP frame 找
appp_buttons = appp_frame.evaluate("""() => {
    const buttons = [];
    document.querySelectorAll('input[type=button], input[type=submit]').forEach(b => {
        buttons.push({
            tag: 'INPUT',
            name: b.name,
            value: b.value,
            onclick: (b.getAttribute('onclick') || '').substring(0, 200),
        });
    });
    document.querySelectorAll('a').forEach(a => {
        const text = a.innerText.trim();
        if (text) {
            buttons.push({
                tag: 'A',
                name: a.name || '',
                value: text,
                onclick: (a.getAttribute('onclick') || '').substring(0, 200),
                href: (a.href || '').substring(0, 100),
            });
        }
    });
    return buttons;
}""")

print(f"\n  APPP frame 按鈕 ({len(appp_buttons)}):")
for b in appp_buttons:
    print(f"    [{b['tag']}] name='{b.get('name','')}' value='{b.get('value','')}' onclick='{b.get('onclick','')}'")

# 在 APPA frame 找
appa_buttons = appa_frame.evaluate("""() => {
    const buttons = [];
    document.querySelectorAll('input[type=button], input[type=submit]').forEach(b => {
        buttons.push({
            tag: 'INPUT',
            name: b.name,
            value: b.value,
            onclick: (b.getAttribute('onclick') || '').substring(0, 200),
        });
    });
    return buttons;
}""")

print(f"\n  APPA frame 按鈕 ({len(appa_buttons)}):")
for b in appa_buttons:
    print(f"    [{b['tag']}] name='{b.get('name','')}' value='{b.get('value','')}' onclick='{b.get('onclick','')}'")

# 找 frameset 容器（STD_APPY_FRM_Q）
print("\n  搜尋 STD_APPY_FRM_Q frameset...")
frm_frame = None
for f in menu_page.frames:
    if "STD_APPY_FRM" in f.url:
        frm_frame = f
        print(f"    找到 FRM frame: {f.url[:100]}")
        break

if frm_frame:
    frm_buttons = frm_frame.evaluate("""() => {
        const buttons = [];
        document.querySelectorAll('input[type=button], a, button').forEach(el => {
            buttons.push({
                tag: el.tagName,
                name: el.name || '',
                value: (el.value || el.innerText || '').trim().substring(0, 50),
                onclick: (el.getAttribute('onclick') || '').substring(0, 200),
            });
        });
        return buttons;
    }""")
    print(f"  FRM frame 按鈕 ({len(frm_buttons)}):")
    for b in frm_buttons:
        print(f"    [{b['tag']}] value='{b['value']}' onclick='{b['onclick']}'")

# 在所有 frame 搜尋「編輯」「存入」按鈕
print("\n  搜尋所有 frame 中的「編輯/存入」按鈕...")
for f in menu_page.frames:
    result = f.evaluate("""() => {
        const hits = [];
        document.querySelectorAll('input[type=button], a, button').forEach(el => {
            const text = (el.value || el.innerText || '').trim();
            if (text.includes('編輯') || text.includes('存入') || text.includes('取消')
                || text.includes('加總') || text.includes('SUM')) {
                hits.push({
                    tag: el.tagName,
                    text: text.substring(0, 50),
                    onclick: (el.getAttribute('onclick') || '').substring(0, 300),
                    name: el.name || '',
                });
            }
        });
        return hits;
    }""")
    if result:
        name = f.name or '(unnamed)'
        url_short = f.url.split('/')[-1][:50] if f.url else '?'
        print(f"\n    Frame: {name} ({url_short})")
        for h in result:
            print(f"      [{h['tag']}] '{h['text']}' name='{h['name']}' onclick='{h['onclick']}'")

# ====================================================================
# Step 2: 讀取表單 SUM_ALERT 完整原始碼（特別是 D_STR/P_STR/A_STR 序列化部分）
# ====================================================================
print("\n" + "="*60)
print("Step 2: SUM_ALERT 完整原始碼")
print("="*60)

full_src = appy_frame.evaluate("SUM_ALERT.toString()")
with open(f"{OUTPUT_DIR}/sum_alert_full.js", "w", encoding="utf-8") as f:
    f.write(full_src)
print(f"  已存: {OUTPUT_DIR}/sum_alert_full.js ({len(full_src)} chars)")

# 印出關鍵的 P_STR 和 A_STR 序列化部分
for keyword in ['P_STR', 'A_STR', 'D_STR', 'PRODUCT', 'VENNAME', 'submit']:
    idx = full_src.find(keyword)
    if idx >= 0:
        start = max(0, idx - 50)
        end = min(len(full_src), idx + 200)
        print(f"\n  --- 含 '{keyword}' 的段落 (位置 {idx}) ---")
        print(f"  ...{full_src[start:end]}...")

# ====================================================================
# Step 3: 截圖留存
# ====================================================================
print("\n  截圖中...")
menu_page.screenshot(path=f"{OUTPUT_DIR}/test_edit_buttons_filled.png", full_page=True)
print(f"  截圖: {OUTPUT_DIR}/test_edit_buttons_filled.png")

# ====================================================================
# Step 4: 驗證填入的資料（在嘗試按鈕前）
# ====================================================================
print("\n" + "="*60)
print("Step 3: 驗證目前三個區塊的資料")
print("="*60)

# APPY
appy_data = appy_frame.evaluate("""() => ({
    bugetno: FORM1.BUGETNO_1 ? FORM1.BUGETNO_1.value : '',
    bugcode: FORM1.BUGCODE_1 ? FORM1.BUGCODE_1.value : '',
    amount: FORM1.D_AMOUNT_1 ? FORM1.D_AMOUNT_1.value : '',
    sum_list: FORM1.SUM_LIST ? FORM1.SUM_LIST.value : '',
})""")
print(f"  APPY: bugetno={appy_data['bugetno']}, bugcode={appy_data['bugcode']}, amount={appy_data['amount']}")

# APPP
appp_data = appp_frame.evaluate("""() => {
    const items = [];
    for (let i = 1; i <= 15; i++) {
        const p = document.querySelector('input[name="PRODUCT_' + i + '"]');
        const a = document.querySelector('input[name="AMOUNT_' + i + '"]');
        if (p && p.value) {
            items.push({
                row: i,
                product: p.value,
                amount: a ? a.value : '',
            });
        }
    }
    const content = document.querySelector('textarea[name="CONTENT"]');
    return {
        items: items,
        content: content ? content.value : '',
        sum: FORM1.SUM_LIST ? FORM1.SUM_LIST.value : '',
    };
}""")
print(f"  APPP: 用途說明='{appp_data['content']}'")
print(f"  APPP: SUM_LIST={appp_data['sum']}")
for item in appp_data.get("items", []):
    print(f"    品項{item['row']}: {item['product']} = {item['amount']}")

# APPA
appa_data = appa_frame.evaluate("""() => ({
    venname: FORM1.VENNAME_1 ? FORM1.VENNAME_1.value : '',
    vendorid_s: FORM1.VENDORID_S_1 ? FORM1.VENDORID_S_1.value : '',
    vendorid: FORM1.VENDORID_1 ? FORM1.VENDORID_1.value : '',
    bankno: FORM1.BANKNO_1 ? FORM1.BANKNO_1.value : '',
    account: FORM1.ACCOUNT_1 ? FORM1.ACCOUNT_1.value : '',
    amount: FORM1.AMOUNT_1 ? FORM1.AMOUNT_1.value : '',
    invoiceno: FORM1.INVOICENO_1 ? FORM1.INVOICENO_1.value : '',
    idate: FORM1.IDATE_1 ? FORM1.IDATE_1.value : '',
    paykind: FORM1.PAYKIND_1 ? FORM1.PAYKIND_1.value : '',
    sum: typeof SUM_LIST !== 'undefined' ? (FORM1.SUM_LIST ? FORM1.SUM_LIST.value : '') : 'N/A',
})""")
print(f"  APPA: venname={appa_data['venname']}, bankno={appa_data['bankno']}")
print(f"  APPA: amount={appa_data['amount']}, invoiceno={appa_data['invoiceno']}")
print(f"  APPA: vendorid_s={appa_data['vendorid_s']}, vendorid={appa_data['vendorid'][:30]}...")
print(f"  APPA: idate={appa_data['idate']}, paykind={appa_data['paykind']}")

# ====================================================================
# Step 4: 手動呼叫 SUM_ALERT 但不 submit，只看 D_STR / P_STR / A_STR
# ====================================================================
print("\n" + "="*60)
print("Step 4: 測試 SUM_ALERT 序列化（攔截 submit）")
print("="*60)

# Hook submit to prevent actual submission, just capture data
serialized = appy_frame.evaluate("""() => {
    // 暫時替換 submit 為 no-op
    const origSubmit = parent.PS.FORM1.submit;
    let captured = null;
    parent.PS.FORM1.submit = function() {
        captured = {
            D_STR: parent.PS.FORM1.D_STR ? parent.PS.FORM1.D_STR.value : null,
            P_STR: parent.PS.FORM1.P_STR ? parent.PS.FORM1.P_STR.value : null,
            A_STR: parent.PS.FORM1.A_STR ? parent.PS.FORM1.A_STR.value : null,
            ABSTRACT: parent.PS.FORM1.ABSTRACT ? parent.PS.FORM1.ABSTRACT.value : null,
            IsNew: parent.PS.FORM1.IsNew ? parent.PS.FORM1.IsNew.value : null,
            APPYSET: parent.PS.FORM1.APPYSET ? parent.PS.FORM1.APPYSET.value : null,
        };
        // 不真正 submit
    };

    // 自動 accept 所有 dialog
    const origAlert = window.alert;
    const origConfirm = window.confirm;
    const dialogs = [];
    window.alert = function(msg) { dialogs.push({type:'alert', msg:msg}); };
    window.confirm = function(msg) { dialogs.push({type:'confirm', msg:msg}); return true; };

    try {
        SUM_ALERT();
    } catch(e) {
        captured = captured || {};
        captured.error = e.message;
    }

    // 恢復
    parent.PS.FORM1.submit = origSubmit;
    window.alert = origAlert;
    window.confirm = origConfirm;

    return {
        captured: captured,
        dialogs: dialogs,
    };
}""")

print(f"\n  Dialogs: {json.dumps(serialized.get('dialogs', []), ensure_ascii=False)}")

cap = serialized.get("captured", {}) or {}
if cap.get("error"):
    print(f"  ERROR: {cap['error']}")

print(f"\n  D_STR ({len(str(cap.get('D_STR', '') or ''))} chars):")
d_str = cap.get('D_STR', '') or ''
print(f"    {d_str[:300]}...")

print(f"\n  P_STR ({len(str(cap.get('P_STR', '') or ''))} chars):")
p_str = cap.get('P_STR', '') or ''
print(f"    {p_str[:300]}...")

print(f"\n  A_STR ({len(str(cap.get('A_STR', '') or ''))} chars):")
a_str = cap.get('A_STR', '') or ''
print(f"    {a_str[:300]}...")

print(f"\n  ABSTRACT: {cap.get('ABSTRACT', '')}")
print(f"  IsNew: {cap.get('IsNew', '')}")
print(f"  APPYSET: {cap.get('APPYSET', '')}")

# Save full debug info
with open(f"{OUTPUT_DIR}/edit_buttons_debug.json", "w", encoding="utf-8") as f:
    json.dump({
        "appy_buttons": appy_buttons,
        "appp_buttons": appp_buttons,
        "appa_buttons": appa_buttons,
        "appy_data": appy_data,
        "appp_data": appp_data,
        "appa_data": appa_data,
        "serialized": {
            "D_STR": d_str,
            "P_STR": p_str,
            "A_STR": a_str,
            "dialogs": serialized.get("dialogs", []),
        },
    }, f, ensure_ascii=False, indent=2)

print(f"\n  Debug: {OUTPUT_DIR}/edit_buttons_debug.json")
print("\n瀏覽器保持開啟，方便手動檢查。按 Ctrl+C 結束。")

try:
    input("按 Enter 結束...")
except (EOFError, KeyboardInterrupt):
    pass

browser.close()
pw.stop()
