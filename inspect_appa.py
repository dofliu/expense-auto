"""深入分析 APPA frame（受款人編輯）的完整欄位結構。

目標：取得所有表單欄位 name、代墊 checkbox、日期欄位、金額欄位、
      查受款人按鈕 onclick 行為、填入收據按鈕行為等。
"""

import json
import time
from form_filler import start_browser, login, navigate_to_expense_form
from config import OUTPUT_DIR


def inspect_appa_deep():
    pw, browser, context = start_browser(headless=True)

    try:
        menu_page = login(context)
        frames = navigate_to_expense_form(menu_page)

        appa_frame = frames.get("appa")
        if not appa_frame:
            print("ERROR: APPA frame not found!")
            return

        appa_frame.wait_for_load_state("networkidle", timeout=10000)
        time.sleep(2)

        # ── 1. 完整 HTML ──────────────────────────────
        appa_html = appa_frame.evaluate("""() => {
            return document.documentElement.outerHTML.substring(0, 80000);
        }""")

        # ── 2. 所有 interactive 元素 ─────────────────
        all_elements = appa_frame.evaluate("""() => {
            const els = document.querySelectorAll(
                'input, select, textarea, button, a[onclick], td[onclick], span[onclick]'
            );
            return [...els].map((el, idx) => ({
                idx,
                tag: el.tagName,
                name: el.name || '',
                id: el.id || '',
                type: el.type || '',
                value: (el.value || '').substring(0, 200),
                className: el.className || '',
                onclick: el.getAttribute('onclick') || '',
                onchange: el.getAttribute('onchange') || '',
                onblur: el.getAttribute('onblur') || '',
                onfocus: el.getAttribute('onfocus') || '',
                href: el.getAttribute('href') || '',
                innerText: (el.innerText || '').substring(0, 200),
                disabled: el.disabled || false,
                checked: el.checked || false,
                maxLength: el.maxLength > 0 ? el.maxLength : null,
                placeholder: el.placeholder || '',
                parentTag: el.parentElement?.tagName || '',
                parentText: (el.parentElement?.innerText || '').substring(0, 100),
            }));
        }""")

        # ── 3. 第1列的所有欄位（Row 1 詳細）──────────
        row1_elements = appa_frame.evaluate("""() => {
            // 找所有 name 結尾是 _1 的元素
            const els = document.querySelectorAll('[name$="_1"], [name$="NO_1"]');
            return [...els].map(el => ({
                tag: el.tagName,
                name: el.name,
                type: el.type || '',
                value: (el.value || '').substring(0, 200),
                checked: el.checked || false,
                disabled: el.disabled || false,
                onclick: el.getAttribute('onclick') || '',
                onchange: el.getAttribute('onchange') || '',
                onblur: el.getAttribute('onblur') || '',
                options: el.tagName === 'SELECT' ?
                    [...el.options].slice(0, 10).map(o => ({
                        value: o.value, text: o.text.substring(0, 80)
                    })) : null,
            }));
        }""")

        # ── 4. 所有 button 和 clickable 元素 ────────
        buttons = appa_frame.evaluate("""() => {
            const els = document.querySelectorAll(
                'input[type=button], input[type=submit], button, a[onclick]'
            );
            return [...els].map(el => ({
                tag: el.tagName,
                name: el.name || '',
                value: (el.value || '').substring(0, 200),
                innerText: (el.innerText || '').substring(0, 200),
                onclick: el.getAttribute('onclick') || '',
                className: el.className || '',
            }));
        }""")

        # ── 5. JS 函數名和 script 內容 ──────────────
        js_functions = appa_frame.evaluate("""() => {
            const scripts = document.querySelectorAll('script');
            const funcs = [];
            scripts.forEach(s => {
                const matches = s.textContent.match(
                    /function\\s+([A-Za-z_$][A-Za-z0-9_$]*)\\s*\\(/g
                );
                if (matches)
                    funcs.push(...matches.map(m =>
                        m.replace('function ', '').replace('(', '')
                    ));
            });
            return funcs;
        }""")

        script_content = appa_frame.evaluate("""() => {
            const scripts = document.querySelectorAll('script');
            let content = '';
            scripts.forEach(s => {
                if (s.textContent.length > 0)
                    content += '\\n--- SCRIPT ---\\n' + s.textContent.substring(0, 8000);
            });
            return content.substring(0, 50000);
        }""")

        # ── 6. 所有 hidden 欄位 ──────────────────────
        hidden_fields = appa_frame.evaluate("""() => {
            const els = document.querySelectorAll('input[type=hidden]');
            return [...els].map(el => ({
                name: el.name || '',
                id: el.id || '',
                value: (el.value || '').substring(0, 500),
            }));
        }""")

        # ── 7. 所有 select 元素 ──────────────────────
        all_selects = appa_frame.evaluate("""() => {
            return [...document.querySelectorAll('select')].map(s => ({
                name: s.name,
                id: s.id,
                disabled: s.disabled,
                optionCount: s.options.length,
                options: [...s.options].slice(0, 15).map(o => ({
                    value: o.value, text: o.text.substring(0, 80)
                })),
            }));
        }""")

        # ── 8. 所有 checkbox 元素 ────────────────────
        checkboxes = appa_frame.evaluate("""() => {
            return [...document.querySelectorAll('input[type=checkbox]')].map(el => ({
                name: el.name,
                id: el.id || '',
                checked: el.checked,
                value: el.value,
                onclick: el.getAttribute('onclick') || '',
                onchange: el.getAttribute('onchange') || '',
                parentText: (el.parentElement?.innerText || '').substring(0, 100),
            }));
        }""")

        # ── 9. Table 結構（取第1列的 td 內容）────────
        table_row1 = appa_frame.evaluate("""() => {
            // 找到第一個資料列（通常是 tr 中包含 input 的）
            const trs = document.querySelectorAll('tr');
            const rows = [];
            for (const tr of trs) {
                const inputs = tr.querySelectorAll('input, select, checkbox');
                if (inputs.length > 2) {
                    const cells = [...tr.querySelectorAll('td')].map(td => ({
                        html: td.innerHTML.substring(0, 500),
                        text: (td.innerText || '').substring(0, 100),
                        childElements: [...td.querySelectorAll('input, select')].map(el => ({
                            tag: el.tagName,
                            name: el.name || '',
                            type: el.type || '',
                        })),
                    }));
                    rows.push({
                        cellCount: cells.length,
                        cells: cells,
                    });
                    if (rows.length >= 3) break;  // 只取前 3 列
                }
            }
            return rows;
        }""")

        # ── 10. CK_VN frame 結構（查受款人框架）─────
        ck_vn_info = None
        for f in menu_page.frames:
            if "CHK_VEN" in f.url:
                try:
                    ck_vn_info = f.evaluate("""() => {
                        return {
                            url: window.location.href,
                            html: document.documentElement.outerHTML.substring(0, 5000),
                            forms: [...document.forms].map(f => ({
                                action: f.action,
                                method: f.method,
                                elements: [...f.elements].map(e => ({
                                    name: e.name, type: e.type,
                                    value: (e.value||'').substring(0, 200),
                                })),
                            })),
                        };
                    }""")
                except Exception as e:
                    ck_vn_info = {"error": str(e)}
                break

        # ── 組合結果 ─────────────────────────────────
        results = {
            "total_elements": len(all_elements),
            "all_elements": all_elements,
            "row1_elements": row1_elements,
            "buttons": buttons,
            "js_functions": js_functions,
            "hidden_fields": hidden_fields,
            "all_selects": all_selects,
            "checkboxes": checkboxes,
            "table_rows": table_row1,
            "ck_vn_frame": ck_vn_info,
        }

        # ── 存檔 ─────────────────────────────────────
        with open(f"{OUTPUT_DIR}/appa_deep.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        with open(f"{OUTPUT_DIR}/appa_html.html", "w", encoding="utf-8") as f:
            f.write(appa_html)

        with open(f"{OUTPUT_DIR}/appa_scripts.js", "w", encoding="utf-8") as f:
            f.write(script_content)

        # ── 印出摘要 ─────────────────────────────────
        print(f"\n=== APPA Frame 分析結果 ===")
        print(f"  總元素數: {len(all_elements)}")
        print(f"  Row 1 元素: {len(row1_elements)}")
        print(f"  按鈕: {len(buttons)}")
        print(f"  Hidden fields: {len(hidden_fields)}")
        print(f"  Select elements: {len(all_selects)}")
        print(f"  Checkboxes: {len(checkboxes)}")
        print(f"  JS functions: {js_functions}")
        print(f"  CK_VN frame: {'found' if ck_vn_info else 'not found'}")

        print(f"\n--- Row 1 欄位名稱 ---")
        for el in row1_elements:
            print(f"  {el['name']:20s} type={el['type']:10s} value={el.get('value','')}")

        print(f"\n--- Checkboxes ---")
        for cb in checkboxes:
            print(f"  {cb['name']:20s} checked={cb['checked']}  parent={cb['parentText'][:50]}")

        print(f"\n--- Buttons ---")
        for btn in buttons:
            val = btn.get('value', '') or btn.get('innerText', '')
            print(f"  {val:20s}  onclick={btn['onclick'][:80]}")

        print(f"\n結果已存至: {OUTPUT_DIR}/appa_deep.json")
        print(f"HTML 已存至: {OUTPUT_DIR}/appa_html.html")
        print(f"JS  已存至: {OUTPUT_DIR}/appa_scripts.js")

    finally:
        browser.close()
        pw.stop()


if __name__ == "__main__":
    inspect_appa_deep()
