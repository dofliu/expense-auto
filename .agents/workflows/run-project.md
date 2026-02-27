---
description: 執行核銷自動填單系統的各種模式
---

# 執行核銷自動填單系統

## 前置條件

1. 確認已建立虛擬環境並啟動
2. 確認 `credentials.env` 已正確設定
3. 確認 Playwright Chromium 已安裝

## 批次處理（完整流程）

// turbo

1. 將發票圖片放入 `receipts/` 資料夾
2. 執行主程式：

```bash
python main.py
```

## 僅 OCR 辨識（不填單）

```bash
python main.py --ocr-only
```

## 顯示瀏覽器視窗（Debug 模式）

```bash
python main.py --no-headless
```

## 不自動存入（僅填單截圖）

```bash
python main.py --no-save
```

## 指定計畫（跳過互動選擇）

```bash
python main.py --plan "高教深耕"
```

## 單張 OCR 辨識

```bash
python ocr.py receipts/invoice_001.jpg
```

## 測試登入功能

```bash
python test_login.py
```

## 測試填單功能（使用假資料）

```bash
python form_filler.py
```
