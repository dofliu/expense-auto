"""發票/收據辨識，使用 Google Gemini Vision API（google.genai 新套件）。
支援圖片（JPG/PNG/WebP）及 PDF 文件。"""

import json
import os
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image


# 使用 gemini-2.5-flash：速度快、支援 vision、適合 OCR
MODEL_NAME = "gemini-2.5-flash"

# 支援的檔案格式
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"}
PDF_EXTENSIONS = {".pdf"}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | PDF_EXTENSIONS


def _load_file_for_gemini(file_path: str):
    """
    依副檔名載入檔案，回傳適合 Gemini API 的內容物件。

    - 圖片 → PIL.Image（Gemini SDK 原生支援）
    - PDF  → types.Part.from_bytes（inline bytes + MIME type）

    Returns:
        PIL.Image 或 genai.types.Part
    """
    ext = Path(file_path).suffix.lower()

    if ext in PDF_EXTENSIONS:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        return types.Part.from_bytes(
            data=pdf_bytes,
            mime_type="application/pdf",
        )
    else:
        # 圖片：用 PIL 開啟（Gemini SDK 接受 PIL.Image）
        return Image.open(file_path)


# ── OCR Prompt（單張/多張共用欄位定義）──────────────────

_FIELDS_PROMPT = (
    "- doc_type: 文件類型 (可能的值: 'receipt'=發票/收據, 'credit_card_statement'=信用卡刷卡紀錄)\n"
    "- date: 日期 (YYYY-MM-DD)\n"
    "- vendor: 廠商/店家名稱\n"
    "- amount: 總金額 (數字，含稅總價)\n"
    "- currency: 幣別 (如 'TWD', 'USD', 'JPY'，預設 TWD)\n"
    "- original_amount: 原幣金額 (若幣別為 TWD 則同 amount，若為外幣則填原幣數字)\n"
    "- tax_id: 統一編號 (8碼，若無則為空字串)\n"
    "- invoice_no: 發票號碼 (若無則為空字串)\n"
    "- items: 品項列表，每項含 name, quantity, price（price 是單價）\n"
)

_RULES_PROMPT = (
    "特殊規則：\n"
    "1. 若發票上有「稅額」、「營業稅」、「Tax」等稅金項目，請單獨列為 items 中的一筆，"
    "name 填 '稅額' 或 '營業稅'，不要混入其他品項的 price。\n"
    "2. 若是國外收據（如 Anthropic、Google Cloud、OpenAI、AWS），"
    "請正確辨識幣別和金額。\n"
    "3. 若是信用卡刷卡紀錄/帳單，doc_type 填 'credit_card_statement'，"
    "items 中每筆交易包含 name(廠商名), quantity(1), price(台幣金額)，"
    "另外加 original_currency 和 original_price 欄位。\n"
)


def _parse_gemini_response(raw: str):
    """移除 markdown code block 包裹，解析 JSON。"""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]       # 移除第一行 ```json
        raw = raw.rsplit("```", 1)[0]     # 移除最後的 ```
        raw = raw.strip()
    return json.loads(raw)


def extract_receipt_data(file_path: str) -> dict:
    """
    辨識單張發票/收據檔案（圖片或 PDF），回傳結構化資料。

    Args:
        file_path: 圖片或 PDF 路徑

    Returns:
        dict: {
            "doc_type": "receipt",
            "date": "2026-01-15",
            "vendor": "全家便利商店",
            "amount": 150,
            "currency": "TWD",
            "original_amount": 150,
            "tax_id": "12345678",
            "invoice_no": "AB-12345678",
            "items": [{"name": "文具用品", "quantity": 1, "price": 150}]
        }
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    content = _load_file_for_gemini(file_path)

    prompt = (
        "請辨識這張發票、收據或刷卡紀錄，回傳 JSON 格式，包含以下欄位：\n"
        + _FIELDS_PROMPT + "\n" + _RULES_PROMPT +
        "只回傳 JSON，不要其他文字，不要用 markdown code block。"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, content],
        config=types.GenerateContentConfig(temperature=0.1),
    )

    return _parse_gemini_response(response.text)


def extract_multiple_receipts(file_path: str) -> list:
    """
    辨識一個檔案中的所有發票/收據（圖片可能含多張並排，PDF 可能多頁）。

    Args:
        file_path: 圖片或 PDF 路徑

    Returns:
        list[dict]: 每個 dict 格式同 extract_receipt_data()。
                    若只有一張收據，回傳含一個元素的 list。
    """
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    content = _load_file_for_gemini(file_path)

    ext = Path(file_path).suffix.lower()
    is_pdf = ext in PDF_EXTENSIONS

    # PDF 可能有多頁，提示 Gemini 逐頁辨識
    pdf_hint = (
        "這份 PDF 文件可能有多頁，每頁可能是不同的發票或收據。"
        "請逐頁辨識所有文件。\n"
    ) if is_pdf else (
        "這張圖片可能包含一張或多張發票、收據或信用卡刷卡紀錄（例如多張收據並排拍照）。\n"
    )

    prompt = (
        pdf_hint +
        "請辨識所有文件，回傳 JSON 陣列，每個元素代表一張收據或刷卡紀錄，"
        "包含以下欄位：\n"
        + _FIELDS_PROMPT + "\n" + _RULES_PROMPT +
        "若只有一張收據，回傳含一個元素的陣列 [...]。\n"
        "只回傳 JSON 陣列，不要其他文字，不要用 markdown code block。"
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, content],
        config=types.GenerateContentConfig(temperature=0.1),
    )

    result = _parse_gemini_response(response.text)

    # 防禦：若 Gemini 回傳單一 dict 而非 list
    if isinstance(result, dict):
        result = [result]

    return result


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv
    load_dotenv("credentials.env")

    if len(sys.argv) < 2:
        print("Usage: python ocr.py <file_path>")
        print("  支援格式: JPG, PNG, WebP, PDF")
        sys.exit(1)
    result = extract_receipt_data(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
