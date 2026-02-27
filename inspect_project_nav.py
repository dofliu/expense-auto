"""Debug: inspect TITLE frame after LIS4 navigation (計畫請購查詢)."""
import json, time, os
from form_filler import start_browser, login

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

pw, browser, context = start_browser(headless=False)
menu_page = login(context)

# Navigate to LIS4 (計畫請購查詢) - NOT LIS3!
title_frame = menu_page.frame("TITLE")

# First try direct LIS4()
try:
    title_frame.evaluate("""() => {
        try {
            LIS4();
        } catch(e) {
            // Fallback: manually navigate like LIS4 should
            parent.FM.rows = "15%,*,0,0,0,0,0";
            parent.MAIN.location = '../BLANK_Q.asp?COM=NT';
            parent.TRAN.location = 'TRAN_Q.asp?COM=NT';
            parent.OT.location = '../SHAR_BUG_Q/SHAR_BUG_STR_Q.asp?COM=NT';
            window.location = 'DA_SerFun_Q.asp?COM=NT';
        }
    }""")
except Exception as e:
    print(f"LIS4 error: {e}")
time.sleep(3)

# Re-get TITLE frame
title_frame = menu_page.frame("TITLE")
title_frame.wait_for_load_state("networkidle", timeout=10000)

# Dump everything
info = title_frame.evaluate(r"""() => {
    const result = {};

    // URL
    result.url = window.location.href;

    // All select elements
    result.selects = [];
    document.querySelectorAll('select').forEach(sel => {
        result.selects.push({
            name: sel.name,
            id: sel.id,
            options: [...sel.options].map(o => ({v: o.value, t: o.text}))
        });
    });

    // All links
    result.links = [];
    document.querySelectorAll('a').forEach(a => {
        result.links.push({
            name: a.name,
            text: (a.innerText || '').trim(),
            href: a.href,
            onclick: a.getAttribute('onclick') || '',
            visible: a.offsetParent !== null
        });
    });

    // All buttons
    result.buttons = [];
    document.querySelectorAll('input[type=button], input[type=submit], button').forEach(b => {
        result.buttons.push({
            name: b.name,
            value: b.value,
            type: b.type,
            onclick: b.getAttribute('onclick') || ''
        });
    });

    // Forms
    result.forms = [];
    document.querySelectorAll('form').forEach(f => {
        result.forms.push({name: f.name, action: f.action});
    });

    // Function names
    result.functions = [];
    document.querySelectorAll('script').forEach(s => {
        const matches = (s.textContent || '').match(/function\s+\w+/g);
        if (matches) result.functions.push(...matches);
    });

    // Open/aBT functions source
    result.abt_sources = {};
    for (let i = 1; i <= 9; i++) {
        const fn = window['openaBT' + i];
        if (fn) result.abt_sources['openaBT' + i] = fn.toString();
    }

    return result;
}""")

with open(f"{OUTPUT_DIR}/project_lis4_debug.json", "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=2)

print(f"URL: {info.get('url')}")
print(f"\nSelects ({len(info.get('selects', []))}):")
for sel in info.get("selects", []):
    print(f"  {sel['name']}: {len(sel['options'])} options")
    for o in sel["options"][:15]:
        print(f"    [{o['v']}] {o['t']}")

print(f"\nButtons ({len(info.get('buttons', []))}):")
for b in info.get("buttons", []):
    print(f"  [{b['name']}] {b['value']}  onclick={b['onclick'][:80]}")

print(f"\nLinks with name ({sum(1 for l in info.get('links',[]) if l['name'])}):")
for l in info.get("links", []):
    if l["name"]:
        print(f"  [{l['name']}] text={l['text'][:20]}  onclick={l['onclick'][:60]}")

print(f"\naBT sources: {list(info.get('abt_sources', {}).keys())}")

browser.close()
pw.stop()
