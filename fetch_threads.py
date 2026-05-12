import os
import json
import requests
import sys
import argparse
from dotenv import load_dotenv

# 修正 Windows 命令列預設編碼 (cp950) 無法印出 Emoji 的問題
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 1. 讀取環境變數
load_dotenv()

ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")
TEST_USERNAME = os.getenv("TEST_USERNAME")

BASE_URL = "https://graph.threads.net/v1.0"

def fetch_threads_posts(access_token, username=None):
    """
    抓取 Threads 貼文
    如果有傳入 username，則抓取該目標帳號的貼文 (Profile Discovery)；
    否則抓取授權用戶自己的貼文 (App-Scoped)。
    """
    if not access_token:
        print("❌ 錯誤：找不到 THREADS_ACCESS_TOKEN，請檢查 .env 檔案。")
        return None

    # 決定使用的 Endpoint
    if username:
        print(f"🔍 準備擷取目標帳號 [{username}] 的公開貼文...")
        url = f"{BASE_URL}/profile_posts"
        params = {
            "username": username,
            "access_token": access_token,
            "fields": "id,text,media_type,media_url,permalink,timestamp,username,is_quote_post"
        }
    else:
        print("🔍 準備擷取授權用戶自己的貼文...")
        url = f"{BASE_URL}/me/threads"
        params = {
            "access_token": access_token,
            "fields": "id,text,media_type,media_url,permalink,timestamp,username,is_quote_post"
        }

    all_posts = []
    
    # 3. 分頁處理 (Pagination)
    while url:
        try:
            print(f"🌐 發送 API 請求：{url.split('?')[0]} (隱藏 token)...")
            response = requests.get(url, params=params, timeout=10)
            
            # 4. 錯誤處理
            response.raise_for_status() # 如果是 4xx 或 5xx 會拋出例外
            
            data = response.json()
            posts = data.get("data", [])
            all_posts.extend(posts)
            print(f"✅ 成功獲取本頁資料，共 {len(posts)} 筆貼文 (目前累計 {len(all_posts)} 筆)")

            # 檢查是否有下一頁
            paging = data.get("paging", {})
            next_url = paging.get("next")
            
            if next_url:
                url = next_url
                # next_url 已經包含了所有需要的 query parameters (包含 access_token 和 after cursor)
                # 因此後續請求不需要再附加 params
                params = None 
            else:
                print("🏁 已抓取完畢，沒有下一頁了。")
                break
                
        except requests.exceptions.HTTPError as errh:
            print(f"❌ HTTP 錯誤: {errh}")
            if response.status_code == 400:
                 print("👉 可能原因：Token 過期、權限不足，或是帳號不存在。")
            elif response.status_code == 429:
                 print("👉 可能原因：API Rate Limit (達到呼叫次數上限)。")
            
            # 印出詳細 API 錯誤訊息 (如果有的話)
            try:
                error_details = response.json()
                print(f"📄 API 錯誤詳情:\n{json.dumps(error_details, indent=2, ensure_ascii=False)}")
            except:
                pass
            break
        except requests.exceptions.ConnectionError as errc:
            print(f"❌ 連線錯誤: {errc}")
            break
        except requests.exceptions.Timeout as errt:
            print(f"❌ 請求超時: {errt}")
            break
        except requests.exceptions.RequestException as err:
            print(f"❌ 未知錯誤: {err}")
            break

    return all_posts

def save_to_json(data, filename="my_posts.json"):
    """
    5. 資料儲存
    將抓取到的資料儲存為 JSON 檔案
    """
    if not data:
        print("⚠️ 沒有資料可以儲存。")
        return

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 資料已成功儲存至 {filename}")
    except Exception as e:
        print(f"❌ 儲存檔案時發生錯誤：{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Threads API 爬蟲腳本")
    parser.add_argument("-u", "--username", type=str, help="指定要抓取的目標帳號名稱 (Profile Discovery)，若未指定則預設抓取 .env 內的 TEST_USERNAME 或授權帳號本身。")
    parser.add_argument("-o", "--output", type=str, default="my_posts.json", help="輸出的 JSON 檔案名稱 (預設: my_posts.json)")
    
    args = parser.parse_args()

    print("🚀 開始執行 Threads 爬蟲腳本...")
    
    # 決定要使用的 username，優先權：命令列參數 > .env 中的 TEST_USERNAME
    target_username = args.username if args.username else TEST_USERNAME
    
    # 執行抓取
    posts_data = fetch_threads_posts(ACCESS_TOKEN, target_username)
    
    # 如果有抓到資料，則進行儲存
    if posts_data:
        save_to_json(posts_data, filename=args.output)
        
    print("🎉 腳本執行結束。")
