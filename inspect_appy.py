"""深入分析 APPY frame（表頭：計畫/經費/科目）的欄位結構。"""

import json
import time
from form_filler import start_browser, login, navigate_to_expense_form
from config import OUTPUT_DIR


def inspect_appy_deep():
    pw, browser, context = start_browser(headless=True)

    try:
        menu_page = login(context)
        frames = navigate_to_expense_form(menu_page)

        appy_frame = frames.get("appy")
        if not appy_frame:
            print("ERROR: APPY frame not found!")
            return

        # 1. 取得 APPY frame 的完整 HTML（截斷到 50KB）
        appy_html = appy_frame.evaluate("""() => {
            return document.documentElement.outerHTML.substring(0, 50000);
        }""")

        # 2. 取得所有 interactive 元素 (input, select, textarea, a, button)
        appy_elements = appy_frame.evaluate("""() => {
            const els = document.querySelectorAll('input, select, textarea, a, button, td[onclick], td[onmousedown], span[onclick]');
            return [...els].map((el, idx) => ({
                idx: idx,
                tag: el.tagName,
                name: el.name || '',
                id: el.id || '',
                type: el.type || '',
                value: (el.value || '').substring(0, 200),
                className: el.className || '',
                onclick: el.getAttribute('onclick') || '',
                onchange: el.getAttribute('onchange') || '',
                onmousedown: el.getAttribute('onmousedown') || '',
                href: el.getAttribute('href') || '',
                innerText: (el.innerText || '').substring(0, 200),
                disabled: el.disabled || false,
                readonly: el.readOnly || false,
                options: el.tagName === 'SELECT' ?
                    [...el.options].slice(0, 20).map(o => ({
                        value: o.value, text: o.text, selected: o.selected
                    })) : null,
            }));
        }""")

        # 3. 取得所有 table cells 有 onclick 的
        clickable_cells = appy_frame.evaluate("""() => {
            const cells = document.querySelectorAll('td, th, span, div, a');
            return [...cells].filter(el =>
                el.getAttribute('onclick') ||
                el.getAttribute('onmousedown') ||
                el.getAttribute('ondblclick')
            ).map(el => ({
                tag: el.tagName,
                id: el.id || '',
                onclick: el.getAttribute('onclick') || '',
                onmousedown: el.getAttribute('onmousedown') || '',
                ondblclick: el.getAttribute('ondblclick') || '',
                innerText: (el.innerText || '').substring(0, 100),
                className: el.className || '',
            }));
        }""")

        # 4. 取得所有 JS 函數名稱
        js_functions = appy_frame.evaluate("""() => {
            const scripts = document.querySelectorAll('script');
            const funcs = [];
            scripts.forEach(s => {
                const matches = s.textContent.match(/function\\s+([A-Za-z_$][A-Za-z0-9_$]*)\\s*\\(/g);
                if (matches) funcs.push(...matches.map(m => m.replace('function ', '').replace('(', '')));
            });
            return funcs;
        }""")

        # 5. 取得 script 內容（精簡版，找與 select/dropdown 相關的）
        script_content = appy_frame.evaluate("""() => {
            const scripts = document.querySelectorAll('script');
            let content = '';
            scripts.forEach(s => {
                if (s.textContent.length > 0) {
                    content += '\\n--- SCRIPT ---\\n' + s.textContent.substring(0, 5000);
                }
            });
            return content.substring(0, 30000);
        }""")

        # 6. 找 select 元素（包含隱藏的）
        all_selects = appy_frame.evaluate("""() => {
            return [...document.querySelectorAll('select')].map(s => ({
                name: s.name,
                id: s.id,
                disabled: s.disabled,
                style: s.style.cssText,
                parentTag: s.parentElement?.tagName || '',
                parentId: s.parentElement?.id || '',
                optionCount: s.options.length,
                firstOptions: [...s.options].slice(0, 10).map(o => ({
                    value: o.value, text: o.text.substring(0, 80)
                })),
            }));
        }""")

        results = {
            "appy_elements": appy_elements,
            "clickable_cells": clickable_cells,
            "js_functions": js_functions,
            "all_selects": all_selects,
        }

        # 存結果
        with open(f"{OUTPUT_DIR}/appy_deep.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        with open(f"{OUTPUT_DIR}/appy_html.html", "w", encoding="utf-8") as f:
            f.write(appy_html)

        with open(f"{OUTPUT_DIR}/appy_scripts.js", "w", encoding="utf-8") as f:
            f.write(script_content)

        print(f"APPY elements: {len(appy_elements)}")
        print(f"Clickable cells: {len(clickable_cells)}")
        print(f"JS functions: {js_functions}")
        print(f"Select elements: {len(all_selects)}")
        print(f"Results saved to {OUTPUT_DIR}/appy_deep.json")

    finally:
        browser.close()
        pw.stop()


if __name__ == "__main__":
    inspect_appy_deep()
