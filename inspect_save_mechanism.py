"""Debug: 深入調查 SUM_ALERT() 存檔機制，找出為何 APPP/APPA 資料沒存到。

重點檢查：
1. SUM_ALERT() 的完整原始碼
2. PS frame (PR_SAVE_Q.asp) 的內容和 form action
3. 各 frame 的 FORM1 action 屬性
4. 存檔時是否需要 submit 多個 form
"""
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
    "vendor": "測試用-調查存檔機制",
    "amount": 100,
    "invoice_no": "TEST-SAVE",
    "items": [
        {"name": "測試品項A", "quantity": 1, "price": 100},
    ],
}

pw, browser, context = start_browser(headless=False)
menu_page = login(context)

# 導航到計畫請購表單
frames = navigate_to_expense_form(menu_page, use_project=True, plan_name="定位量測")

appy_frame = frames.get("appy")
appp_frame = frames.get("appp")
appa_frame = frames.get("appa")

print(f"\nFrames: appy={appy_frame is not None}, appp={appp_frame is not None}, appa={appa_frame is not None}")

# ============================================================
# 1. 檢查所有 frame 的 URL 和 FORM1 action
# ============================================================
print("\n=== Frame URLs and Form Actions ===")
for name, frame in frames.items():
    if frame:
        url = frame.url
        form_info = frame.evaluate("""() => {
            const forms = [];
            document.querySelectorAll('form').forEach(f => {
                forms.push({
                    name: f.name,
                    action: f.action,
                    method: f.method,
                    target: f.target,
                    enctype: f.enctype || '',
                    inputCount: f.querySelectorAll('input, select, textarea').length,
                });
            });
            return forms;
        }""")
        print(f"\n  [{name}] URL: {url}")
        for fi in form_info:
            print(f"    FORM name={fi['name']} action={fi['action']}")
            print(f"      method={fi['method']} target={fi['target']} inputs={fi['inputCount']}")

# ============================================================
# 2. 檢查 PS frame (存檔 handler)
# ============================================================
print("\n=== PS Frame (Save Handler) ===")
ps_frame = None
for f in menu_page.frames:
    if "PR_SAVE" in f.url or f.name == "PS":
        ps_frame = f
        print(f"  Found PS frame: name={f.name} url={f.url}")
        break

# Also look for it by name
if not ps_frame:
    for f in menu_page.frames:
        if f.name == "PS":
            ps_frame = f
            print(f"  Found PS frame by name: url={f.url}")
            break

if ps_frame:
    ps_content = ps_frame.evaluate("""() => {
        return {
            url: location.href,
            html: document.documentElement.outerHTML.substring(0, 3000),
            scripts: [...document.querySelectorAll('script')].map(s =>
                s.textContent.trim().substring(0, 1000)
            ),
            forms: [...document.querySelectorAll('form')].map(f => ({
                name: f.name, action: f.action, method: f.method, target: f.target,
                inputs: [...f.querySelectorAll('input')].map(inp => ({
                    name: inp.name, type: inp.type, value: inp.value.substring(0, 100)
                }))
            })),
        };
    }""")
    print(f"  PS URL: {ps_content.get('url')}")
    print(f"  PS HTML (first 500):\n{ps_content.get('html', '')[:500]}")
    print(f"  PS Forms: {json.dumps(ps_content.get('forms', []), ensure_ascii=False, indent=2)}")
    print(f"  PS Scripts: {len(ps_content.get('scripts', []))}")
    for i, s in enumerate(ps_content.get("scripts", [])):
        print(f"    Script {i} (first 300): {s[:300]}")
else:
    print("  PS frame NOT found!")
    # List all frames
    print("  All frames:")
    for f in menu_page.frames:
        print(f"    name='{f.name}' url={f.url[:100]}")

# ============================================================
# 3. 取得 APPY frame 的 SUM_ALERT() 原始碼
# ============================================================
print("\n=== SUM_ALERT() Source Code ===")
sum_alert_src = appy_frame.evaluate("""() => {
    const funcs = {};

    // SUM_ALERT
    if (typeof SUM_ALERT === 'function') {
        funcs.SUM_ALERT = SUM_ALERT.toString();
    }

    // CHK_APPP
    if (typeof CHK_APPP === 'function') {
        funcs.CHK_APPP = CHK_APPP.toString();
    }

    // CHK_APPA
    if (typeof CHK_APPA === 'function') {
        funcs.CHK_APPA = CHK_APPA.toString();
    }

    // SUM_SUM
    if (typeof SUM_SUM === 'function') {
        funcs.SUM_SUM = SUM_SUM.toString();
    }

    // PASS_APPP - might be the function that passes APPP data to APPY
    if (typeof PASS_APPP === 'function') {
        funcs.PASS_APPP = PASS_APPP.toString();
    }

    // PASS_APPA
    if (typeof PASS_APPA === 'function') {
        funcs.PASS_APPA = PASS_APPA.toString();
    }

    // PR_SAVE or related save functions
    if (typeof PR_SAVE === 'function') {
        funcs.PR_SAVE = PR_SAVE.toString();
    }

    // Check for SAVE_DATA or similar
    if (typeof SAVE_DATA === 'function') {
        funcs.SAVE_DATA = SAVE_DATA.toString();
    }

    // FORM1 action and target
    funcs.FORM1_action = FORM1.action;
    funcs.FORM1_target = FORM1.target;
    funcs.FORM1_method = FORM1.method;

    return funcs;
}""")

for fname, src in sum_alert_src.items():
    print(f"\n--- {fname} ---")
    print(src[:2000] if isinstance(src, str) else str(src))

# ============================================================
# 4. 取得 APPP frame 的相關函數
# ============================================================
print("\n=== APPP Frame Functions ===")
appp_funcs = appp_frame.evaluate("""() => {
    const funcs = {};

    // FORM1 details
    funcs.FORM1_action = FORM1.action;
    funcs.FORM1_target = FORM1.target;
    funcs.FORM1_method = FORM1.method;

    // Look for save-related functions
    const funcNames = ['SUM_SUM', 'CHK_SAVE', 'SAVE', 'PR_SAVE', 'SUBMIT_DATA'];
    funcNames.forEach(name => {
        try {
            if (typeof window[name] === 'function') {
                funcs[name] = window[name].toString().substring(0, 500);
            }
        } catch(e) {}
    });

    // Check if there are hidden inputs that store aggregated data
    funcs.hiddenInputs = [];
    document.querySelectorAll('input[type=hidden]').forEach(inp => {
        funcs.hiddenInputs.push({name: inp.name, value: inp.value.substring(0, 100)});
    });

    return funcs;
}""")

print(f"  FORM1 action: {appp_funcs.get('FORM1_action')}")
print(f"  FORM1 target: {appp_funcs.get('FORM1_target')}")
print(f"  FORM1 method: {appp_funcs.get('FORM1_method')}")
print(f"  Hidden inputs ({len(appp_funcs.get('hiddenInputs', []))}):")
for inp in appp_funcs.get("hiddenInputs", [])[:20]:
    print(f"    {inp['name']}: {inp['value']}")
for name, val in appp_funcs.items():
    if name.startswith("FORM1_") or name == "hiddenInputs":
        continue
    print(f"  {name}: {str(val)[:300]}")

# ============================================================
# 5. 取得 APPA frame 的相關函數
# ============================================================
print("\n=== APPA Frame Functions ===")
appa_funcs = appa_frame.evaluate("""() => {
    const funcs = {};

    funcs.FORM1_action = FORM1.action;
    funcs.FORM1_target = FORM1.target;
    funcs.FORM1_method = FORM1.method;

    const funcNames = ['SUM_SUM', 'CHK_SAVE', 'SAVE', 'PR_SAVE'];
    funcNames.forEach(name => {
        try {
            if (typeof window[name] === 'function') {
                funcs[name] = window[name].toString().substring(0, 500);
            }
        } catch(e) {}
    });

    funcs.hiddenInputs = [];
    document.querySelectorAll('input[type=hidden]').forEach(inp => {
        funcs.hiddenInputs.push({name: inp.name, value: inp.value.substring(0, 100)});
    });

    return funcs;
}""")

print(f"  FORM1 action: {appa_funcs.get('FORM1_action')}")
print(f"  FORM1 target: {appa_funcs.get('FORM1_target')}")
print(f"  FORM1 method: {appa_funcs.get('FORM1_method')}")
print(f"  Hidden inputs ({len(appa_funcs.get('hiddenInputs', []))}):")
for inp in appa_funcs.get("hiddenInputs", [])[:20]:
    print(f"    {inp['name']}: {inp['value']}")

# ============================================================
# 6. 檢查 APPY frame 的所有 JS 函數名稱（找 SAVE 相關）
# ============================================================
print("\n=== APPY All Function Names (save-related) ===")
all_funcs = appy_frame.evaluate("""() => {
    const names = [];
    for (const key of Object.keys(window)) {
        if (typeof window[key] === 'function') {
            const name = key.toLowerCase();
            if (name.includes('save') || name.includes('sum') ||
                name.includes('submit') || name.includes('alert') ||
                name.includes('pass') || name.includes('chk') ||
                name.includes('pr_') || name.includes('ps')) {
                names.push(key);
            }
        }
    }
    return names.sort();
}""")
print(f"  Functions: {all_funcs}")

# Get source of any interesting ones we haven't seen
for fn in all_funcs:
    if fn not in sum_alert_src:
        src = appy_frame.evaluate(f"typeof {fn} === 'function' ? {fn}.toString().substring(0, 800) : 'N/A'")
        if src != 'N/A' and len(src) > 10:
            print(f"\n  --- {fn} ---")
            print(f"  {src[:500]}")

# ============================================================
# Save all debug info
# ============================================================
debug_info = {
    "sum_alert_functions": sum_alert_src,
    "appp_functions": appp_funcs,
    "appa_functions": appa_funcs,
    "appy_save_functions": all_funcs,
}
with open(f"{OUTPUT_DIR}/save_mechanism_debug.json", "w", encoding="utf-8") as f:
    json.dump(debug_info, f, ensure_ascii=False, indent=2)

print(f"\n\nDebug info saved to {OUTPUT_DIR}/save_mechanism_debug.json")

browser.close()
pw.stop()
