# leapnet-helpCenter-chatbot
leapnetのHelpCenter用のChatbot（Leapnet RAG）

Codexを利用するために、Publicで作成する

## How to Run

1. **Install dependencies:**

   ```bash
   brew install uv
   uv pip install -r src/requirements.txt
   ```

2. **Start the server:**

   ```bash
   uv run uvicorn src.main:app --reload
   ```

3. **Open the chatbot:**

   Open the `index.html` file in your browser.
