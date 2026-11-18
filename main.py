"""GitHub の Google のリポジトリ情報を取得して DB に保存する

https://github.com/orgs/google/repositories の全ページをスクレイピングし、
リポジトリ名・主要な言語・スターの数を SQLite に保存して SELECT 文で表示する。
"""
import json
import sqlite3
import time

import requests
from bs4 import BeautifulSoup

# Google のリポジトリ一覧ページ
URL = "https://github.com/orgs/google/repositories"

# 保存する DB ファイル名
DB_NAME = "google_repos.db"


def create_table(conn):
    """テーブルを作成する"""
    cur = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS repos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        language TEXT,
        stars INTEGER
    );
    """
    cur.execute(sql)
    conn.commit()


def get_repos(page):
    """指定したページのリポジトリ情報を取得する"""
    response = requests.get(URL, params={"page": page}, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # 今の GitHub は一覧のデータを <script> タグの中に JSON で持っている
    script = soup.find("script", attrs={"data-target": "react-app.embeddedData"})
    if script is None:
        return []

    data = json.loads(script.string)
    repo_list = data["payload"]["orgReposPageRoute"]["repositories"]

    repos = []
    for repo in repo_list:
        name = repo["name"]

        # 言語が設定されていないリポジトリもある
        if repo["primaryLanguage"]:
            language = repo["primaryLanguage"]["name"]
        else:
            language = "不明"

        stars = repo["starsCount"]
        repos.append((name, language, stars))

    return repos


def save_repos(conn, repos):
    """取得したデータを DB に保存する"""
    cur = conn.cursor()
    sql = "INSERT INTO repos (name, language, stars) VALUES (?, ?, ?);"
    cur.executemany(sql, repos)
    conn.commit()


def show_repos(conn):
    """保存したデータを SELECT 文で表示する"""
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM repos;")
    print("保存件数:", cur.fetchone()[0], "件")

    print("\n--- DB に保存されたデータ ---")
    cur.execute("SELECT name, language, stars FROM repos;")
    for row in cur.fetchall():
        print(row)


def main():
    conn = sqlite3.connect(DB_NAME)
    create_table(conn)

    # 何度実行しても重複しないように、前回のデータを消しておく
    conn.execute("DELETE FROM repos;")
    conn.commit()

    print("スクレイピングを開始します...\n")
    page = 1
    while True:
        try:
            repos = get_repos(page)
        except requests.exceptions.RequestException as e:
            print("HTTP エラーが発生しました:", e)
            break

        # データがなくなったら最後のページ
        if len(repos) == 0:
            break

        save_repos(conn, repos)
        print(page, "ページ目:", len(repos), "件保存しました")

        page += 1
        time.sleep(1)  # サーバーに負荷をかけないように 1 秒待つ

    show_repos(conn)
    conn.close()
    print("\n処理が終了しました。")


if __name__ == "__main__":
    main()
