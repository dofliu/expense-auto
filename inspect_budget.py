"""取得可用的預算計畫編號和經費用途選項。"""

import json
import time
from form_filler import start_browser, login, navigate_to_expense_form
from config import OUTPUT_DIR


def inspect_budget():
    pw, browser, context = start_browser(headless=True)

    try:
        menu_page = login(context)
        frames = navigate_to_expense_form(menu_page)

        appy_frame = frames.get("appy")
        if not appy_frame:
            print("ERROR: APPY frame not found!")
            return

        # 1. 取得 BUGETNO_1 的所有 options（計畫編號列表）
        bugetno_opts = appy_frame.evaluate("""() => {
            const sel = document.querySelector('select[name="BUGETNO_1"]');
            if (!sel) return {error: 'BUGETNO_1 not found'};
            return [...sel.options].map(o => ({
                value: o.value,
                text: o.text,
            }));
        }""")

        # 2. 取得 TRAN frame 中的原始資料
        tran_data = None
        for f in menu_page.frames:
            if "TRAN" in f.name:
                try:
                    tran_data = f.evaluate("""() => ({
                        BUGET: document.querySelector('input[name="BUGET"]')?.value?.substring(0, 5000) || '',
                        BUGETS: document.querySelector('input[name="BUGETS"]')?.value?.substring(0, 5000) || '',
                        SUBJECTNO: document.querySelector('input[name="SUBJECTNO"]')?.value?.substring(0, 5000) || '',
                        APYKIND: document.querySelector('input[name="APYKIND"]')?.value?.substring(0, 2000) || '',
                        formElements: [...document.querySelectorAll('form input')].map(i => ({
                            name: i.name, value: (i.value || '').substring(0, 200),
                        })),
                    })""")
                except Exception as e:
                    tran_data = {"error": str(e)}
                break

        # 3. 取得 D_APYKIND_1 options (分類)
        apykind_opts = appy_frame.evaluate("""() => {
            const sel = document.querySelector('select[name="D_APYKIND_1"]');
            if (!sel) return {error: 'D_APYKIND_1 not found'};
            return [...sel.options].map(o => ({
                value: o.value,
                text: o.text,
            }));
        }""")

        # 4. 取得 SERSUB_1 options (科目)
        sersub_opts = appy_frame.evaluate("""() => {
            const sel = document.querySelector('select[name="SERSUB_1"]');
            if (!sel) return {error: 'SERSUB_1 not found'};
            return [...sel.options].map(o => ({
                value: o.value,
                text: o.text,
            }));
        }""")

        # 5. 取得 APPY hidden fields
        appy_hidden = appy_frame.evaluate("""() => {
            return [...document.querySelectorAll('input[type="hidden"]')].map(i => ({
                name: i.name,
                value: (i.value || '').substring(0, 300),
            }));
        }""")

        # 6. 取得 amount 相關欄位
        amount_fields = appy_frame.evaluate("""() => {
            const names = ['D_AMOUNT_1', 'A9_1', 'BUGET_AMOUNT_1', 'MOVETYPE_1',
                           'SUBJECTNO_1', 'D_BUGETNO_1', 'D_BUGCODE_1'];
            return names.map(name => {
                const el = document.querySelector(`input[name="${name}"]`);
                return {
                    name: name,
                    found: !!el,
                    type: el?.type || '',
                    value: (el?.value || '').substring(0, 200),
                    disabled: el?.disabled || false,
                };
            });
        }""")

        results = {
            "bugetno_options": bugetno_opts,
            "apykind_options": apykind_opts,
            "sersub_options": sersub_opts,
            "amount_fields": amount_fields,
            "appy_hidden_fields": appy_hidden,
            "tran_data": tran_data,
        }

        with open(f"{OUTPUT_DIR}/budget_data.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # Pretty print key info
        print("\n=== 計畫編號 (BUGETNO_1) 選項 ===")
        if isinstance(bugetno_opts, list):
            for opt in bugetno_opts:
                print(f"  value={opt['value']!r:20s}  text={opt['text']}")
        else:
            print(f"  {bugetno_opts}")

        print(f"\n=== 分類 (D_APYKIND_1) 選項 ({len(apykind_opts) if isinstance(apykind_opts, list) else '?'}) ===")
        if isinstance(apykind_opts, list):
            for opt in apykind_opts[:10]:
                print(f"  value={opt['value']!r:20s}  text={opt['text']}")

        print(f"\n=== 科目 (SERSUB_1) 選項 ({len(sersub_opts) if isinstance(sersub_opts, list) else '?'}) ===")
        if isinstance(sersub_opts, list):
            for opt in sersub_opts[:10]:
                print(f"  value={opt['value']!r:20s}  text={opt['text']}")

        print(f"\n=== Amount 欄位 ===")
        for af in amount_fields:
            print(f"  {af['name']:20s}  found={af['found']}  type={af['type']!r:10s}  value={af['value']!r}")

        if tran_data and isinstance(tran_data, dict) and 'BUGET' in tran_data:
            print(f"\n=== TRAN BUGET (first 200 chars) ===")
            print(f"  {tran_data['BUGET'][:200]}")
            print(f"\n=== TRAN BUGETS (first 200 chars) ===")
            print(f"  {tran_data['BUGETS'][:200]}")
            print(f"\n=== TRAN APYKIND ===")
            print(f"  {tran_data['APYKIND'][:200]}")

        print(f"\nResults saved to {OUTPUT_DIR}/budget_data.json")

    finally:
        browser.close()
        pw.stop()


if __name__ == "__main__":
    inspect_budget()
