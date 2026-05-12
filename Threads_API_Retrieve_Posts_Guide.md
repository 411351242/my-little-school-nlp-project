# Threads API：自動化擷取貼文實戰指引 (AI 與開發者協作版)

> **💡 文件用途說明**
> 這是一份專為「人類開發者」與「AI 程式助手」共同協作設計的指南。
> 只要將這份文件完整提供給 AI（如 ChatGPT, Claude, Gemini），AI 就能理解 API 規格並為您產出可以直接執行的爬蟲/串接腳本。
> 
> **流程分為兩大階段**：
> 1. **【👤 使用者手動操作】**：AI 無法幫您點擊網頁與申請帳號，您必須手動完成這些步驟並取得密鑰。
> 2. **【🤖 給 AI 的開發指令】**：AI 讀取此區塊與規格後，將為您產出完整的自動化程式碼。

---

## 🛑 第一階段：👤 使用者手動操作區 (Human Tasks)

因為安全性與 Meta 的平台限制，以下步驟**必須由您親自手動完成**。請在完成後，將取得的資料填入 `.env` 檔案中。

### 步驟 1：註冊 Meta 開發者與建立應用程式
1. 前往 [Meta for Developers](https://developers.facebook.com/) 並登入。
2. 點擊「我的應用程式 (My Apps)」 > 「建立應用程式 (Create App)」。
3. 根據您的需求選擇使用案例（通常選擇「其他」或與 Threads 相關的選項），並完成 App 建立。
4. 在應用程式儀表板中，找到「新增產品 (Add Product)」，並設定 **Threads API**。

### 步驟 2：手動取得存取權杖 (Access Token)
開發與測試最快的方法是使用 Graph API Explorer，而不是從零寫一個複雜的網頁登入系統。
1. 前往 [Graph API 測試工具 (Graph API Explorer)](https://developers.facebook.com/tools/explorer/)。
2. 在右側的「Meta 應用程式」下拉選單中，選擇您剛才建立的 App。
3. 在「權限 (Permissions)」欄位，新增以下權限：
   * `threads_basic` (必備：讀取自己貼文)
   * `threads_profile_discovery` (可選：如果需要抓取其他公開帳號的貼文才需要)
4. 點擊「Generate Access Token」，此時會跳出授權視窗，請用您的 Threads 帳號登入並同意。
5. 複製產生的那一長串字元，這就是您的 `ACCESS_TOKEN`。

### 步驟 3：建立本地環境變數檔 (`.env`)
在您的專案根目錄下建立一個名為 `.env` 的檔案，並填入您剛才取得的資訊。**請勿將此檔案上傳至 GitHub 等公開存放區。**

```env
# .env 檔案範例
THREADS_ACCESS_TOKEN=請將剛剛複製的_ACCESS_TOKEN_貼在這裡
TARGET_USERNAME=zuck  # (可選) 如果您想抓取特定公開帳號，填寫其帳號名稱
```

✅ **完成上述步驟後，您就可以將這份文件與 `.env` 丟給 AI，讓它開始寫 Code 了！**

---

## 🚀 第二階段：🤖 給 AI 的開發指令 (AI Prompt / Instructions)

> **⚠️ 致 AI 助手：**
> 請閱讀以下開發規範與下方的「API 規格參考」，並根據使用者的語言偏好（例如 Python 或 Node.js）撰寫一段完整且可執行的腳本。

### 🧑‍💻 AI 開發目標
請撰寫一個指令碼（Script），達成以下目標：
1. **讀取環境變數**：載入 `.env` 檔案中的 `THREADS_ACCESS_TOKEN`（與可選的 `TARGET_USERNAME`）。
2. **呼叫 API**：使用下方的 API 規格擷取貼文資料。
3. **分頁處理 (Pagination) 自動化**：實作一個 `while` 迴圈或遞迴，自動偵測 API 回傳的 `paging.next` 或 `paging.cursors.after`，直到抓取完所有貼文（或達到使用者設定的擷取數量上限）為止。
4. **錯誤處理 (Error Handling)**：加入 HTTP 錯誤捕獲機制（例如 Token 過期、API Rate Limit），並在發生錯誤時印出具體原因。
5. **資料儲存**：將抓取到的完整貼文資料（包含 id, text, timestamp, media_url, permalink 等）整理並儲存成一個易讀的 JSON 檔案（例如 `threads_posts_export.json`）或 CSV 檔案。

### 📝 AI 實作細節建議 (以 Python 為例)
* 請使用 `python-dotenv` 讀取環境變數。
* 請使用 `requests` 模組處理 HTTP GET 請求。
* 程式碼需具備良好的註解與模組化（例如將「抓取單頁資料」寫成一個函數）。

---

## 📚 附錄：API 規格參考 (API Reference)

AI 請嚴格遵循以下 Meta Threads API 的端點與參數設計：

### 1. API 基礎架構
* **Base URL**: `https://graph.threads.net/v1.0`
* **認證方式**: 在 Query Parameter 帶入 `?access_token={YOUR_TOKEN}`。

### 2. 主要端點 (Endpoints)

#### 選項 A：擷取授權用戶自己的貼文 (App-Scoped)
* **Endpoint**: `GET /me/threads`
* **適用情境**: 只要抓取 `.env` 中提供授權 Token 的那個帳號的貼文。

#### 選項 B：擷取其他公開帳號的貼文 (Profile Discovery)
* **Endpoint**: `GET /profile_posts`
* **必須參數**: `username={目標帳號名稱}` (例如 `username=zuck`)
* **適用情境**: 欲建立爬蟲搜集特定公開 KOL 的 Threads 發文。*(前提是 Token 具備 `threads_profile_discovery` 權限)*

### 3. 可用欄位 (Fields)
請求時，應透過 `fields` 參數指定要拿回來的資料（以逗號分隔）。建議組合：
`fields=id,text,media_type,media_url,permalink,timestamp,username,is_quote_post`

### 4. API 回傳結構與分頁 (Pagination)
成功請求後，回傳的 JSON 結構如下：
```json
{
  "data": [
    {
      "id": "1234567890",
      "text": "這是一篇 Threads 貼文",
      "timestamp": "2023-11-01T12:00:00+0000",
      // ... 其他要求的 fields
    }
  ],
  "paging": {
    "cursors": {
      "before": "...",
      "after": "..."
    },
    "next": "https://graph.threads.net/v1.0/me/threads?access_token=...&after=..."
  }
}
```
**分頁邏輯**：如果回傳的 JSON 中存在 `paging.next`，代表還有下一頁資料，請對該 URL 繼續發起 GET 請求，直到 `paging.next` 不存在為止。