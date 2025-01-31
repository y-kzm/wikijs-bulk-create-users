import os
import csv
import requests
import csv
import ast
from dotenv import load_dotenv
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

# コンソール出力設定
console = Console()

def create_user(name, email, password, groups, must_change_password=True, send_welcome_email=False):
    """Wiki.js に新しいユーザーを作成"""
    mutation = """
    mutation ($email: String!, $name: String!, $passwordRaw: String!, $groups: [Int!]!, $mustChangePassword: Boolean!, $sendWelcomeEmail: Boolean!) {
      users {
        create (
          email: $email
          name: $name
          passwordRaw: $passwordRaw
          providerKey: "local"
          groups: $groups
          mustChangePassword: $mustChangePassword
          sendWelcomeEmail: $sendWelcomeEmail
        ) {
          responseResult {
            succeeded
            message
          }
          user {
            id
          }
        }
      }
    }
    """
    variables = {
        "email": email,
        "name": name,
        "passwordRaw": password,
        "groups": groups,
        "mustChangePassword": must_change_password,
        "sendWelcomeEmail": send_welcome_email
    }

    try:
        response = requests.post(WIKI_API_URL, json={"query": mutation, "variables": variables}, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        # API からエラーが返ってきた場合
        if "errors" in data:
            console.print(f"[bold red]API エラー:[/bold red] {data['errors'][0]['message']}")
            console.print("[bold yellow]送信したリクエスト:[/bold yellow]", variables)
            return None

        # ユーザー作成に失敗した場合
        if not data["data"]["users"]["create"]["responseResult"]["succeeded"]:
            console.print(f"[bold red]作成失敗: {data['data']['users']['create']['responseResult']['message']}[/bold red]")
            console.print("[bold yellow]送信したリクエスト:[/bold yellow]", variables)
            return None

        return data["data"]["users"]["create"]

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]リクエストエラー:[/bold red] {e}")
        return None

def create_users_from_csv(file_path):
    """CSV ファイルを読み込んで複数のユーザーを作成"""
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        user_list = []

        for row in reader:
            name = row["name"].strip()
            email = row["email"].strip()
            password = row["password"].strip()

            # グループ ID をリストに変換
            try:
                groups = ast.literal_eval(row["groups"]) if row["groups"] else [1]
            except (ValueError, SyntaxError):
                groups = [1]  # デフォルト値

            must_change_password = row["must_change_password"].strip().lower() == "yes"
            send_welcome_email = row["send_welcome_email"].strip().lower() == "yes"

            print(f"\nユーザー作成中: {name} ({email}) - グループ: {groups}")

            user = create_user(name, email, password, groups, must_change_password, send_welcome_email)

            if user and user["responseResult"]["succeeded"]:
                user_list.append({
                    "id": "Unknown",
                    "name": name,
                    "email": email,
                    "groups": ", ".join(map(str, groups)),
                    "status": "🟢 成功"
                })
            else:
                user_list.append({
                    "id": "-",
                    "name": name,
                    "email": email,
                    "groups": ", ".join(map(str, groups)),
                    "status": "🔴 失敗"
                })

        # ユーザー作成結果を表示
        display_results(user_list)

def display_results(user_list):
    """ユーザー作成結果を表形式で表示"""
    table = Table(title="ユーザー作成結果")
    table.add_column("ID", justify="right")
    table.add_column("ユーザー名", style="bold")
    table.add_column("メール", style="magenta")
    table.add_column("グループ", style="cyan")
    table.add_column("状態", style="bold yellow")

    for user in user_list:
        table.add_row(user["id"], user["name"], user["email"], user["groups"], user["status"])

    console.print("\n")
    console.print(table)
    console.print("\n")

def main():
    """メイン処理"""
    console.print("[bold cyan]Wiki.js ユーザー一括作成スクリプト[/bold cyan]")

    file_path = input("CSV ファイルのパスを入力: ").strip()

    if not os.path.exists(file_path):
        console.print(f"[bold red]エラー: 指定されたファイルが見つかりません → {file_path}[/bold red]")
        return

    create_users_from_csv(file_path)

if __name__ == "__main__":
    main()