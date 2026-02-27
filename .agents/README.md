# NCUT 核銷自動填單系統 — Agent 指引

## 專案概述

本專案是勤益科技大學 (NCUT) 會計核銷系統的**自動填單工具**。  
核心流程：`掃描發票圖片 → Gemini Vision OCR 辨識 → 自動登入核銷系統 → 填寫「直接核銷（零用金）」表單`。

- **語言**：Python 3.10+
- **平台**：Windows（主要測試環境）
- **GitHub**：<https://github.com/dofliu/expense-auto>

---

## 技術棧

| 技術 | 用途 |
|------|------|
| **Playwright** | 瀏覽器自動化（登入、導航、填表） |
| **Google Gemini Vision API** | OCR 辨識發票圖片 + 驗證碼辨識 |
| **python-dotenv** | 載入 `credentials.env` 機敏設定 |
| **Pillow** | 圖片處理（截取驗證碼區域） |

---

## 專案結構

```
expense-auto/
├── credentials.env        # 帳密和 API Key（不進版控）
├── config.py              # 集中設定：URL、欄位名稱、科目對照
├── ocr.py                 # Gemini Vision OCR 辨識發票圖片
├── form_filler.py         # Playwright 自動化：登入、導航、填單（核心，808 行）
├── main.py                # 主程式入口：批次掃描 receipts/
├── requirements.txt       # Python 套件：playwright, google-generativeai, python-dotenv, pillow
├── .gitignore
│
├── receipts/              # 輸入：待處理的發票圖片 (.jpg/.jpeg/.png/.webp)
├── output/                # 輸出：OCR JSON、填單截圖、驗證碼暫存
│
├── inspect_appy.py        # 開發工具：分析 APPY frame 結構
├── inspect_budget.py      # 開發工具：查詢可用預算和科目
├── inspect_tran.py        # 開發工具：分析 TRAN frame 資料
├── inspect_menu.py        # 開發工具：分析選單結構
├── inspect_pages.py       # 開發工具：分析頁面結構
├── test_login.py          # 開發工具：測試登入功能
└── printer.py             # 開發工具：輔助列印
```

---

## 核心模組

### `config.py` — 設定中心

- 從 `credentials.env` 載入帳密與 API Key
- 定義所有 CSS selector、欄位名稱、會計科目
- 目標系統為 **Big5 編碼的 ASP 架構**，使用多層 frameset

### `ocr.py` — 發票辨識

- 呼叫 `gemini-3.1-pro-preview` 模型
- 輸入：圖片路徑 → 輸出：結構化 JSON（date, vendor, amount, tax_id, invoice_no, items）
- 獨立可用：`python ocr.py <image_path>`

### `form_filler.py` — 核心自動化（808 行）

- **`start_browser()`**：啟動 Playwright Chromium
- **`solve_captcha()`**：截圖驗證碼 → Gemini 辨識
- **`login()`**：填入帳密 + 驗證碼，處理新視窗彈出（最多重試 5 次）
- **`navigate_to_expense_form()`**：操作 4 層巢狀 frameset，導航至核銷表單
- **`fill_expense_form()`**：整合填寫，包含三個子區塊：
  - `fill_appy_frame()` — 經費表頭（計畫編號→經費用途→科目→金額，級聯 dropdown）
  - APPP frame — 品名明細（用途說明、憑證日期、品名數量單價）
  - `fill_appa_frame()` — 受款人（代墊、收據號碼、日期、受款人代碼、銀行帳戶、金額）
- **`verify_and_save()`**：驗證三個區塊金額一致後自動存入

### `main.py` — 主程式入口

- 批次處理 `receipts/` 中的所有圖片
- 流程：選擇計畫 → OCR → 確認 → 登入 → 填單 → 截圖
- 支援命令列參數：`--plan`, `--no-save`, `--headless`, `--ocr-only`

---

## 核銷系統 Frame 結構

```
DA_SerBug_Menu_Q.asp (主選單 frameset)
├── TITLE  — 功能選單列
├── MAIN   — 主內容區（核銷表單載入此處）
├── OT     — 共用功能 (hidden)
├── CK_VN  — 廠商檢核 (hidden)
├── LA_AM  — 金額相關 (hidden)
├── TRAN   — 傳輸相關 (hidden)
└── OTHER  — 空白頁 (hidden)

STD_APPY_FRM_Q.asp (核銷表單 frameset, 載入 MAIN)
├── APPY   — 表頭：計畫經費、科目、金額
├── APPP   — 品項明細：品名、數量、單價
├── APPA   — 受款人：發票號碼、日期、受款人、銀行帳戶
└── PS     — 存檔 handler (hidden)
```

> **重要**：目標系統是舊式 ASP 架構，所有互動都在多層 frameset 中進行，需要精確的 frame 引用。

---

## 日期處理

- 核銷系統使用**民國年**（如 115 年 = 2026 年）
- OCR 回傳 ISO 格式 `YYYY-MM-DD`
- `_roc_date()` 轉換為 (年, 月, 日) tuple
- `_idate_format()` 轉換為 7 位數字（如 `1150226`）
- 收據號碼格式：`收據115022601` = 收據 + 民國年月日 + 流水號

---

## 環境設定

### credentials.env（不進版控）

```env
SYSTEM_URL=https://account.ncut.edu.tw/APSWIS_Q/Login_L_Q.asp
NCUT_USERNAME=員工編號
NCUT_PASSWORD=密碼
GEMINI_API_KEY=Google_Gemini_API_Key
```

### 安裝

```bash
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

---

## 開發注意事項

1. **不要自動送出存檔**：系統設計上在填單後需人工確認再存檔（`auto_save` 參數可控制）
2. **驗證碼重試**：登入預設最多重試 5 次驗證碼辨識
3. **Big5 編碼**：目標核銷系統為 Big5，Playwright 處理時需注意編碼
4. **Frame 操作**：所有表單互動必須在正確的 Frame 中執行，不能直接操作 page
5. **級聯 Dropdown**：APPY frame 的計畫→經費→科目是連動 dropdown，選擇後需等待載入
6. **機敏資訊**：`credentials.env` 含帳密，確保不進版控
7. **`inspect_*.py`**：這些是開發分析工具，一般使用不需執行；修改表單欄位前可先用它們分析系統結構
