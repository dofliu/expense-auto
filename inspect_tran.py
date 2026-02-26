"""深入分析 TRAN frame 和 budget data 載入流程。"""

import json
import time
from form_filler import start_browser, login, navigate_to_expense_form
from config import OUTPUT_DIR


def inspect_tran():
    pw, browser, context = start_browser(headless=True)

    try:
        menu_page = login(context)
        frames = navigate_to_expense_form(menu_page)

        # 先等久一點讓所有 frames 載入
        print("  等待 5 秒讓所有 frame 載入...")
        time.sleep(5)

        results = {}

        # 1. 檢查 TRAN frame
        tran_frame = None
        for f in menu_page.frames:
            if f.name == "TRAN":
                tran_frame = f
                break

        if tran_frame:
            tran_data = tran_frame.evaluate("""() => {
                const allForms = [...document.querySelectorAll('form')].map(f => ({
                    name: f.name || f.id || '',
                    action: f.action || '',
                    method: f.method || '',
                    elements: [...f.querySelectorAll('input,select,textarea')].map(i => ({
                        name: i.name,
                        type: i.type || '',
                        valueLen: (i.value || '').length,
                        valuePeek: (i.value || '').substring(0, 300),
                    })),
                }));
                return {
                    url: location.href,
                    forms: allForms,
                    bodyLen: document.body?.innerHTML?.length || 0,
                    bodyText: (document.body?.innerText || '').substring(0, 1000),
                };
            }""")
            results["tran_frame"] = tran_data
            print(f"\n=== TRAN frame (url: {tran_data['url']}) ===")
            print(f"  Body length: {tran_data['bodyLen']}")
            for form in tran_data['forms']:
                print(f"\n  Form: name={form['name']!r} action={form['action'][-50:]}")
                for el in form['elements']:
                    print(f"    {el['name']:25s}  type={el['type']:10s}  valueLen={el['valueLen']:5d}  peek={el['valuePeek'][:80]!r}")
        else:
            results["tran_frame"] = "NOT FOUND"

        # 2. 檢查 APPY frame 的 F1 按鈕和 onload 行為
        appy_frame = frames.get("appy")
        if appy_frame:
            appy_f1 = appy_frame.evaluate("""() => {
                const f1 = document.querySelector('input[name="F1"]');
                if (!f1) return {error: "F1 not found"};
                return {
                    name: f1.name,
                    type: f1.type,
                    value: f1.value,
                    onclick: f1.getAttribute('onclick') || '',
                    formAction: f1.form?.action || '',
                };
            }""")
            results["appy_f1"] = appy_f1
            print(f"\n=== APPY F1 button ===")
            print(f"  {json.dumps(appy_f1, indent=2)}")

            # 看 body onload
            appy_onload = appy_frame.evaluate("""() => {
                return {
                    bodyOnload: document.body?.getAttribute('onload') || '',
                    bodyOnunload: document.body?.getAttribute('onunload') || '',
                };
            }""")
            results["appy_onload"] = appy_onload
            print(f"\n=== APPY body events ===")
            print(f"  onload: {appy_onload['bodyOnload'][:200]}")

        # 3. 再次等 5 秒後重新檢查 TRAN
        print("\n  再等 5 秒...")
        time.sleep(5)

        if tran_frame:
            tran_data2 = tran_frame.evaluate("""() => {
                const allForms = [...document.querySelectorAll('form')].map(f => ({
                    name: f.name || f.id || '',
                    elements: [...f.querySelectorAll('input')].map(i => ({
                        name: i.name,
                        valueLen: (i.value || '').length,
                        valuePeek: (i.value || '').substring(0, 300),
                    })),
                }));
                return {
                    url: location.href,
                    forms: allForms,
                };
            }""")
            results["tran_frame_after_wait"] = tran_data2
            print(f"\n=== TRAN frame (after 10s wait) ===")
            for form in tran_data2['forms']:
                print(f"  Form: {form['name']!r}")
                for el in form['elements']:
                    if el['valueLen'] > 2:
                        print(f"    {el['name']:25s}  valueLen={el['valueLen']:5d}  peek={el['valuePeek'][:80]!r}")

        # 4. 檢查 BUGETNO_1 在等待後是否有更多選項
        if appy_frame:
            bugetno_after = appy_frame.evaluate("""() => {
                const sel = document.querySelector('select[name="BUGETNO_1"]');
                if (!sel) return {error: 'not found'};
                return {
                    length: sel.options.length,
                    options: [...sel.options].map(o => ({
                        value: o.value,
                        text: o.text,
                    })),
                };
            }""")
            results["bugetno_after_wait"] = bugetno_after
            print(f"\n=== BUGETNO_1 after wait ({bugetno_after.get('length', '?')} options) ===")
            if 'options' in bugetno_after:
                for opt in bugetno_after['options']:
                    print(f"  value={opt['value']!r:20s}  text={opt['text']}")

        with open(f"{OUTPUT_DIR}/tran_data.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\nResults saved to {OUTPUT_DIR}/tran_data.json")

    finally:
        browser.close()
        pw.stop()


if __name__ == "__main__":
    inspect_tran()
