"""Debug: 調查銀行帳戶彈窗 HTML，找到正確的點擊目標。"""
import json, time, os
from form_filler import (
    start_browser, login, navigate_to_expense_form,
    _js_escape, _idate_format, generate_receipt_no,
)
from config import PAYEE_CODE, BANK_KEYWORD, OUTPUT_DIR

os.makedirs(OUTPUT_DIR, exist_ok=True)

pw, browser, context = start_browser(headless=False)
menu_page = login(context)

# 導航到表單
frames = navigate_to_expense_form(menu_page, use_project=True, plan_name="定位量測")
appa_frame = frames.get("appa")

# 基本 APPA 填入
appa_frame.evaluate("""() => {
    FORM1.PROX_1.checked = true;
    FORM1.PAYKIND_1.value = "2";
    FORM1.INVOICENO_1.value = "TEST001";
    FORM1.IDATE_1.value = "1150211";
    FORM1.VENDORID_S_1.value = "56006";
    if (typeof STAR_ID_1 === 'function') STAR_ID_1();
}""")
time.sleep(1)

# 觸發 CHK_P_1() 並捕捉彈窗
print("\n=== Triggering CHK_P_1() ===")
try:
    with context.expect_page(timeout=15000) as popup_info:
        appa_frame.evaluate("CHK_P_1();")
        time.sleep(3)

    popup = popup_info.value
    popup.wait_for_load_state("networkidle", timeout=10000)
    print(f"Popup URL: {popup.url}")
    print(f"Popup title: {popup.title()}")

    # 取得完整 HTML
    html = popup.content()
    with open(f"{OUTPUT_DIR}/bank_popup.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Popup HTML saved: {OUTPUT_DIR}/bank_popup.html")

    # 取得頁面結構
    structure = popup.evaluate("""() => {
        const result = {};

        // All links
        result.links = [];
        document.querySelectorAll('a').forEach(a => {
            result.links.push({
                text: (a.innerText || '').trim().substring(0, 100),
                href: a.href,
                onclick: a.getAttribute('onclick') || '',
                name: a.name || '',
            });
        });

        // All forms
        result.forms = [];
        document.querySelectorAll('form').forEach(f => {
            result.forms.push({name: f.name, action: f.action, method: f.method});
        });

        // All input buttons
        result.buttons = [];
        document.querySelectorAll('input[type=button], input[type=submit]').forEach(b => {
            result.buttons.push({
                name: b.name, value: b.value, onclick: b.getAttribute('onclick') || ''
            });
        });

        // All table rows with content
        result.rows = [];
        document.querySelectorAll('tr').forEach(tr => {
            const cells = [];
            tr.querySelectorAll('td').forEach(td => {
                cells.push({
                    text: td.innerText.trim().substring(0, 80),
                    html: td.innerHTML.substring(0, 200),
                });
            });
            if (cells.length > 0 && cells.some(c => c.text)) {
                result.rows.push(cells);
            }
        });

        // Body text
        result.bodyText = document.body.innerText.substring(0, 2000);

        // Scripts
        result.scripts = [];
        document.querySelectorAll('script').forEach(s => {
            const src = s.textContent.trim();
            if (src) result.scripts.push(src.substring(0, 500));
        });

        return result;
    }""")

    with open(f"{OUTPUT_DIR}/bank_popup_structure.json", "w", encoding="utf-8") as f:
        json.dump(structure, f, ensure_ascii=False, indent=2)

    print(f"\nLinks ({len(structure.get('links', []))}):")
    for l in structure.get("links", []):
        print(f"  text={l['text'][:40]}  onclick={l['onclick'][:80]}  href={l['href'][:80]}")

    print(f"\nButtons ({len(structure.get('buttons', []))}):")
    for b in structure.get("buttons", []):
        print(f"  [{b['name']}] {b['value']}  onclick={b['onclick'][:80]}")

    print(f"\nTable rows ({len(structure.get('rows', []))}):")
    for row in structure.get("rows", []):
        texts = [c['text'][:30] for c in row]
        print(f"  {' | '.join(texts)}")

    print(f"\nBody text (first 500 chars):")
    print(structure.get("bodyText", "")[:500])

    # Don't click yet - just inspect
    popup.screenshot(path=f"{OUTPUT_DIR}/bank_popup.png")
    print(f"\nScreenshot: {OUTPUT_DIR}/bank_popup.png")

except Exception as e:
    print(f"No popup appeared: {e}")

    # Check CK_VN frame directly
    print("\nChecking CK_VN frame...")
    for f in menu_page.frames:
        if "CK_VN" in f.name or "SEAR_VENDORID" in f.url or "CK_VN" in f.url:
            print(f"  Found frame: {f.name} -> {f.url}")

    # Check if APPA was filled directly (single account case)
    time.sleep(3)
    vals = appa_frame.evaluate("""() => ({
        venname: FORM1.VENNAME_1.value,
        bankno: FORM1.BANKNO_1.value,
        account: FORM1.ACCOUNT_1.value,
    })""")
    print(f"  APPA values: {vals}")

browser.close()
pw.stop()
