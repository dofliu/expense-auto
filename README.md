# NCUT 核銷自動填單系統

勤益科技大學會計核銷系統的自動填單工具。
掃描發票/收據圖片 → Gemini Vision OCR 辨識 → 自動登入系統 → 填寫「直接核銷（零用金）」表單。

---

## 目錄

- [功能概述](#功能概述)
- [環境需求](#環境需求)
- [安裝步驟](#安裝步驟)
- [設定憑證](#設定憑證)
- [使用方法](#使用方法)
  - [批次處理（推薦）](#批次處理推薦)
  - [單獨 OCR 辨識](#單獨-ocr-辨識)
  - [單獨測試填單](#單獨測試填單)
- [會計科目對照表](#會計科目對照表)
- [專案架構](#專案架構)
- [常見問題](#常見問題)

---

## 功能概述

| 步驟 | 說明 | 模組 |
|------|------|------|
| 1. OCR 辨識 | 用 Google Gemini Vision API 辨識發票圖片 | `ocr.py` |
| 2. 自動登入 | 自動填入帳密 + AI 驗證碼辨識 | `form_filler.py` |
| 3. 選單導航 | 自動操作 4 層巢狀 frameset，開啟核銷表單 | `form_filler.py` |
| 4. 表單填寫 | 自動填入品項、日期、金額、會計科目 | `form_filler.py` |

> **目前支援**：「直接核銷（零用金）」類型
> **尚未支援**：送出存檔（需手動確認後存檔）、廠商/發票號碼欄位（APPA frame）

---

## 環境需求

- **Python** 3.10 以上
- **Google Gemini API Key**（用於 OCR 和驗證碼辨識）
- **Windows**（測試環境；Linux/macOS 理論上相容但尚未驗證）

---

## 安裝步驟

### 1. 建立虛擬環境（建議）

```bash
cd expense-auto
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 2. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

### 3. 安裝 Playwright 瀏覽器

```bash
playwright install chromium
```

---

## 設定憑證

在專案根目錄建立 `credentials.env` 檔（此檔已在 `.gitignore` 中排除）：

```env
SYSTEM_URL=https://account.ncut.edu.tw/APSWIS_Q/Login_L_Q.asp
NCUT_USERNAME=你的員工編號
NCUT_PASSWORD=你的密碼
GEMINI_API_KEY=你的_Google_Gemini_API_Key
```

### 如何取得 Gemini API Key

1. 前往 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 點擊「Create API Key」
3. 將產生的 Key 填入 `credentials.env` 的 `GEMINI_API_KEY`

---

## 使用方法

### 批次處理（推薦）

最簡單的使用方式：把發票圖片丟進 `receipts/` 資料夾，然後執行主程式。

**步驟：**

1. 將發票/收據圖片放入 `receipts/` 資料夾
   支援格式：`.jpg`、`.jpeg`、`.png`、`.webp`

2. 執行主程式：
   ```bash
   python main.py
   ```

3. 程式會逐一處理每張圖片：
   - **OCR 辨識** → 顯示辨識結果（廠商、金額、日期、品項）
   - **詢問確認** → 輸入 `y` 繼續填單，或 `n` 跳過
   - **自動填單** → 登入系統、導航、填寫表單
   - **截圖存檔** → 填寫完的畫面截圖存到 `output/`
   - **等待確認** → 按 Enter 後處理下一張

4. 填單完成後，**請自行在系統中確認並存檔**。

### 單獨 OCR 辨識

只想辨識發票圖片，不填單：

```bash
python ocr.py receipts/invoice_001.jpg
```

輸出範例：
```json
{
  "date": "2026-01-15",
  "vendor": "全家便利商店",
  "amount": 150,
  "tax_id": "12345678",
  "invoice_no": "AB-12345678",
  "items": [
    {"name": "文具用品", "quantity": 1, "price": 150}
  ]
}
```

### 單獨測試填單

用程式內建的測試資料測試登入和填單流程：

```bash
python form_filler.py
```

這會用預設的假資料（全家便利商店 150 元文具用品）跑完整個流程，
方便確認帳號密碼是否正確、系統是否可以正常存取。

---

## 會計科目對照表

預設科目為 `110704-8012`（材料及用品費），可在 `config.py` 修改 `DEFAULT_SUBJECT`。

零用金常用科目：

| 科目代碼 | 名稱 | 適用情境 |
|----------|------|----------|
| `110704-8012` | 管理及總務費用-材料及用品費 | 辦公用品、文具 |
| `110704-8013` | 管理及總務費用-服務費用 | 印刷、廣告 |
| `110704-8014` | 管理及總務費用-維護費 | 設備維修 |
| `110704-8016` | 管理及總務費用-郵電費 | 郵寄、快遞 |
| `110704-8023` | 教學研究及訓輔費用-材料及用品費 | 教學相關用品 |
| `110704-8022` | 教學研究及訓輔費用-服務費用 | 教學相關服務 |

如需其他科目，完整清單請參考 `output/subjects.txt`（執行 `inspect_budget.py` 後產生）。

### 自訂科目

在 OCR 辨識結果中加入 `subject_code` 欄位即可指定：

```python
receipt_data = {
    "date": "2026-01-15",
    "vendor": "全家便利商店",
    "amount": 150,
    "items": [{"name": "文具用品", "quantity": 1, "price": 150}],
    "subject_code": "110704-8013"   # 改用「服務費用」
}
```

---

## 專案架構

```
expense-auto/
├── credentials.env        # 帳密和 API Key（不進版控）
├── config.py              # 所有設定：URL、欄位名稱、科目對照
├── ocr.py                 # Gemini Vision OCR 辨識發票圖片
├── form_filler.py         # Playwright 自動化：登入、導航、填單
├── main.py                # 主程式：批次掃描 receipts/ 資料夾
├── requirements.txt       # Python 套件清單
├── .gitignore
│
├── receipts/              # 放入待處理的發票圖片
│   └── .gitkeep
│
├── output/                # 程式輸出（OCR JSON、截圖等）
│   ├── *_ocr.json         # 每張發票的 OCR 辨識結果
│   ├── *_filled.png       # 填單完成截圖
│   └── captcha_tmp.png    # 驗證碼暫存圖片
│
├── inspect_appy.py        # 開發工具：分析 APPY frame 結構
├── inspect_budget.py      # 開發工具：查詢可用預算和科目
├── inspect_tran.py        # 開發工具：分析 TRAN frame 資料
├── inspect_menu.py        # 開發工具：分析選單結構
├── inspect_pages.py       # 開發工具：分析頁面結構
├── test_login.py          # 開發工具：測試登入功能
└── printer.py             # 開發工具：輔助列印
```

### 核心模組說明

| 檔案 | 用途 |
|------|------|
| `config.py` | 集中管理所有設定：系統 URL、帳密讀取、表單欄位名稱、會計科目 |
| `ocr.py` | 呼叫 Gemini Vision API 辨識發票圖片，回傳結構化 JSON |
| `form_filler.py` | 4 大功能：`solve_captcha()`（驗證碼辨識）、`login()`（登入）、`navigate_to_expense_form()`（選單導航）、`fill_expense_form()`（表單填寫） |
| `main.py` | 組合上述模組，批次處理 `receipts/` 中的所有圖片 |

### `inspect_*.py` 開發工具

這些檔案是開發過程中用來分析核銷系統的工具，一般使用不需要執行。

如果需要查看系統目前可用的預算計畫或科目清單：
```bash
python inspect_budget.py
```

---

## 常見問題

### Q: 驗證碼一直辨識錯誤？

系統會自動重試最多 5 次。如果持續失敗，可能是：
- Gemini API Key 過期或額度用完
- 網路連線不穩定
- 系統維護中

### Q: 登入後出現「帳號密碼錯誤」？

確認 `credentials.env` 中的帳密正確。注意：
- `NCUT_USERNAME` 是員工編號（純數字）
- `NCUT_PASSWORD` 是密碼（注意特殊字元）
- 使用 `NCUT_` 前綴避免和 Windows 系統環境變數衝突

### Q: 表單填寫後還需要做什麼？

目前系統**不會自動存檔**。填寫完成後：
1. 仔細檢查表單內容是否正確
2. 手動點擊「存檔」按鈕
3. 確認系統回傳成功訊息

### Q: 可以修改預設的會計科目嗎？

可以。修改 `config.py` 中的 `DEFAULT_SUBJECT`：
```python
DEFAULT_SUBJECT = "110704-8013"  # 改為服務費用
```

### Q: 如果要處理非零用金的核銷？

目前只支援「直接核銷（零用金）」。其他類型的核銷流程不同，
需要修改 `config.py` 中的 `EXPENSE_CATEGORY` 以及 `form_filler.py` 的導航邏輯。

### Q: output/ 中的檔案可以刪除嗎？

可以。`output/` 中的檔案都是程式產生的暫存/輸出：
- `*_ocr.json`：OCR 辨識結果備份
- `*_filled.png`：填單截圖供確認
- `captcha_tmp.png`：驗證碼暫存

---

## 注意事項

- 本工具僅自動填寫表單，**不會自動送出存檔**，請務必人工確認後再存檔
- `credentials.env` 含敏感資訊，請勿分享或上傳至版控
- 核銷系統為 Big5 編碼的舊式 ASP 架構，如系統改版可能需更新程式
- 日期使用民國年（如 115 年 = 2026 年）
