"""發票/收據圖片辨識，使用 Google Gemini Vision API。"""

import json
import os
from pathlib import Path

import google.generativeai as genai
from PIL import Image


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
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    model = genai.GenerativeModel("gemini-3.1-pro-preview")
    image = Image.open(image_path)

    prompt = (
        "請辨識這張台灣發票或收據，回傳 JSON 格式，包含以下欄位：\n"
        "- date: 日期 (YYYY-MM-DD)\n"
        "- vendor: 廠商/店家名稱\n"
        "- amount: 總金額 (數字)\n"
        "- tax_id: 統一編號 (8碼，若無則為空字串)\n"
        "- invoice_no: 發票號碼 (若無則為空字串)\n"
        "- items: 品項列表，每項含 name, quantity, price\n"
        "只回傳 JSON，不要其他文字，不要用 markdown code block。"
    )

    response = model.generate_content([prompt, image])
    raw = response.text.strip()

    # 移除可能的 markdown code block 包裹
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]  # 移除第一行 ```json
        raw = raw.rsplit("```", 1)[0]  # 移除最後的 ```
        raw = raw.strip()

    return json.loads(raw)


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv
    load_dotenv("credentials.env")

    if len(sys.argv) < 2:
        print("Usage: python ocr.py <image_path>")
        sys.exit(1)
    result = extract_receipt_data(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
