# leapnet-helpCenter-chatbot

Leapnet の HelpCenter 向け Chatbot（Leapnet RAG）プロジェクトです。  
Zendesk に埋め込まれたチャットボットから、Leapnet のエージェントまでを連携します。

---

## 概要

本プロジェクトは、Zendesk の HelpCenter 上で動作するチャットボットを通じて  
Leapnet の RAG エージェントと連携する仕組みを提供します。

---

## 全体構成

### リクエストフロー

Zendesk HTML（chatbot.js / Ajax）

↓

Cloudflare Workers（work.js）

↓

Chatbot API（leapnet-chatbot-api.inside.ai）

↓

Leapnet エージェント（agent.leapnet.com）


## コンポーネント説明

### chatbot.js

- 本プロジェクトの対象
- Zendesk の HTML 画面に埋め込まれる JavaScript
- jQuery を使用した Ajax 通信を担当
- ユーザーの入力を Cloudflare Workers に送信

---

### work.js（Cloudflare Workers）

- 本プロジェクトの対象
- Zendesk からの通信は **HTTPS が必須**
- Cloudflare Workers（無料枠）を利用して中継レイヤーを構築
- chatbot.js からのリクエストを Leapnet Chatbot API に転送

---

### leapnet-chatbot-api

- 本プロジェクトの対象
- GCP 上に構築した FastAPI アプリケーション
- 固定 IP を使用
- Cloudflare の仕様上、固定 IP への直接リダイレクトができないため  
  ドメイン（`leapnet-chatbot-api.inside.ai`）を利用

---

### Leapnet エージェント

- 本プロジェクトの対象外
- Leapnet 上で構築された Chatbot 用エージェント
- エージェントの作成・更新は本リポジトリでは管理しない

---

## How to Run（macOS/本番）

### 1. 依存関係のインストール

```

brew install uv

uv pip install -r app/requirements.txt

```


### 2. 起動

```
uv run uvicorn app.main:app --reload

```


### 2. 起動(本番)

```
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &

```
### 3. 停止(本番)

```
sudo ps aux | grep uv
sudo kill -9 [対象プロセス番号]

```


## How to Run（Windows: Powershell管理者）

### 0. 実行環境

- pyenv-win + Poetry

- python3.11.x


### 1. 依存関係のインストール

```


poetry run pip　install -r app/requirements.txt


```


### 2. 起動

```

poetry run uvicorn app.main:app --reload


```
