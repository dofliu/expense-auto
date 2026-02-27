"""Debug: 查詢計畫請購中已存的記錄 + 查看 SUM_ALERT 行為。"""
import json, time, os
from form_filler import start_browser, login

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

pw, browser, context = start_browser(headless=False)
menu_page = login(context)

# Navigate to LIS4 (計畫請購查詢)
title_frame = menu_page.frame("TITLE")
title_frame.evaluate("""() => {
    try { LIS4(); } catch(e) {
        parent.FM.rows = "15%,*,0,0,0,0,0";
        parent.MAIN.location = '../BLANK_Q.asp?COM=NT';
        parent.TRAN.location = 'TRAN_Q.asp?COM=NT';
        parent.OT.location = '../SHAR_BUG_Q/SHAR_BUG_STR_Q.asp?COM=NT';
        window.location = 'DA_SerFun_Q.asp?COM=NT';
    }
}""")
time.sleep(3)

# Select 定位量測 plan
title_frame = menu_page.frame("TITLE")
title_frame.wait_for_load_state("networkidle", timeout=10000)

result = title_frame.evaluate("""() => {
    const sel = document.querySelector('select[name="BUGETNO"]');
    if (!sel) return {found: false};
    for (let i = 0; i < sel.options.length; i++) {
        if (sel.options[i].text.includes('定位量測')) {
            sel.selectedIndex = i;
            sel.dispatchEvent(new Event('change'));
            return {found: true, text: sel.options[i].text};
        }
    }
    return {found: false};
}""")
print(f"Plan: {result}")
time.sleep(1)

# Click "請購明細" (BUT3/SBT3) to see existing procurement records
title_frame.evaluate("""() => {
    parent.FM.rows = "15%,*,0,0,0,0,0";
    const link = document.querySelector('a[name="SBT3"]');
    if (link) link.click();
}""")
time.sleep(3)

# Check MAIN content
main_frame = menu_page.frame("MAIN")
if main_frame:
    main_frame.wait_for_load_state("networkidle", timeout=10000)
    print(f"MAIN URL: {main_frame.url}")

    # Take screenshot
    menu_page.screenshot(path=f"{OUTPUT_DIR}/project_records.png", full_page=True)
    print(f"Screenshot: {OUTPUT_DIR}/project_records.png")

    # Get table content
    content = main_frame.evaluate("""() => {
        const rows = [];
        document.querySelectorAll('table tr').forEach(tr => {
            const cells = [];
            tr.querySelectorAll('td, th').forEach(td => {
                cells.push(td.innerText.trim().substring(0, 80));
            });
            if (cells.length > 0) rows.push(cells);
        });
        return rows.slice(0, 30);
    }""")

    print(f"\nTable rows ({len(content)}):")
    for row in content:
        print(f"  {' | '.join(row[:8])}")

# Also try the "計畫清單" view (BUT1/SBT1) for budget overview
title_frame = menu_page.frame("TITLE")
title_frame.evaluate("""() => {
    parent.FM.rows = "15%,*,0,0,0,0,0";
    const link = document.querySelector('a[name="SBT1"]');
    if (link) link.click();
}""")
time.sleep(3)

main_frame = menu_page.frame("MAIN")
if main_frame:
    main_frame.wait_for_load_state("networkidle", timeout=10000)
    print(f"\nBudget view URL: {main_frame.url}")

    content2 = main_frame.evaluate("""() => {
        const rows = [];
        document.querySelectorAll('table tr').forEach(tr => {
            const cells = [];
            tr.querySelectorAll('td, th').forEach(td => {
                cells.push(td.innerText.trim().substring(0, 80));
            });
            if (cells.length > 0) rows.push(cells);
        });
        return rows.slice(0, 20);
    }""")

    print(f"Budget rows ({len(content2)}):")
    for row in content2:
        print(f"  {' | '.join(row[:8])}")

    menu_page.screenshot(path=f"{OUTPUT_DIR}/project_budget.png", full_page=True)

browser.close()
pw.stop()
