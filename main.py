"""主程式入口：掃描 receipts/ 內的發票圖片，逐一辨識並填單。

完整流程：
    1. 選擇核銷計畫（啟動時一次）
    2. 掃描 receipts/ 中的圖片
    3. 逐張：OCR → 確認 → 登入 → 填品名 → 填經費 → 填受款人 → 驗證 → 存入
"""

import argparse
import os
import sys
import json
from datetime import date
from pathlib import Path

from config import RECEIPTS_DIR, OUTPUT_DIR
from ocr import extract_receipt_data
from form_filler import (
    start_browser, login, navigate_to_expense_form, fill_expense_form,
)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# ── 常用計畫清單（可自行新增）──────────────────────
# 選項格式: (顯示名稱, 搜尋關鍵字, 需要計畫請購)
#   需要計畫請購=True → 使用 LIS4 (計畫請購) 路徑
#   需要計畫請購=False → 使用 LIS2 (部門請購) 路徑
PLAN_CHOICES = [
    ("部門經費（高教深耕）", "高教深耕", False),
    ("國科會計畫", "國科會", True),
    ("產學計畫", "產學", True),
    ("教育部計畫", "教育部", True),
]

# ── 收據流水號追蹤（每天重新從 01 開始）────────────
_receipt_counter: dict[str, int] = {}  # key: "YYYYMMDD" → next seq


def get_next_receipt_seq(iso_date: str) -> int:
    """
    取得某日的下一個收據流水號。

    同天第 1 張=1、第 2 張=2，隔天重新從 1 開始。
    """
    key = iso_date.replace("-", "")[:8]  # "20260226"
    _receipt_counter[key] = _receipt_counter.get(key, 0) + 1
    return _receipt_counter[key]


def get_receipt_images() -> list[Path]:
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
    讓使用者選擇核銷計畫，回傳 (搜尋關鍵字, 是否需要計畫請購)。

    Args:
        preset: 若已透過命令列指定，直接回傳。

    Returns:
        (計畫名稱關鍵字, 需要計畫請購 bool)
        例如: ("產學", True) 或 ("", False)
    """
    if preset:
        # 從 PLAN_CHOICES 找對應的 use_project 設定
        for name, kw, need_project in PLAN_CHOICES:
            if kw == preset or preset in name:
                print(f"使用計畫: {name} (搜尋: {kw}, {'計畫請購' if need_project else '部門請購'})")
                return kw, need_project
        print(f"使用計畫: {preset} (計畫請購)")
        return preset, True  # 預設用計畫請購

    print("\n請選擇核銷計畫：")
    for i, (name, _kw, need_proj) in enumerate(PLAN_CHOICES, 1):
        mode = "計畫請購" if need_proj else "部門請購"
        print(f"  {i}. {name} [{mode}]")
    print(f"  {len(PLAN_CHOICES) + 1}. 其他（手動輸入關鍵字）")
    print(f"  0. 使用預設（第一個計畫）")

    try:
        choice = input("> ").strip()
    except EOFError:
        choice = "0"

    if choice == "0" or not choice:
        return "", False

    try:
        idx = int(choice)
        if 1 <= idx <= len(PLAN_CHOICES):
            name, kw, need_project = PLAN_CHOICES[idx - 1]
            mode = "計畫請購" if need_project else "部門請購"
            print(f"  → 選擇: {name} (搜尋: {kw}, {mode})")
            return kw, need_project
        elif idx == len(PLAN_CHOICES) + 1:
            kw = input("請輸入計畫關鍵字: ").strip()
            return kw, True  # 手動輸入預設用計畫請購
    except ValueError:
        # 直接輸入關鍵字
        return choice, True

    return "", False


def process_single(image_path: Path, plan_name: str = "",
                    headless: bool = True, auto_save: bool = True,
                    use_project: bool = False):
    """
    處理單張發票：OCR → 確認 → 登入 → 導航 → 填品名/經費/受款人 → 存入。

    Args:
        image_path: 發票圖片路徑
        plan_name: 計畫名稱關鍵字
        headless: 是否使用 headless 瀏覽器
        auto_save: 是否在金額一致時自動存入
        use_project: True=計畫請購, False=部門請購
    """
    print(f"\n{'='*60}")
    print(f"處理: {image_path.name}")
    print(f"{'='*60}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ── Step 1: OCR 辨識 ──────────────────────────
    print("正在辨識發票...")
    receipt_data = extract_receipt_data(str(image_path))

    print(f"  廠商: {receipt_data.get('vendor', 'N/A')}")
    print(f"  金額: {receipt_data.get('amount', 'N/A')}")
    print(f"  日期: {receipt_data.get('date', 'N/A')}")
    print(f"  發票號碼: {receipt_data.get('invoice_no', '(無)')}")
    print(f"  品項: {json.dumps(receipt_data.get('items', []), ensure_ascii=False)}")

    # 存 OCR 結果
    ocr_out = Path(OUTPUT_DIR) / f"{image_path.stem}_ocr.json"
    with open(ocr_out, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, ensure_ascii=False, indent=2)
    print(f"  OCR 結果: {ocr_out}")

    # ── Step 2: 確認 ──────────────────────────────
    try:
        confirm = input("是否填入核銷系統？(y/n): ").strip().lower()
    except EOFError:
        confirm = "y"

    if confirm != "y":
        print("已跳過。")
        return

    # ── Step 3: 計算收據流水號 ────────────────────
    receipt_date = receipt_data.get("date", "")
    if not receipt_date:
        # 無日期時用今天
        receipt_date = date.today().isoformat()
        receipt_data["date"] = receipt_date
        print(f"  日期未辨識，使用今天: {receipt_date}")

    if receipt_data.get("invoice_no"):
        print("  此為發票，不計算收據流水號")
        receipt_seq = 0
    else:
        receipt_seq = get_next_receipt_seq(receipt_date)
        print(f"  收據流水號: {receipt_seq:02d}")

    # ── Step 4: 自動登入 → 導航 → 填三區塊 → 存入 ─
    pw, browser, context = start_browser(headless=headless)
    try:
        # 登入
        menu_page = login(context)

        # 導航到核銷表單
        frames = navigate_to_expense_form(menu_page, use_project=use_project,
                                          plan_name=plan_name)

        # 填寫表單（品名 + 經費 + 受款人 + 自動存入）
        fill_expense_form(
            frames, receipt_data,
            menu_page=menu_page,
            context=context,
            plan_name=plan_name,
            receipt_seq=receipt_seq,
            auto_save=auto_save,
        )

        # 截圖
        screenshot_path = f"{OUTPUT_DIR}/{image_path.stem}_filled.png"
        menu_page.screenshot(path=screenshot_path, full_page=True)
        print(f"  截圖已存: {screenshot_path}")

        # 如果不是自動存入，暫停讓使用者檢查
        if not auto_save:
            try:
                input("請確認表單填寫正確後按 Enter 繼續...")
            except EOFError:
                pass

    finally:
        browser.close()
        pw.stop()

    print("完成！")


def main():
    # ── 解析命令列參數 ────────────────────────────
    parser = argparse.ArgumentParser(
        description="核銷自動填單：OCR 辨識發票 → 自動填入核銷系統"
    )
    parser.add_argument(
        "--plan", type=str, default="",
        help="計畫名稱關鍵字（如 '高教深耕'），跳過互動選擇"
    )
    parser.add_argument(
        "--no-save", action="store_true",
        help="不自動存入（僅填單截圖，供檢查用）"
    )
    parser.add_argument(
        "--headless", action="store_true", default=True,
        help="使用 headless 瀏覽器（預設）"
    )
    parser.add_argument(
        "--no-headless", action="store_true",
        help="顯示瀏覽器視窗（debug 用）"
    )
    parser.add_argument(
        "--ocr-only", action="store_true",
        help="僅執行 OCR 辨識，不填入系統"
    )
    parser.add_argument(
        "--project", action="store_true",
        help="使用「計畫請購」路徑（預設為「部門請購」）"
    )
    args = parser.parse_args()

    headless = not args.no_headless
    auto_save = not args.no_save
    use_project = args.project

    # ── 掃描圖片 ──────────────────────────────────
    images = get_receipt_images()
    if not images:
        print("receipts/ 目錄中沒有找到圖片。")
        print(f"請將發票/收據圖片放入 {RECEIPTS_DIR}/ 目錄。")
        sys.exit(0)

    print(f"\n找到 {len(images)} 張發票/收據圖片：")
    for i, img in enumerate(images, 1):
        print(f"  {i}. {img.name}")

    # ── OCR-only 模式 ────────────────────────────
    if args.ocr_only:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        for image in images:
            print(f"\n--- OCR: {image.name} ---")
            data = extract_receipt_data(str(image))
            out = Path(OUTPUT_DIR) / f"{image.stem}_ocr.json"
            with open(out, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(json.dumps(data, ensure_ascii=False, indent=2))
        print("\nOCR 完成！")
        sys.exit(0)

    # ── 選擇計畫 ──────────────────────────────────
    plan_name, plan_need_project = choose_plan(preset=args.plan)

    # 若選的計畫需要計畫請購，自動覆蓋 use_project
    if plan_need_project and not use_project:
        print(f"  自動切換到「計畫請購」模式（{plan_name} 需要計畫請購路徑）")
        use_project = True

    # ── 處理模式說明 ──────────────────────────────
    mode_str = "計畫請購" if use_project else "部門請購"
    print(f"\n{'─'*40}")
    print(f"  請購類型: {mode_str}")
    print(f"  計畫: {plan_name or '(預設)'}")
    print(f"  自動存入: {'是' if auto_save else '否'}")
    print(f"  瀏覽器: {'headless' if headless else '有畫面'}")
    print(f"  圖片數: {len(images)}")
    print(f"{'─'*40}")

    # ── 逐張處理 ──────────────────────────────────
    success = 0
    for idx, image in enumerate(images, 1):
        print(f"\n[{idx}/{len(images)}]")
        try:
            process_single(
                image,
                plan_name=plan_name,
                headless=headless,
                auto_save=auto_save,
                use_project=use_project,
            )
            success += 1
        except Exception as e:
            print(f"  錯誤: {e}")
            print(f"  跳過 {image.name}，繼續下一張...")

    # ── 結果摘要 ──────────────────────────────────
    print(f"\n{'='*60}")
    print(f"全部處理完成！成功: {success}/{len(images)}")
    if _receipt_counter:
        print("收據流水號統計：")
        for day, count in sorted(_receipt_counter.items()):
            print(f"  {day[:4]}/{day[4:6]}/{day[6:]}: {count} 張")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
