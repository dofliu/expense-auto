---
description: 設定開發環境與安裝相依套件
---

# 設定開發環境

## 1. 建立 Python 虛擬環境

```bash
cd d:\Dropbox\Project_CodingSimulation\expense-auto
python -m venv venv
```

## 2. 啟動虛擬環境（Windows）

```bash
venv\Scripts\activate
```

## 3. 安裝 Python 套件

// turbo

```bash
pip install -r requirements.txt
```

## 4. 安裝 Playwright 瀏覽器

// turbo

```bash
playwright install chromium
```

## 5. 設定憑證

建立 `credentials.env` 並填入以下內容：

```env
SYSTEM_URL=https://account.ncut.edu.tw/APSWIS_Q/Login_L_Q.asp
NCUT_USERNAME=你的員工編號
NCUT_PASSWORD=你的密碼
GEMINI_API_KEY=你的_Google_Gemini_API_Key
```

## 6. 驗證安裝

// turbo

```bash
python -c "import playwright; import google.generativeai; import dotenv; import PIL; print('All packages installed successfully!')"
```
