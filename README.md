# NCUT 核銷自動填單系統

勤益科技大學會計核銷系統的自動填單工具。
掃描發票/收據圖片或 PDF → Gemini Vision OCR 辨識 → 自動登入系統 → 填寫「直接核銷（零用金）」表單 → 自動存檔並產生 PDF。

---

## 目錄

- [功能概述](#功能概述)
- [環境需求](#環境需求)
- [安裝步驟](#安裝步驟)
- [設定憑證](#設定憑證)
- [使用方法](#使用方法)
  - [批次處理（推薦）](#批次處理推薦)
  - [單獨 OCR 辨識](#單獨-ocr-辨識)
  - [進階選項](#進階選項)
- [外幣收據處理](#外幣收據處理)
- [會計科目對照表](#會計科目對照表)
- [專案架構](#專案架構)
- [常見問題](#常見問題)
- [已知限制與注意事項](#已知限制與注意事項)

---

## 功能概述

| 步驟 | 說明 | 模組 |
|------|------|------|
| 1. OCR 辨識 | Gemini Vision API 辨識發票圖片/PDF，支援多張收據 | `ocr.py` |
| 2. 外幣處理 | 自動比對信用卡刷卡紀錄，換算台幣金額 | `main.py` |
| 3. 稅額處理 | 自動判斷含稅/未稅，智慧合併或拆分稅額 | `main.py` |
| 4. 自動登入 | 帳密 + AI 驗證碼辨識（自動重試 5 次） | `form_filler.py` |
| 5. 選單導航 | 操作 4 層巢狀 frameset，開啟核銷表單 | `form_filler.py` |
| 6. 表單填寫 | 填入經費(APPY)、品名(APPP)、受款人(APPA)、用途說明 | `form_filler.py` |
| 7. 自動存檔 | 驗證金額一致 → SUM_ALERT 存入 → 產生 PDF 核銷文件 | `form_filler.py` |

### 主要特色

- **多張收據合併**：一次處理多張發票/收據，合併為一張請購單（最多 14 項品名）
- **外幣自動換算**：自動比對信用卡帳單，將外幣金額換算為台幣
- **AI 服務品名標準化**：Google → "Google Gemini AI服務費"、Claude → "Claude AI服務費" 等
- **稅額智慧處理**：自動判斷 Case A(單品+稅→合併) / Case B(多品+稅) / Case C(無稅)
- **PDF 收據支援**：支援 PDF 格式的發票和信用卡帳單
- **OCR 自動重試**：失敗自動重試（最多 3 次），並有單張辨識備案模式
- **金額自動校正**：存檔時若有 ≤5 元的四捨五入差額，自動調整

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

最簡單的使用方式：把發票/收據檔案丟進 `receipts/` 資料夾，然後執行主程式。

**步驟：**

1. 將發票/收據檔案放入 `receipts/` 資料夾
   支援格式：`.jpg`、`.jpeg`、`.png`、`.webp`、`.pdf`

2. 若有外幣收據，同時放入信用卡刷卡明細的圖片或 PDF

3. 執行主程式：
   ```bash
   python main.py
   ```

4. 程式會自動：
   - **OCR 辨識**所有檔案（支援多張收據合併、PDF 多頁辨識）
   - **比對外幣**收據與信用卡刷卡紀錄
   - **顯示摘要**供使用者確認
   - **登入系統**並自動填寫表單
   - **自動存檔**並產生 PDF 核銷文件

### 單獨 OCR 辨識

只想辨識發票圖片，不填單：

```bash
python main.py --ocr-only
```

或直接辨識單一檔案：

```bash
python ocr.py receipts/invoice_001.jpg
python ocr.py receipts/google_invoice.pdf
```

### 進階選項

```bash
# 計畫請購模式（預設會詢問）
python main.py --project

# 部門請購模式
python main.py --no-project

# 自動存入（不需手動確認）
python main.py --auto-save

# headless 模式（無瀏覽器視窗）
python main.py --headless

# 完成後自動關閉瀏覽器
python main.py --close

# 測試模式（用假資料測試填單流程）
python main.py --test
```

---

## 外幣收據處理

### 使用方式

1. 將外幣收據（如 Google Cloud、Anthropic、OpenAI 的帳單）放入 `receipts/`
2. 將信用卡刷卡明細（截圖或 PDF）也放入 `receipts/`
3. 程式會自動比對並換算台幣金額

### 比對規則

| 比對項目 | 分數 | 說明 |
|----------|------|------|
| 原幣金額完全吻合 | +5 | 如收據 USD $5.00 = 刷卡紀錄 $5.00 |
| 廠商名稱匹配 | +3 | 部分關鍵字匹配即可 |
| 日期 ±1 天 | +3 | 考慮時區差異 |
| 日期 ±3 天 | +2 | |
| 日期 ±7 天 | +1 | |
| **門檻** | **≥5** | 達到門檻才視為匹配成功 |

### AI 服務品名標準化

| 廠商關鍵字 | 標準品名 |
|------------|----------|
| google, gemini | Google Gemini AI服務費 |
| anthropic, claude | Claude AI服務費 |
| openai, chatgpt | ChatGPT AI服務費 |
| microsoft, azure | Microsoft Azure AI服務費 |
| aws, amazon | AWS AI服務費 |

### 注意事項

- 外幣收據的發票號碼會自動清空，改用收據流水號
- 信用卡上的「國外服務費」會包含在匹配金額中（合為一筆）
- 若未找到匹配的刷卡紀錄，程式會暫停警告

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

---

## 專案架構

```
expense-auto/
├── credentials.env        # 帳密和 API Key（不進版控）
├── config.py              # 所有設定：URL、欄位名稱、科目對照
├── ocr.py                 # Gemini Vision OCR（圖片 + PDF）
├── form_filler.py         # Playwright 自動化：登入、導航、填單、存檔
├── main.py                # 主程式：OCR + 外幣比對 + 稅額處理 + 填單
├── requirements.txt       # Python 套件清單
├── .gitignore
│
├── receipts/              # 放入待處理的發票/收據/信用卡帳單
│   └── .gitkeep
│
├── output/                # 程式輸出
│   ├── *_ocr.json         # 每張收據的 OCR 辨識結果
│   ├── *_filled.png       # 填單完成截圖
│   ├── expense_report_*.pdf  # 自動產生的核銷 PDF 文件
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
| `ocr.py` | 呼叫 Gemini Vision API 辨識發票圖片/PDF，回傳結構化 JSON |
| `form_filler.py` | 核心自動化：驗證碼辨識、登入、選單導航、三區塊填寫(APPY/APPP/APPA)、用途說明、金額驗證、自動存檔、PDF 產生 |
| `main.py` | 組合上述模組：OCR → 外幣比對 → 品名標準化 → 稅額處理 → 收據合併 → 填單 |

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

### Q: OCR 辨識某些檔案經常失敗？

程式會自動重試最多 3 次，並嘗試備用的單張辨識模式。若仍失敗：
- 檢查檔案是否損毀（嘗試手動開啟確認）
- PDF 檔案格式複雜時成功率較低，可嘗試截圖轉為 PNG
- 確認 Gemini API 額度未用盡

### Q: 外幣收據金額不正確？

確保將信用卡刷卡明細（圖片或 PDF）也放入 `receipts/` 目錄。
程式需要刷卡紀錄來換算正確的台幣金額。

### Q: 存檔時出現「金額不相符」？

程式會自動處理 ≤5 元的四捨五入差額。若差額過大：
- 檢查 OCR 辨識的品項金額是否正確
- 查看 `output/` 目錄中的 OCR JSON 結果
- 必要時手動修改 JSON 後重新執行

### Q: 可以修改預設的會計科目嗎？

可以。修改 `config.py` 中的 `DEFAULT_SUBJECT`：
```python
DEFAULT_SUBJECT = "110704-8013"  # 改為服務費用
```

### Q: output/ 中的檔案可以刪除嗎？

可以。`output/` 中的檔案都是程式產生的暫存/輸出：
- `*_ocr.json`：OCR 辨識結果備份
- `*_filled.png`：填單截圖供確認
- `expense_report_*.pdf`：核銷文件 PDF
- `captcha_tmp.png`：驗證碼暫存

---

## 已知限制與注意事項

- 核銷系統為 **Big5 編碼的舊式 ASP 架構**，品名中的特殊字元（如 Ω、°、μ）會自動替換為安全字元
- 日期使用**民國年**（如 115 年 = 2026 年）
- 單張請購單最多 **14 個品項**，超過會自動截斷（超出金額歸入差額列）
- `credentials.env` 含敏感資訊，請勿分享或上傳至版控
- 外幣收據**必須搭配信用卡刷卡紀錄**才能正確換算台幣金額
