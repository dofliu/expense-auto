"""主程式入口：掃描 receipts/ 內的發票圖片，合併辨識後填入同一張請購單。

完整流程：
    1. 掃描 receipts/ 中的所有圖片
    2. OCR 辨識所有圖片（每張照片可能含多張收據）
    3. 顯示辨識摘要
    4. 使用者確認（一次確認全部）
    5. 選擇核銷類型（部門採購 / 計畫請購）
    6. 合併所有收據 → 一份 receipt_data
    7. 登入 → 導航 → 填品名 / 經費 / 受款人 → 驗證 → 存入
"""

import argparse
import os
import sys
import json
import threading
from datetime import date as date_cls
from pathlib import Path

from config import RECEIPTS_DIR, OUTPUT_DIR


def _timed_input(prompt: str, timeout: int = 10, default: str = "") -> str:
    """帶超時的 input()。超過 timeout 秒未輸入則自動回傳 default。"""
    result = [default]

    def _ask():
        try:
            result[0] = input(prompt)
        except EOFError:
            result[0] = default

    t = threading.Thread(target=_ask, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        print(f"\n    (超過 {timeout} 秒未選擇，自動使用預設值)")
        return default
    return result[0]
from ocr import extract_multiple_receipts
from form_filler import (
    start_browser, login, navigate_to_expense_form, fill_expense_form,
)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# ── 收據流水號追蹤（每天重新從 01 開始）────────────
_receipt_counter: dict = {}  # key: "YYYYMMDD" → next_seq


def get_next_receipt_seq(iso_date: str) -> int:
    """
    取得某日的下一個收據流水號。
    同天第 1 張=1、第 2 張=2，隔天重新從 1 開始。
    """
    key = iso_date.replace("-", "")[:8]  # "20260226"
    _receipt_counter[key] = _receipt_counter.get(key, 0) + 1
    return _receipt_counter[key]


def get_receipt_images() -> list:
    """取得 receipts/ 目錄中所有支援的圖片檔。"""
    receipts_dir = Path(RECEIPTS_DIR)
    if not receipts_dir.exists():
        print(f"找不到目錄: {RECEIPTS_DIR}")
        return []
    images = [
        f for f in sorted(receipts_dir.iterdir())
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return images


def choose_plan(preset: str = "") -> tuple:
    """
    讓使用者選擇核銷類型（部門採購或計畫請購）。
    實際計畫名稱（BUGETNO）會在登入後從系統下拉選單中選擇。

    Returns:
        (計畫關鍵字, 需要計畫請購 bool)
    """
    if preset:
        print(f"使用計畫關鍵字: {preset} (計畫請購路徑)")
        return preset, True

    print("\n請選擇核銷類型：")
    print("  1. 部門採購（高教深耕等部門經費）")
    print("  2. 計畫請購（國科會 / 產學 / 教育部等計畫）")

    choice = _timed_input("> ", timeout=10, default="2").strip()

    if choice == "2":
        print("  → 計畫請購（進入系統後請從下拉選單選擇計畫）")
        return "", True
    else:
        print("  → 部門採購（進入系統後請從下拉選單選擇計畫）")
        return "", False


# ════════════════════════════════════════════════════════════
#  OCR 批次辨識
# ════════════════════════════════════════════════════════════

def ocr_all_images(images: list) -> list:
    """
    OCR 所有圖片，每張照片可能包含多張收據。
    回傳所有收據的 flat list，每筆附加 _source_image 欄位。
    """
    all_receipts = []
    for img in images:
        print(f"  辨識中: {img.name} ...")
        try:
            receipts = extract_multiple_receipts(str(img))
            n = len(receipts)
            label = "" if n == 1 else f"（含 {n} 張收據）"
            print(f"    -> 完成{label}")
            for r in receipts:
                r["_source_image"] = img.name
            all_receipts.extend(receipts)
        except Exception as e:
            print(f"    [ERROR] OCR 失敗: {e}")
    return all_receipts


def show_ocr_summary(receipts: list) -> None:
    """在終端顯示所有辨識到的收據摘要供使用者確認。"""
    print(f"\n共辨識到 {len(receipts)} 張收據，將合併為一張請購單：")
    print(f"{'─'*50}")
    grand_total = 0
    for i, r in enumerate(receipts, 1):
        try:
            amt = int(float(r.get("amount", 0)))
        except (ValueError, TypeError):
            amt = 0
        grand_total += amt
        src = r.get("_source_image", "")
        src_label = f" [{src}]" if src else ""
        inv = r.get("invoice_no", "")
        inv_label = f" 發票:{inv}" if inv else " (收據)"
        print(f"  [{i}]{src_label}")
        print(f"      廠商: {r.get('vendor', '?')}  日期: {r.get('date', '?')}"
              f"  金額: NT${amt}{inv_label}")
        items = r.get("items", [])
        if items:
            for item in items:
                try:
                    qty = int(float(item.get("quantity", 1)))
                    price = int(float(item.get("price", 0)))
                    subtotal = qty * price
                except (ValueError, TypeError):
                    qty, price, subtotal = 1, 0, 0
                print(f"      - {item.get('name', '?')} x{qty} "
                      f"= NT${subtotal}")
    print(f"{'─'*50}")
    print(f"  合計總金額: NT${grand_total}")


# ════════════════════════════════════════════════════════════
#  收據合併
# ════════════════════════════════════════════════════════════

def merge_receipts(receipts: list) -> dict:
    """
    將多張收據合併為一份 receipt_data，填入同一張請購單。

    合併規則：
    - items:      所有品項串接（超過 14 項時截斷並警告）
    - amount:     各 amount 加總
    - date:       最早的日期
    - vendor:     唯一廠商直接用；多家則顯示「廠商A 等N家」
    - invoice_no: 若只有一張且有發票號碼則保留；否則留空（自動產生收據號碼）
    - tax_id:     第一張的統一編號
    """
    if not receipts:
        return {}

    # 單張直接回傳（不需要合併）
    if len(receipts) == 1:
        return receipts[0]

    all_items = []
    total_amount = 0
    dates = []
    vendors = []

    for r in receipts:
        items = r.get("items", [])
        if not items:
            # 無品項明細時，用廠商名稱 + 總金額建一個代表品項
            try:
                amt = int(float(r.get("amount", 0)))
            except (ValueError, TypeError):
                amt = 0
            items = [{
                "name": r.get("vendor", "核銷明細"),
                "quantity": 1,
                "price": amt,
            }]
        all_items.extend(items)

        try:
            total_amount += int(float(r.get("amount", 0)))
        except (ValueError, TypeError):
            pass

        d = r.get("date", "")
        if d:
            dates.append(d)

        v = r.get("vendor", "")
        if v and v not in vendors:
            vendors.append(v)

    # 選日期（最早）
    merged_date = min(dates) if dates else date_cls.today().isoformat()

    # 選廠商名
    if not vendors:
        merged_vendor = "多家廠商"
    elif len(vendors) == 1:
        merged_vendor = vendors[0]
    else:
        merged_vendor = f"{vendors[0]} 等{len(vendors)}家"

    # 品項數量警告
    if len(all_items) > 14:
        print(f"  [WARN] 合計品項 {len(all_items)} 項，超過系統上限 14 項")
        print(f"         將截斷至 14 項（超出金額會進入「差額」列）")

    return {
        "date": merged_date,
        "vendor": merged_vendor,
        "amount": total_amount,
        "tax_id": receipts[0].get("tax_id", ""),
        "invoice_no": "",          # 多張合併統一用自動收據號碼
        "items": all_items,
        "_source_count": len(receipts),
        "_vendors": vendors,
        "_receipts": receipts,     # 保留原始清單供 APPA 多行填寫用
    }


# ════════════════════════════════════════════════════════════
#  填單（單次登入，處理合併後的 receipt_data）
# ════════════════════════════════════════════════════════════

def process_batch(merged_data: dict, plan_name: str = "",
                  headless: bool = True, auto_save: bool = True,
                  use_project: bool = False,
                  source_stem: str = "batch",
                  auto_close: bool = False):
    """
    將合併後的 receipt_data 填入核銷系統（一張請購單）。

    Args:
        merged_data:  merge_receipts() 回傳的合併 receipt_data
        plan_name:    計畫名稱關鍵字（進系統後下拉選單篩選用）
        headless:     是否使用 headless 瀏覽器
        auto_save:    是否在金額一致時自動存入
        use_project:  True=計畫請購, False=部門請購
        source_stem:  截圖檔名前綴
        auto_close:   完成後是否自動關閉瀏覽器
    """
    print(f"\n{'='*60}")
    print(f"填入核銷系統...")
    print(f"{'='*60}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 存合併後的 OCR 結果（供事後檢查）
    ocr_out = Path(OUTPUT_DIR) / f"{source_stem}_merged_ocr.json"
    with open(ocr_out, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    print(f"  合併 OCR: {ocr_out}")

    # 計算收據流水號
    receipt_date = merged_data.get("date", "")
    if not receipt_date:
        receipt_date = date_cls.today().isoformat()
        merged_data["date"] = receipt_date
        print(f"  日期未辨識，使用今天: {receipt_date}")

    if merged_data.get("invoice_no"):
        print("  此為單張發票，不計算收據流水號")
        receipt_seq = 0
    else:
        receipt_seq = get_next_receipt_seq(receipt_date)
        print(f"  收據流水號: {receipt_seq:02d}")

    # 登入 → 導航 → 填三區塊 → 存入
    pw, browser, context = start_browser(headless=headless)
    try:
        menu_page = login(context)

        frames = navigate_to_expense_form(
            menu_page, use_project=use_project, plan_name=plan_name
        )

        fill_expense_form(
            frames, merged_data,
            menu_page=menu_page,
            context=context,
            plan_name=plan_name,
            receipt_seq=receipt_seq,
            auto_save=auto_save,
            use_project=use_project,
        )

        screenshot_path = f"{OUTPUT_DIR}/{source_stem}_filled.png"
        menu_page.screenshot(path=screenshot_path, full_page=True)
        print(f"  截圖已存: {screenshot_path}")

        if not auto_save:
            print("\n  [提示] 系統已暫停自動存入！您可以：")
            print("         1. 切換到視窗去檢查欄位（經費/品名/受款人）。")
            print("         2. 直接在網頁上修改內容。")
            print("         3. 從網頁上按下「存入」。")
            _timed_input("\n  [按 Enter 繼續，或等待 60 秒自動繼續...] ",
                         timeout=60, default="")

        if not auto_close:
            _timed_input("\n  [保留瀏覽器] 按 Enter 關閉，或等待 60 秒自動關閉...",
                         timeout=60, default="")
    finally:
        browser.close()
        pw.stop()

    print("完成！")


# ════════════════════════════════════════════════════════════
#  主程式
# ════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="核銷自動填單：OCR 辨識發票 → 合併 → 填入一張請購單"
    )
    parser.add_argument(
        "--plan", type=str, default="",
        help="計畫名稱關鍵字（如 '高教深耕'），跳過互動選擇"
    )
    parser.add_argument(
        "--auto-save", action="store_true",
        help="自動存入（預設為手動確認後存入）"
    )
    parser.add_argument(
        "--headless", action="store_true",
        help="不顯示瀏覽器視窗（預設會顯示視窗供查看）"
    )
    parser.add_argument(
        "--close", action="store_true",
        help="完成後自動關閉瀏覽器（預設會保持開啟讓您繼續操作）"
    )
    parser.add_argument(
        "--ocr-only", action="store_true",
        help="僅執行 OCR 辨識，不填入系統"
    )
    parser.add_argument(
        "--project", action="store_true",
        help="使用「計畫請購」路徑（預設為「部門請購」）"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="使用測試資料（不進行 OCR，直接填入固定的測試資料）"
    )
    args = parser.parse_args()

    headless = args.headless
    auto_save = args.auto_save
    auto_close = args.close
    use_project = args.project
    use_test_data = args.test

    # ── Step 1~3: 掃描與 OCR 或測試資料 ──────────────────────────
    if use_test_data:
        print("\n[測試模式] 啟用，直接使用測試資料，不進行 OCR 辨識。")
        # 測試用收據（收據號碼自動產生，不指定 invoice_no）
        all_receipts = [{
            "date": date_cls.today().isoformat(),
            "invoice_no": "",
            "amount": 1000,
            "items": [
                {"name": "測試用物品A", "quantity": 1, "price": 400, "amount": 400},
                {"name": "測試用物品B", "quantity": 2, "price": 300, "amount": 600}
            ],
            "payee": "測試受款人",
            "_source_image": "test_dummy.jpg"
        }]
        images = [Path("test_dummy.jpg")]
    else:
        images = get_receipt_images()
        if not images:
            print(f"receipts/ 目錄中沒有找到圖片。")
            print(f"請將發票/收據圖片放入 {RECEIPTS_DIR}/ 目錄。")
            sys.exit(0)

        print(f"\n找到 {len(images)} 張圖片：")
        for i, img in enumerate(images, 1):
            print(f"  {i}. {img.name}")

        # ── Step 2: OCR 所有圖片 ──────────────────────
        print("\n開始辨識...")
        all_receipts = ocr_all_images(images)

        if not all_receipts:
            print("OCR 失敗，無法辨識任何收據。")
            sys.exit(1)

        # 儲存各張 OCR 結果
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        saved_stems = {}
        for r in all_receipts:
            src = r.get("_source_image", "receipt")
            stem = Path(src).stem
            # 同一張圖片可能有多張收據，加序號區分
            saved_stems[stem] = saved_stems.get(stem, 0) + 1
            suffix = f"_{saved_stems[stem]}" if saved_stems[stem] > 1 else ""
            out = Path(OUTPUT_DIR) / f"{stem}{suffix}_ocr.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(r, f, ensure_ascii=False, indent=2)

        # ── Step 3: 顯示辨識摘要 ──────────────────────
        show_ocr_summary(all_receipts)

        # ── OCR-only 模式 ─────────────────────────────
        if args.ocr_only:
            print("\nOCR 完成！（--ocr-only 模式，不填入系統）")
            sys.exit(0)

    # ── Step 4: 選擇計畫類型 ──────────────────────
    plan_name, plan_need_project = choose_plan(preset=args.plan)
    if plan_need_project:
        use_project = True

    mode_str = "計畫請購" if use_project else "部門請購"
    print(f"\n{'─'*40}")
    print(f"  請購類型: {mode_str}")
    print(f"  計畫: {plan_name or '(進入系統後從下拉選單選擇)'}")
    print(f"  自動存入: {'是' if auto_save else '否'}")
    print(f"  瀏覽器: {'headless' if headless else '有畫面'}")
    print(f"  收據數: {len(all_receipts)} 張 -> 合併為 1 張請購單")
    print(f"  測試模式: {'是' if use_test_data else '否'}")
    print(f"{'─'*40}")

    # ── Step 5: 使用者確認 ────────────────────────
    if use_test_data:
        confirm = "y"
    else:
        confirm = _timed_input("\n是否將以上收據合併填入核銷系統？(y/n, 10秒後自動y): ",
                               timeout=10, default="y").strip().lower()

    if confirm != "y":
        print("已取消。")
        sys.exit(0)

    # ── Step 6: 合併所有收據 ──────────────────────
    merged = merge_receipts(all_receipts)
    n_items = len(merged.get("items", []))
    print(f"\n合併後: {n_items} 個品項，總金額 NT${merged.get('amount', 0)}")

    # 截圖前綴：單張圖片用其名稱，多張用 batch_日期
    if use_test_data:
        source_stem = "test_dummy"
    elif len(images) == 1:
        source_stem = images[0].stem
    else:
        source_stem = f"batch_{date_cls.today().strftime('%Y%m%d')}"

    # ── Step 7: 填入系統 ──────────────────────────
    try:
        process_batch(
            merged,
            plan_name=plan_name,
            headless=headless,
            auto_save=auto_save,
            use_project=use_project,
            source_stem=source_stem,
            auto_close=auto_close,
        )
    except Exception as e:
        print(f"\n[ERROR] 填單失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # ── 結果摘要 ──────────────────────────────────
    print(f"\n{'='*60}")
    print(f"全部完成！")
    if _receipt_counter:
        print("收據流水號統計：")
        for day, count in sorted(_receipt_counter.items()):
            print(f"  {day[:4]}/{day[4:6]}/{day[6:]}: {count} 張")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
