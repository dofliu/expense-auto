"""發票/收據圖片辨識，使用 Google Gemini Vision API（google.genai 新套件）。"""

import json
import os
from pathlib import Path

from google import genai
from PIL import Image


# 使用 gemini-2.5-flash：速度快、支援 vision、適合 OCR
MODEL_NAME = "gemini-2.5-flash"


def extract_receipt_data(image_path: str) -> dict:
    """
    辨識發票/收據圖片，回傳結構化資料。

    Returns:
        dict: {
            "date": "2026-01-15",
            "vendor": "全家便利商店",
            "amount": 150,
            "tax_id": "12345678",
            "invoice_no": "AB-12345678",
            "items": [{"name": "文具用品", "quantity": 1, "price": 150}]
        }
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    image = Image.open(image_path)

    prompt = (
        "請辨識這張台灣發票或收據，回傳 JSON 格式，包含以下欄位：\n"
        "- date: 日期 (YYYY-MM-DD)\n"
        "- vendor: 廠商/店家名稱\n"
        "- amount: 總金額 (數字)\n"
        "- tax_id: 統一編號 (8碼，若無則為空字串)\n"
        "- invoice_no: 發票號碼 (若無則為空字串)\n"
        "- items: 品項列表，每項含 name, quantity, price（price 是單價）\n"
        "只回傳 JSON，不要其他文字，不要用 markdown code block。"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, image],
    )
    raw = response.text.strip()

    # 移除可能的 markdown code block 包裹
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]  # 移除第一行 ```json
        raw = raw.rsplit("```", 1)[0]  # 移除最後的 ```
        raw = raw.strip()

    return json.loads(raw)


def extract_multiple_receipts(image_path: str) -> list:
    """
    辨識一張圖片中的所有發票/收據（圖片可能同時含多張）。

    Args:
        image_path: 圖片路徑

    Returns:
        list[dict]: 每個 dict 格式同 extract_receipt_data()。
                    若圖片只有一張收據，回傳含一個元素的 list。
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    image = Image.open(image_path)

    prompt = (
        "這張圖片可能包含一張或多張台灣發票或收據（例如多張收據並排拍照）。\n"
        "請辨識圖中所有收據，回傳 JSON 陣列，每個元素代表一張收據，"
        "包含以下欄位：\n"
        "- date: 日期 (YYYY-MM-DD)\n"
        "- vendor: 廠商/店家名稱\n"
        "- amount: 總金額 (數字)\n"
        "- tax_id: 統一編號 (8碼，若無則為空字串)\n"
        "- invoice_no: 發票號碼 (若無則為空字串)\n"
        "- items: 品項列表，每項含 name, quantity, price（price 是單價）\n"
        "若圖片只有一張收據，回傳含一個元素的陣列 [...]。\n"
        "只回傳 JSON 陣列，不要其他文字，不要用 markdown code block。"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, image],
    )
    raw = response.text.strip()

    # 移除可能的 markdown code block 包裹
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0].strip()

    result = json.loads(raw)

    # 防禦：若 Gemini 回傳單一 dict 而非 list（理應是 list）
    if isinstance(result, dict):
        result = [result]

    return result


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv
    load_dotenv("credentials.env")

    if len(sys.argv) < 2:
        print("Usage: python ocr.py <image_path>")
        sys.exit(1)
    result = extract_receipt_data(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
