import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from rich.console import Console
from rich.table import Table

# .env ファイルを読み込む
load_dotenv()

# 環境変数から API キーを取得
API_KEY = os.getenv("API_KEY")

# Wiki.js の API エンドポイント
WIKI_API_URL = os.getenv("WIKI_API_URL")

# API ヘッダー
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# コンソール設定
console = Console()

def format_datetime(iso_str):
    """ISO 8601 形式の日付を 'YYYY-MM-DD HH:MM:SS' に変換"""
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return iso_str  # 変換失敗時はそのまま

def fetch_data(query):
    """GraphQL API へリクエストを送信"""
    try:
        response = requests.post(WIKI_API_URL, json={"query": query}, headers=HEADERS)
        response.raise_for_status()
        return response.json().get("data", {})
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]エラー:[/bold red] {e}")
        return None

def get_users():
    """ユーザー一覧を取得し、ID順にソート"""
    user_query = """
    query {
      users {
        list {
          id
          name
          email
          isActive
          createdAt
        }
      }
    }
    """
    data = fetch_data(user_query)
    if data:
        users = data.get("users", {}).get("list", [])
        return sorted(users, key=lambda x: x["id"])
    return []

def get_groups():
    """グループ一覧を取得し、ID順にソート"""
    group_query = """
    query {
      groups {
        list {
          id
          name
          createdAt
        }
      }
    }
    """
    data = fetch_data(group_query)
    if data:
        return sorted(data.get("groups", {}).get("list", []), key=lambda x: x["id"])
    return []

def display_users(users):
    """ユーザー情報を美しく表示"""
    table = Table(title="ユーザー一覧", show_header=True, header_style="bold cyan")
    table.add_column("ID", justify="right")
    table.add_column("ユーザー名", style="bold")
    table.add_column("メール", style="magenta")
    table.add_column("作成日時", style="green")
    table.add_column("状態", style="bold yellow")

    for user in users:
        status = "🟢 Active" if user["isActive"] else "🔴 Inactive"
        table.add_row(str(user["id"]), user["name"], user["email"], format_datetime(user["createdAt"]), status)

    console.print("\n")
    console.print(table)
    console.print("\n")

def display_groups(groups):
    """グループ情報を美しく表示"""
    table = Table(title="グループ一覧", show_header=True, header_style="bold blue")
    table.add_column("ID", justify="right")
    table.add_column("グループ名", style="bold yellow")
    table.add_column("作成日時", style="green")

    for group in groups:
        table.add_row(str(group["id"]), group["name"], format_datetime(group["createdAt"]))

    console.print("\n")
    console.print(table)
    console.print("\n")

def main():
    """メイン処理"""
    users = get_users()
    groups = get_groups()

    if users:
        display_users(users)
    else:
        console.print("[bold red]ユーザーが見つかりません。[/bold red]")

    if groups:
        display_groups(groups)
    else:
        console.print("[bold red]グループが見つかりません。[/bold red]")

if __name__ == "__main__":
    main()