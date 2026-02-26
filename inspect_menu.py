"""分析直接核銷表單的實際表單欄位 - 改用 response 攔截。"""

import json
import time
from playwright.sync_api import sync_playwright
from form_filler import login
from config import OUTPUT_DIR


def inspect_expense_fields():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.new_page()

        menu_page = login(context)

        # Step 1: LIS2
        title_frame = menu_page.frame("TITLE")
        title_frame.evaluate("LIS2()")
        time.sleep(2)

        # Step 2: 新增請購
        title_frame = menu_page.frame("TITLE")
        title_frame.wait_for_load_state("networkidle", timeout=10000)
        title_frame.evaluate("""() => {
            parent.FM.rows="15%,*,0,0,0,0,0";
            document.querySelector('a[name=aBT2]').click();
        }""")
        time.sleep(3)

        # 用 frame url 取得 MAIN frame（DA_APP_Q.asp 是類別選擇頁面）
        main_frame = None
        for f in menu_page.frames:
            if "DA_APP_Q" in f.url:
                main_frame = f
                break
        if not main_frame:
            main_frame = menu_page.frame("MAIN")

        main_frame.wait_for_load_state("networkidle", timeout=15000)

        # Step 3: 選 CHK3 (直接核銷) + 提交
        main_frame.evaluate("document.querySelector('input[name=CHK3]').click()")
        time.sleep(1)

        # 用 expect_navigation 等表單提交
        with main_frame.expect_navigation(timeout=15000):
            main_frame.evaluate("document.querySelector('input[name=SSS]').click()")

        time.sleep(3)

        # 重新列出所有 frames
        all_frames = []
        for f in menu_page.frames:
            all_frames.append({"name": f.name, "url": f.url})

        results = {"all_frames_after_submit": all_frames}

        # 嘗試找 APPY frame
        appy_frame = None
        appp_frame = None
        for f in menu_page.frames:
            if "STD_APPY_Q" in f.url:
                appy_frame = f
            elif "STD_APPP_Q" in f.url:
                appp_frame = f

        if appy_frame:
            try:
                appy_frame.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass
            appy_data = appy_frame.evaluate("""() => ({
                url: location.href,
                bodyText: document.body?.innerText?.substring(0, 5000) || '',
                forms: [...document.querySelectorAll('form')].map(f => ({
                    id: f.id, action: f.action, method: f.method,
                    elements: [...f.querySelectorAll('input,select,textarea')].map(i => ({
                        tag: i.tagName,
                        name: i.name,
                        type: i.type || '',
                        value: i.value?.substring(0, 200) || '',
                        id: i.id || '',
                        readonly: i.readOnly || false,
                        disabled: i.disabled || false,
                        maxLength: i.maxLength > 0 ? i.maxLength : undefined,
                        options: i.tagName === 'SELECT' ?
                            [...i.options].slice(0, 30).map(o => ({
                                value: o.value, text: o.text, selected: o.selected
                            })) : undefined,
                    })),
                })),
            })""")
            results["appy_frame"] = appy_data
        else:
            results["appy_frame"] = "NOT FOUND"

        if appp_frame:
            try:
                appp_frame.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass
            appp_data = appp_frame.evaluate("""() => ({
                url: location.href,
                bodyText: document.body?.innerText?.substring(0, 5000) || '',
                forms: [...document.querySelectorAll('form')].map(f => ({
                    id: f.id, action: f.action, method: f.method,
                    elements: [...f.querySelectorAll('input,select,textarea')].map(i => ({
                        tag: i.tagName,
                        name: i.name,
                        type: i.type || '',
                        value: i.value?.substring(0, 200) || '',
                        id: i.id || '',
                        readonly: i.readOnly || false,
                        disabled: i.disabled || false,
                        maxLength: i.maxLength > 0 ? i.maxLength : undefined,
                        options: i.tagName === 'SELECT' ?
                            [...i.options].slice(0, 30).map(o => ({
                                value: o.value, text: o.text, selected: o.selected
                            })) : undefined,
                    })),
                })),
            })""")
            results["appp_frame"] = appp_data
        else:
            results["appp_frame"] = "NOT FOUND"

        # 也看 APPA
        appa_frame = None
        for f in menu_page.frames:
            if "STD_APPA_Q" in f.url:
                appa_frame = f
        if appa_frame:
            try:
                appa_frame.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass
            appa_data = appa_frame.evaluate("""() => ({
                url: location.href,
                bodyText: document.body?.innerText?.substring(0, 3000) || '',
                forms: [...document.querySelectorAll('form')].map(f => ({
                    id: f.id, action: f.action, method: f.method,
                    elements: [...f.querySelectorAll('input,select,textarea')].map(i => ({
                        tag: i.tagName,
                        name: i.name,
                        type: i.type || '',
                        value: i.value?.substring(0, 200) || '',
                        id: i.id || '',
                        options: i.tagName === 'SELECT' ?
                            [...i.options].slice(0, 30).map(o => ({
                                value: o.value, text: o.text, selected: o.selected
                            })) : undefined,
                    })),
                })),
            })""")
            results["appa_frame"] = appa_data

        with open(f"{OUTPUT_DIR}/expense_fields.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Results saved to {OUTPUT_DIR}/expense_fields.json")
        browser.close()


if __name__ == "__main__":
    inspect_expense_fields()
