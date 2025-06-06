# ロジックモデル作成支援ツール

このツールは、自治体の施策や事業に関するロジックモデルを自動生成するWebアプリケーションです。政策名、最終アウトカム、自治体名を入力することで、関連情報を収集し、ロジックモデルを作成します。

## 必要条件

- Python 3.8以上
- OpenAI APIキー

## インストール方法

1. リポジトリのクローン
```bash
git clone [リポジトリURL]
cd logicmodel_localgov
```

2. 必要なパッケージのインストール

```bash
make install
```

3. 環境変数の設定
.streamlit/secrets.toml ファイルを作成し、以下を記述してください：
```
OPENAI_API_KEY = "your_openai_api_key"
```

## 使用方法

1. アプリケーションの起動
```bash
make run
```

2. ブラウザで表示されるフォームに以下の情報を入力：
   - 政策名（例：子育て支援事業）
   - 最終アウトカム（例：子育て世帯の生活満足度向上）
   - 自治体名（例：東京都渋谷区）

3. 「ロジックモデルを作成する」ボタンをクリック

4. 生成されたロジックモデルと図を確認

## 注意事項

- OpenAI APIの利用には料金が発生します
- 生成されるロジックモデルは、入力された情報とWeb検索結果に基づいて作成されます
- より正確な結果を得るためには、具体的な政策名とアウトカムを入力してください
