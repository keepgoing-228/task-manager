# Email 功能設定說明

## 功能概述

ASRtranslate 系統現在支援在翻譯完成後自動發送 email 通知，包含下載連結。

## 設定步驟


### 1. Email 設定檔 (可選)
可以建立 `email_config.json` 檔案來自訂 email 設定，這邊須設定 ASRtranslate 專案需要的：

```json
{
	"sender": "",
	"password": "",
	"smtp_server": "mail.asrock.com.tw",
	"domain": "",
	"smtp_port": 587,
	"use_ntlm": true,
	"include_timestamp":true
}
```

### 2. 修改 main.py 中的 FastAPI 設定

在 `main.py` 中修改以下設定，這邊須設定 ASRtranslate 專案需要的：

```python
# FastAPI configuration
FASTAPI_SERVER = "0.0.0.0"
FASTAPI_PORT = 3030
```

## 使用方法

### 透過 Web UI

1. 在 "Setting" 頁面輸入 email 地址
2. 選擇檔案和語言
3. 點擊 "Start Translation"
4. 翻譯完成後會自動發送 email 通知


## 注意事項

1. 確保 SMTP 伺服器設定正確
2. 如果使用 Gmail，需要開啟應用程式密碼
3. 確保伺服器 IP 和 port 設定正確
4. 檢查防火牆設定，確保可以發送 SMTP 郵件

