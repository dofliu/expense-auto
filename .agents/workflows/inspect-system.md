---
description: 使用開發工具分析核銷系統的頁面與 Frame 結構
---

# 分析核銷系統結構

當需要了解核銷系統的頁面結構、修改表單欄位、或排查問題時，使用以下工具。

## 分析頁面結構

```bash
python inspect_pages.py
```

輸出整體頁面與 frameset 結構。

## 分析選單結構

```bash
python inspect_menu.py
```

列出系統選單項目與導航路徑。

## 分析 APPY frame（經費表頭）

```bash
python inspect_appy.py
```

列出 APPY frame 中所有表單元素及其屬性。

## 查詢可用預算與科目清單

```bash
python inspect_budget.py
```

查詢目前可用的預算計畫和會計科目，結果存入 `output/subjects.txt`。

## 分析 TRAN frame

```bash
python inspect_tran.py
```

查看 TRAN frame 的資料傳輸結構。

## 測試登入

```bash
python test_login.py
```

僅測試帳密和驗證碼是否能正確登入。
