
import requests
import time
import sqlite3
from bs4 import BeautifulSoup

# GoogleのGitHubリポジトリ一覧
url = "https://github.com/orgs/google/repositories"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# スクレイピング
time.sleep(1)

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

repositories = soup.find_all(
    "li",
    class_="listItem__X41oTe"
)

# スター数を数値に変換する関数
def convert_stars(value):
    value = value.strip().lower()

    if value.endswith("k"):
        return int(float(value[:-1]) * 1000)
    elif value.endswith("m"):
        return int(float(value[:-1]) * 1000000)
    else:
        return int(value.replace(",", ""))


# 取得したデータを保存するリスト
repo_data = []

for repo in repositories[:10]:

    # リポジトリ名
    heading = repo.find("h3")
    if not heading or not heading.find("a"):
        continue

    name = heading.find("a").get_text(strip=True)

    # 主要な言語
    language_tag = repo.find(
        "span",
        class_="PrimaryLanguageName__94OAQO"
    )

    if language_tag:
        language = language_tag.get_text(strip=True)
    else:
        language = "不明"

    # スター数
    star_tag = repo.find(
        "a",
        href=lambda x: x and x.endswith("/stargazers")
    )

    if star_tag:
        stars = convert_stars(star_tag.get_text(strip=True))
    else:
        stars = 0

    repo_data.append((name, language, stars))

# データベースに接続
con = sqlite3.connect("repositories.db")
cur = con.cursor()

# テーブルを作成
cur.execute("""
CREATE TABLE IF NOT EXISTS repositories (
    name TEXT PRIMARY KEY,
    language TEXT,
    stars INTEGER
)
""")

# データを保存
cur.executemany("""
INSERT OR REPLACE INTO repositories
(name, language, stars)
VALUES (?, ?, ?)
""", repo_data)

con.commit()

print("データベースへの保存が完了しました！")

# SELECT文でデータを表示
cur.execute("""
SELECT name, language, stars
FROM repositories
ORDER BY stars DESC
""")

print("\n【保存されたリポジトリ一覧】")

for row in cur.fetchall():
    print("リポジトリ名:", row[0])
    print("主要な言語:", row[1])
    print("スター数:", row[2])
    print("--------------------")

# データベースを閉じる
con.close()
