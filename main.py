"""主程式入口：掃描 receipts/ 內的發票檔案（圖片/PDF），合併辨識後填入同一張請購單。

完整流程：
    1. 掃描 receipts/ 中的所有檔案（JPG/PNG/WebP/PDF）
    2. OCR 辨識所有檔案（每張照片可能含多張收據，PDF 可能多頁）
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
from ocr import extract_multiple_receipts, extract_receipt_data
from form_filler import (
    start_browser, login, navigate_to_expense_form, fill_expense_form,
    _is_tax_item,
)

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff", ".pdf"}

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


def get_receipt_files() -> list:
    """取得 receipts/ 目錄中所有支援的收據檔案（圖片 + PDF）。"""
    receipts_dir = Path(RECEIPTS_DIR)
    if not receipts_dir.exists():
        print(f"找不到目錄: {RECEIPTS_DIR}")
        return []
    files = [
        f for f in sorted(receipts_dir.iterdir())
        if f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return files


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

def _validate_ocr_result(receipt: dict) -> bool:
    """
    驗證 OCR 結果是否有效。

    有效條件：
    1. amount > 0 或 items 中有 price > 0 的品項
    2. 有 vendor 或 items（至少能辨識出內容）
    """
    try:
        amt = float(receipt.get("amount", 0) or 0)
    except (ValueError, TypeError):
        amt = 0

    items = receipt.get("items", [])
    has_priced_items = False
    for item in items:
        try:
            p = float(item.get("price", 0) or 0)
            if p > 0:
                has_priced_items = True
                break
        except (ValueError, TypeError):
            continue

    has_vendor = bool(receipt.get("vendor", "").strip())

    # 至少要有金額或有品項
    return (amt > 0 or has_priced_items) and (has_vendor or has_priced_items)


def ocr_all_files(files: list, max_retries: int = 3) -> list:
    """
    OCR 所有檔案（圖片/PDF），每個檔案可能包含多張收據。
    回傳所有收據的 flat list，每筆附加 _source_file 欄位。

    若 OCR 失敗或結果無效，會自動重試（最多 max_retries 次）。
    多張模式失敗時，會嘗試單張模式作為備案。
    """
    all_receipts = []
    for f in files:
        ext = f.suffix.lower()
        file_type = "PDF" if ext == ".pdf" else "圖片"
        print(f"  辨識中: {f.name} ({file_type}) ...")

        receipts = None

        # ── 多張辨識模式（含重試）──
        for attempt in range(1, max_retries + 1):
            try:
                result = extract_multiple_receipts(str(f))
                # 驗證結果
                valid = [r for r in result if _validate_ocr_result(r)]
                invalid_count = len(result) - len(valid)

                if valid:
                    receipts = valid
                    if invalid_count > 0:
                        print(f"    (第{attempt}次) 辨識到 {len(result)} 筆，"
                              f"其中 {invalid_count} 筆無效已略過")
                    break
                else:
                    print(f"    (第{attempt}次) 辨識結果無效（amount=0 或無品項），重試...")
            except Exception as e:
                print(f"    (第{attempt}次) OCR 錯誤: {e}")

            if attempt < max_retries:
                import time as _time
                _time.sleep(1)  # API 重試前等 1 秒

        # ── 備案：單張辨識模式 ──
        if not receipts:
            print(f"    多張模式失敗，嘗試單張辨識模式...")
            for attempt in range(1, max_retries + 1):
                try:
                    single = extract_receipt_data(str(f))
                    if _validate_ocr_result(single):
                        receipts = [single]
                        print(f"    單張模式成功！")
                        break
                    else:
                        print(f"    (單張第{attempt}次) 結果無效，重試...")
                except Exception as e:
                    print(f"    (單張第{attempt}次) 錯誤: {e}")

                if attempt < max_retries:
                    import time as _time
                    _time.sleep(1)

        # ── 最終結果 ──
        if receipts:
            n = len(receipts)
            label = "" if n == 1 else f"（含 {n} 張收據）"
            print(f"    -> 完成{label}")
            for r in receipts:
                r["_source_image"] = f.name   # 保持欄位名稱相容
            all_receipts.extend(receipts)
        else:
            print(f"    [ERROR] {f.name} OCR 完全失敗（重試 {max_retries} 次仍無有效結果）")
            print(f"    請檢查該檔案是否損毀，或嘗試重新擷取/拍照")

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
        currency = r.get("currency", "TWD")
        currency_label = ""
        if currency != "TWD":
            orig_amt = r.get("original_amount", "")
            currency_label = f"  [原幣: {currency} {orig_amt}]"
            if r.get("_matched_twd"):
                currency_label += f" → 刷卡台幣: NT${r['_matched_twd']}"
        print(f"  [{i}]{src_label}")
        print(f"      廠商: {r.get('vendor', '?')}  日期: {r.get('date', '?')}"
              f"  金額: NT${amt}{inv_label}{currency_label}")
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
#  外幣收據 ↔ 信用卡刷卡紀錄交叉比對
# ════════════════════════════════════════════════════════════

def match_foreign_receipts_to_statements(all_docs: list) -> list:
    """
    將外幣收據與信用卡刷卡紀錄進行交叉比對。

    流程：
    1. 從 all_docs 中區分出 receipts 和 credit_card_statements
    2. 對每張外幣收據，在刷卡紀錄的交易明細中搜尋匹配項
    3. 匹配依據：日期相近（±7天）+ 原幣金額吻合 + 廠商名稱模糊匹配
    4. 匹配成功 → 用刷卡紀錄的台幣金額覆蓋收據的 amount

    Args:
        all_docs: OCR 辨識後的全部文件列表（含收據與刷卡紀錄）

    Returns:
        list: 僅包含收據的列表（不含刷卡紀錄本身），外幣收據已替換為台幣金額
    """
    receipts = []
    statements = []

    for doc in all_docs:
        doc_type = doc.get("doc_type", "receipt")
        if doc_type == "credit_card_statement":
            statements.append(doc)
        else:
            receipts.append(doc)

    if statements:
        print(f"\n  找到 {len(statements)} 張信用卡刷卡紀錄，開始交叉比對...")

    # 彙整所有刷卡紀錄中的交易明細
    all_transactions = []
    for stmt in statements:
        stmt_items = stmt.get("items", [])
        for item in stmt_items:
            all_transactions.append({
                "name": item.get("name", ""),
                "twd_amount": item.get("price", 0),
                "original_currency": item.get("original_currency", ""),
                "original_price": item.get("original_price", 0),
                "date": stmt.get("date", ""),
                "_used": False,
            })

    # 對每張外幣收據嘗試比對
    for receipt in receipts:
        currency = receipt.get("currency", "TWD")
        if currency == "TWD":
            continue  # 國內發票不需要比對

        orig_amount = receipt.get("original_amount", receipt.get("amount", 0))
        try:
            orig_amount = float(orig_amount)
        except (ValueError, TypeError):
            orig_amount = 0

        vendor = receipt.get("vendor", "").lower()
        receipt_date = receipt.get("date", "")

        best_match = None
        best_score = 0

        for txn in all_transactions:
            if txn["_used"]:
                continue

            score = 0

            # 廠商名稱模糊比對（部分匹配即可）
            txn_name = txn["name"].lower()
            if vendor and txn_name:
                # 檢查任一方是否包含另一方的關鍵部分
                vendor_words = [w for w in vendor.split() if len(w) > 2]
                for word in vendor_words:
                    if word in txn_name:
                        score += 3
                        break
                if any(w in vendor for w in txn_name.split() if len(w) > 2):
                    score += 3

            # 原幣金額比對
            txn_orig = float(txn.get("original_price", 0) or 0)
            if txn_orig > 0 and abs(txn_orig - orig_amount) < 0.01:
                score += 5  # 原幣金額完全吻合 → 強匹配
            elif txn.get("original_currency", "").upper() == currency.upper():
                score += 1  # 至少幣別相同

            # 日期相近度（刷卡因時區差異可能前後差 1 天）
            if receipt_date and txn["date"]:
                try:
                    from datetime import datetime
                    r_date = datetime.strptime(receipt_date, "%Y-%m-%d")
                    t_date = datetime.strptime(txn["date"], "%Y-%m-%d")
                    day_diff = abs((r_date - t_date).days)
                    if day_diff <= 1:
                        score += 3  # ±1天：高度吻合（時區差異）
                    elif day_diff <= 3:
                        score += 2
                    elif day_diff <= 7:
                        score += 1
                except (ValueError, TypeError):
                    pass

            if score > best_score:
                best_score = score
                best_match = txn

        # 判斷是否達到可信的匹配門檻
        if best_match and best_score >= 5:
            try:
                twd_amount = int(float(best_match["twd_amount"]))
            except (ValueError, TypeError):
                twd_amount = 0

            if twd_amount > 0:
                best_match["_used"] = True
                receipt["_matched_twd"] = twd_amount
                receipt["amount"] = twd_amount
                receipt["_original_currency"] = currency
                receipt["_original_amount"] = orig_amount
                print(f"    ✓ {receipt.get('vendor', '?')} {currency} {orig_amount}"
                      f" → 刷卡台幣 NT${twd_amount} (匹配分數: {best_score})")
            else:
                print(f"    ✗ {receipt.get('vendor', '?')} 匹配到但台幣金額無效")
        elif currency != "TWD":
            print(f"    ⚠ {receipt.get('vendor', '?')} {currency} {orig_amount}"
                  f" → 未找到匹配的刷卡紀錄 (最高分數: {best_score})")
            print(f"      請手動確認台幣金額！")

    return receipts


# ════════════════════════════════════════════════════════════
#  外幣收據正規化（品名、發票號碼、匯率警告）
# ════════════════════════════════════════════════════════════

# AI 服務品名對照表（vendor 關鍵字 → 標準品名）
_AI_SERVICE_NAMES = {
    "google":    "Google Gemini AI服務費",
    "gemini":    "Google Gemini AI服務費",
    "anthropic": "Claude AI服務費",
    "claude":    "Claude AI服務費",
    "openai":    "ChatGPT AI服務費",
    "chatgpt":   "ChatGPT AI服務費",
    "microsoft": "Microsoft AI服務費",
    "azure":     "Microsoft Azure AI服務費",
    "aws":       "AWS AI服務費",
    "amazon":    "AWS AI服務費",
}


def _get_ai_service_name(vendor: str) -> str:
    """根據廠商名稱，回傳標準化的 AI 服務品名。找不到則回傳 None。"""
    v_lower = vendor.lower()
    for keyword, name in _AI_SERVICE_NAMES.items():
        if keyword in v_lower:
            return name
    return None


def normalize_foreign_receipts(receipts: list) -> list:
    """
    正規化外幣收據：
    1. AI 服務品名標準化（Google→Google Gemini AI服務費 等）
    2. 外幣收據清空 invoice_no（用收據流水號取代，避免格式不符導致存入失敗）
    3. 檢查外幣收據是否有台幣金額（未匹配到刷卡紀錄時暫停警告）

    應在 match_foreign_receipts_to_statements() 之後呼叫。
    """
    has_unmatched_foreign = False

    for receipt in receipts:
        currency = receipt.get("currency", "TWD")
        vendor = receipt.get("vendor", "")

        if currency == "TWD":
            # 國內收據也檢查 AI 服務品名（如 Google Cloud 台灣開發票的情況）
            ai_name = _get_ai_service_name(vendor)
            if ai_name:
                items = receipt.get("items", [])
                for item in items:
                    old_name = item.get("name", "")
                    if not _is_tax_item(old_name):
                        item["name"] = ai_name
                print(f"    [AI品名] {vendor} → 品項統一為 '{ai_name}'")
            continue

        # ── 外幣收據處理 ──

        # (1) AI 服務品名標準化
        ai_name = _get_ai_service_name(vendor)
        if ai_name:
            items = receipt.get("items", [])
            for item in items:
                old_name = item.get("name", "")
                if not _is_tax_item(old_name):
                    item["name"] = ai_name
            print(f"    [AI品名] {vendor} → 品項統一為 '{ai_name}'")

        # (2) 清空 invoice_no（外幣收據格式不符學校系統，改用收據流水號）
        if receipt.get("invoice_no"):
            print(f"    [發票號] {vendor}: 清除外幣 invoice '{receipt['invoice_no']}' → 改用收據流水號")
            receipt["invoice_no"] = ""

        # (3) 外幣收據已匹配台幣 → 將所有品項合併為一筆（台幣金額）
        #     原因：OCR 品項價格是外幣原價，直接進入稅額處理會產生錯誤的「其他差額」
        #     例：Claude USD$5 → 刷卡 NT$158 → 應合併為「Claude AI服務費 158」
        if receipt.get("_matched_twd"):
            twd_amount = receipt["_matched_twd"]
            items = receipt.get("items", [])
            # 找主品名：AI 服務標準名 > 第一個非稅品項名 > 廠商名
            main_name = ai_name
            if not main_name:
                for item in items:
                    if not _is_tax_item(item.get("name", "")):
                        main_name = item.get("name", "")
                        break
            if not main_name:
                main_name = vendor or "核銷明細"
            # 取得 spec（規格）：保留第一個品項的 spec
            main_spec = ""
            for item in items:
                if not _is_tax_item(item.get("name", "")) and item.get("spec"):
                    main_spec = item["spec"]
                    break
            # 合併為單一品項
            consolidated = {
                "name": main_name,
                "quantity": 1,
                "price": twd_amount,
            }
            if main_spec:
                consolidated["spec"] = main_spec
            receipt["items"] = [consolidated]
            print(f"    [外幣合併] {vendor}: 合併為 '{main_name}' NT${twd_amount}")

        # (4) 檢查是否有台幣金額
        if not receipt.get("_matched_twd"):
            has_unmatched_foreign = True
            orig_amt = receipt.get("original_amount", receipt.get("amount", "?"))
            print(f"\n    *** 警告: {vendor} 為外幣收據 ({currency} {orig_amt}) ***")
            print(f"    *** 未找到對應的刷卡紀錄，目前金額 NT${receipt.get('amount', 0)} 可能不正確！ ***")
            print(f"    *** 建議: 將信用卡帳單圖片/PDF 一併放入 receipts/ 目錄重新辨識 ***")

    if has_unmatched_foreign:
        print(f"\n  ──────────────────────────────────────────────")
        print(f"  有外幣收據尚未匹配到刷卡紀錄！")
        print(f"  請確認以下任一方式提供台幣金額：")
        print(f"    1. 將信用卡月結單/刷卡明細的圖片或 PDF 放入 receipts/ 目錄")
        print(f"    2. 手動修改 output/ 中的 OCR JSON 檔，將 amount 改為台幣金額")
        print(f"  ──────────────────────────────────────────────")

        user_continue = _timed_input(
            "\n  外幣收據金額可能有誤，是否仍要繼續？(y/n, 15秒後自動取消): ",
            timeout=15, default="n"
        ).strip().lower()
        if user_continue != "y":
            print("  已取消。請加入刷卡紀錄後重新執行。")
            sys.exit(0)

    return receipts


# ════════════════════════════════════════════════════════════
#  每張收據的稅額預處理
# ════════════════════════════════════════════════════════════

def _process_receipt_tax(receipt: dict) -> list:
    """
    針對單張收據做稅額智慧處理，回傳處理後的品項列表。

    稅額處理規則（根據使用者說明）：
      Case A: 單品項 + 稅額 → 合併為一筆（用收據總金額作為該品項價格）
              例: 三相整流橋 457 + 稅額 23 → 三相整流橋 480
      Case B: 多品項 + 稅額 → 檢查品項合計是否已含稅
              - 若品項合計 == 收據金額 → 稅已含（營業稅僅為資訊），保留品項不加稅
              - 若品項合計 + 稅額 == 收據金額 → 品項為未稅價，加「其他差額」
              - 其他情況 → 補差額到收據金額
      Case C: 無稅額 → 直接使用品項

    Returns:
        處理後的品項列表，每筆格式: {"name", "quantity", "price", "spec"(可選)}
    """
    items = receipt.get("items", [])
    try:
        amount = int(float(receipt.get("amount", 0)))
    except (ValueError, TypeError):
        amount = 0

    if not items:
        # 無品項明細 → 用廠商名+總金額建立代表品項
        return [{
            "name": receipt.get("vendor", "核銷明細"),
            "quantity": 1,
            "price": amount,
        }]

    tax_items = [i for i in items if _is_tax_item(i.get("name", ""))]
    regular_items = [i for i in items if not _is_tax_item(i.get("name", ""))]

    if not regular_items:
        # 只有稅額項目？不太可能，但保險起見用總金額
        return [{
            "name": receipt.get("vendor", "核銷明細"),
            "quantity": 1,
            "price": amount,
        }]

    # 計算各項合計
    def _item_total(item):
        try:
            q = int(float(item.get("quantity", 1)))
        except (ValueError, TypeError):
            q = 1
        try:
            p = int(float(item.get("price", 0)))
        except (ValueError, TypeError):
            p = 0
        return p * q

    regular_sum = sum(_item_total(i) for i in regular_items)
    tax_sum = sum(_item_total(i) for i in tax_items)

    if not tax_items:
        # ── Case C: 無稅額 → 直接使用品項 ──
        result = list(regular_items)
        diff = amount - regular_sum
        if diff > 0:
            result.append({"name": "其他差額", "quantity": 1, "price": diff})
        return result

    if len(regular_items) == 1:
        # ── Case A: 單品項 + 稅額 → 合併（用收據總金額） ──
        item = regular_items[0]
        return [{
            "name": item.get("name", ""),
            "spec": item.get("spec", ""),
            "quantity": 1,
            "price": amount,   # 用收據總金額（已含稅）
        }]

    # ── Case B: 多品項 + 稅額 ──
    result = list(regular_items)

    if regular_sum == amount:
        # 品項合計 == 收據金額 → 稅已含在品項價格中，不加稅
        pass
    elif abs(regular_sum + tax_sum - amount) <= 1:
        # 品項 + 稅額 ≈ 收據金額 → 品項為未稅價，加「其他差額」
        result.append({"name": "其他差額", "spec": "稅額", "quantity": 1, "price": tax_sum})
    else:
        # 其他情況 → 用收據金額補差額
        diff = amount - regular_sum
        if diff > 0:
            result.append({"name": "其他差額", "quantity": 1, "price": diff})
        elif diff < 0:
            # 品項合計 > 收據金額，可能 OCR 有誤，但不壓縮成一行
            # 保留品項，讓使用者自行檢查
            pass

    return result


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

    # 單張也做稅額預處理
    if len(receipts) == 1:
        r = receipts[0]
        processed = _process_receipt_tax(r)
        result = dict(r)  # shallow copy
        result["items"] = processed
        return result

    all_items = []
    total_amount = 0
    dates = []
    vendors = []

    for r in receipts:
        # 每張收據先做稅額預處理，再合併品項
        processed = _process_receipt_tax(r)
        all_items.extend(processed)

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
        images = get_receipt_files()
        if not images:
            print(f"receipts/ 目錄中沒有找到收據檔案。")
            print(f"請將發票/收據檔案放入 {RECEIPTS_DIR}/ 目錄。")
            print(f"支援格式: 圖片(JPG/PNG/WebP) 及 PDF")
            sys.exit(0)

        pdf_count = sum(1 for f in images if f.suffix.lower() == ".pdf")
        img_count = len(images) - pdf_count
        parts = []
        if img_count > 0:
            parts.append(f"{img_count} 張圖片")
        if pdf_count > 0:
            parts.append(f"{pdf_count} 份 PDF")
        print(f"\n找到 {'、'.join(parts)}：")
        for i, img in enumerate(images, 1):
            print(f"  {i}. {img.name}")

        # ── Step 2: OCR 所有檔案 ──────────────────────
        print("\n開始辨識...")
        all_receipts = ocr_all_files(images)

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

        # ── Step 2.5: 外幣收據 ↔ 刷卡紀錄交叉比對 ─────
        # 從 all_receipts 中分離出刷卡紀錄，並為外幣收據匹配台幣金額
        all_receipts = match_foreign_receipts_to_statements(all_receipts)

        # ── Step 2.6: 外幣收據正規化 ─────────────────
        # AI 服務品名標準化 + 清空外幣 invoice_no + 未匹配匯率警告
        all_receipts = normalize_foreign_receipts(all_receipts)

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
