"""Debug: 取得完整 SUM_ALERT() 原始碼，重點看 D_STR / A_STR / P_STR 序列化。"""
import json, time, os
from form_filler import start_browser, login, navigate_to_expense_form
from config import OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

pw, browser, context = start_browser(headless=False)
menu_page = login(context)

frames = navigate_to_expense_form(menu_page, use_project=True, plan_name="定位量測")
appy_frame = frames.get("appy")
appp_frame = frames.get("appp")
appa_frame = frames.get("appa")

# ============================================================
# 1. 完整 SUM_ALERT() — 分段取得
# ============================================================
print("\n=== FULL SUM_ALERT() Source ===")
full_src = appy_frame.evaluate("SUM_ALERT.toString()")
print(full_src)

# Save full source
with open(f"{OUTPUT_DIR}/sum_alert_full.js", "w", encoding="utf-8") as f:
    f.write(full_src)

# ============================================================
# 2. 看 APPY frame 有哪些 D_STR 相關函數
# ============================================================
print("\n\n=== D_STR / A_STR / P_STR related ===")
str_funcs = appy_frame.evaluate("""() => {
    const result = {};
    // Search for functions that build D_STR, A_STR, P_STR
    for (const key of Object.keys(window)) {
        if (typeof window[key] === 'function') {
            const src = window[key].toString();
            if (src.includes('D_STR') || src.includes('A_STR') || src.includes('P_STR')) {
                result[key] = src.substring(0, 2000);
            }
        }
    }
    return result;
}""")
for name, src in str_funcs.items():
    print(f"\n--- {name} ---")
    print(src)

# ============================================================
# 3. APPP frame SUM_SUM 完整版
# ============================================================
print("\n\n=== APPP SUM_SUM ===")
appp_sum = appp_frame.evaluate("SUM_SUM.toString()")
print(appp_sum[:2000])

# ============================================================
# 4. APPA frame SUM_SUM
# ============================================================
print("\n\n=== APPA SUM_SUM ===")
try:
    appa_sum = appa_frame.evaluate("SUM_SUM.toString()")
    print(appa_sum[:2000])
except:
    print("SUM_SUM not found in APPA")

# ============================================================
# 5. APPP FORM6 inputs (the 119-input form)
# ============================================================
print("\n\n=== APPP FORM6 sample inputs ===")
form6_info = appp_frame.evaluate("""() => {
    const f6 = document.forms['FORM6'];
    if (!f6) return 'FORM6 not found';
    const inputs = [...f6.querySelectorAll('input, select, textarea')];
    return {
        action: f6.action,
        target: f6.target,
        method: f6.method,
        count: inputs.length,
        sample: inputs.slice(0, 30).map(inp => ({
            tag: inp.tagName,
            name: inp.name,
            type: inp.type || '',
            value: (inp.value || '').substring(0, 50),
        }))
    };
}""")
if isinstance(form6_info, dict):
    print(f"  Action: {form6_info.get('action')}")
    print(f"  Count: {form6_info.get('count')}")
    for inp in form6_info.get("sample", []):
        print(f"    {inp['tag']} name={inp['name']} type={inp['type']} val={inp['value']}")
else:
    print(form6_info)

# ============================================================
# 6. 實際 FORM1 中的 APPP 品名欄位 (用 names 列舉)
# ============================================================
print("\n\n=== APPP FORM1 actual named elements ===")
appp_form_elements = appp_frame.evaluate("""() => {
    const result = [];
    // FORM1 named elements
    const f = document.forms['FORM1'];
    if (!f) return ['FORM1 not found'];

    // Get named elements
    for (let i = 0; i < f.elements.length; i++) {
        const el = f.elements[i];
        if (el.name) {
            result.push({
                name: el.name,
                tag: el.tagName,
                type: el.type || '',
                value: (el.value || '').substring(0, 50),
            });
        }
        if (result.length >= 50) break;
    }
    return result;
}""")
print(f"  Elements: {len(appp_form_elements)}")
for el in appp_form_elements[:30]:
    if isinstance(el, dict):
        print(f"    {el['name']}: {el['tag']} type={el['type']} val='{el['value']}'")

# ============================================================
# 7. Check APPY FORM1 elements - including SAMPLENO and hidden fields
# ============================================================
print("\n\n=== APPY FORM1 named elements ===")
appy_form_elements = appy_frame.evaluate("""() => {
    const result = [];
    const f = document.forms['FORM1'];
    if (!f) return ['FORM1 not found'];
    for (let i = 0; i < f.elements.length; i++) {
        const el = f.elements[i];
        if (el.name) {
            result.push({
                name: el.name,
                tag: el.tagName,
                type: el.type || '',
                value: (el.value || '').substring(0, 80),
            });
        }
        if (result.length >= 60) break;
    }
    return result;
}""")
print(f"  Elements: {len(appy_form_elements)}")
for el in appy_form_elements[:50]:
    if isinstance(el, dict):
        print(f"    {el['name']}: {el['tag']} type={el['type']} val='{el['value']}'")

browser.close()
pw.stop()
