"""主程式入口：掃描 receipts/ 內的發票圖片，逐一辨識並填單。"""

import os
import sys
import json
from pathlib import Path

from config import RECEIPTS_DIR, OUTPUT_DIR
from ocr import extract_receipt_data
from form_filler import (
    start_browser, login, navigate_to_expense_form, fill_expense_form,
)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


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


def process_single(image_path: Path, headless: bool = True):
    """處理單張發票：OCR → 登入 → 導航 → 填單。"""
    print(f"\n{'='*50}")
    print(f"處理: {image_path.name}")
    print(f"{'='*50}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Step 1: OCR 辨識
    print("正在辨識發票...")
    receipt_data = extract_receipt_data(str(image_path))
    print(f"  廠商: {receipt_data.get('vendor', 'N/A')}")
    print(f"  金額: {receipt_data.get('amount', 'N/A')}")
    print(f"  日期: {receipt_data.get('date', 'N/A')}")
    print(f"  品項: {json.dumps(receipt_data.get('items', []), ensure_ascii=False)}")

    # 存 OCR 結果
    ocr_out = Path(OUTPUT_DIR) / f"{image_path.stem}_ocr.json"
    with open(ocr_out, "w", encoding="utf-8") as f:
        json.dump(receipt_data, f, ensure_ascii=False, indent=2)

    # Step 2: 確認
    confirm = input("是否填入核銷系統？(y/n): ").strip().lower()
    if confirm != "y":
        print("已跳過。")
        return

    # Step 3: 自動登入 → 導航 → 填單
    pw, browser, context = start_browser(headless=headless)
    try:
        # 登入
        menu_page = login(context)

        # 導航到核銷表單
        frames = navigate_to_expense_form(menu_page)

        # 填寫表單
        fill_expense_form(frames, receipt_data, menu_page=menu_page)

        # 截圖
        menu_page.screenshot(
            path=f"{OUTPUT_DIR}/{image_path.stem}_filled.png",
            full_page=True,
        )
        print(f"  截圖已存: {OUTPUT_DIR}/{image_path.stem}_filled.png")

        # 暫停讓使用者檢查
        input("請確認表單填寫正確後按 Enter 繼續...")

    finally:
        browser.close()
        pw.stop()

    print("完成！")


def main():
    images = get_receipt_images()
    if not images:
        print("receipts/ 目錄中沒有找到圖片。")
        print(f"請將發票/收據圖片放入 {RECEIPTS_DIR}/ 目錄。")
        sys.exit(0)

    print(f"找到 {len(images)} 張發票/收據圖片：")
    for i, img in enumerate(images, 1):
        print(f"  {i}. {img.name}")

    for image in images:
        process_single(image, headless=True)

    print("\n全部處理完成！")


if __name__ == "__main__":
    main()
