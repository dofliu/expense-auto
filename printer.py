"""列印觸發：將核銷單輸出為 PDF 或觸發列印。"""

from pathlib import Path

from config import OUTPUT_DIR


def save_as_pdf(page, filename: str) -> str:
    """
    將目前頁面存為 PDF。

    Args:
        page: Playwright page 物件
        filename: 輸出檔名（不含路徑）

    Returns:
        str: PDF 完整路徑
    """
    output_path = Path(OUTPUT_DIR) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page.pdf(path=str(output_path), format="A4")
    print(f"已儲存 PDF: {output_path}")
    return str(output_path)


def trigger_print(page):
    """觸發瀏覽器列印對話框。"""
    page.evaluate("window.print()")
