$(function () {
  const $launcher = $(".chatbot-launcher");
  const $container = $(".chatbot-container");
  const $messages = $("#chatbotMessages");
  const $form = $("#chatbotForm");
  const $input = $("#chatbotInput");
  let isOpen = false;

  const API_ENDPOINT = 'https://blue-dream-a358.bing-bai-60c.workers.dev/chat';
  //const API_KEY = "7378f458-1142-4b";

  function toggleChatbot(open) {
    isOpen = typeof open === "boolean" ? open : !isOpen;
    $container.toggleClass("is-open", isOpen);
    $container.attr("aria-hidden", !isOpen);

    if (isOpen) {
      setTimeout(() => {
        $input.trigger("focus");
      }, 200);
    }
  }

  function appendMessage(role, content) {
    const isUser = role === "user";
    const $message = $(`<div class="chatbot-message ${isUser ? "user" : "bot"}">
      ${isUser ? "" : '<div class="chatbot-avatar" aria-hidden="true">LN</div>'}
      <div class="chatbot-bubble"></div>
    </div>`);
    $message.find(".chatbot-bubble").text(content);
    $messages.append($message);
    $messages.scrollTop($messages.prop("scrollHeight"));
  }

  function appendTypingIndicator() {
    const $typing = $(`<div class="chatbot-message bot chatbot-typing-message">
      <div class="chatbot-avatar" aria-hidden="true">LN</div>
      <div class="chatbot-bubble">
        <div class="chatbot-typing" aria-label="Leapnet is typing">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>`);
    $messages.append($typing);
    $messages.scrollTop($messages.prop("scrollHeight"));
    return $typing;
  }

  function sendMessageToBot(message) {
    const $typingIndicator = appendTypingIndicator();

    return $.ajax({
      url: API_ENDPOINT,
      method: "POST",
      contentType: "application/json",
      headers: {
//        "x-api-key": API_KEY,
      },
      data: JSON.stringify({
        query: message,
      }),
    })
      .done(function (response) {
        const botMessage = response?.answer || "回答を取得できませんでした。";
        appendMessage("bot", botMessage);

        if (response?.source_summary) {
          appendMessage(
            "bot",
            `参考情報:\n${response.source_summary}`
          );
        }
      })
      .fail(function (xhr, status) {
        console.error("Chatbot API error", status, xhr);
        appendMessage("bot", "申し訳ありません。現在サーバーに接続できませんでした。");
      })
      .always(function () {
        $typingIndicator.remove();
      });
  }

  $launcher.on("click", function () {
    toggleChatbot();
  });

  $(".chatbot-close").on("click", function () {
    toggleChatbot(false);
  });

  $form.on("submit", function (event) {
    event.preventDefault();
    const message = $input.val().trim();
    if (!message) {
      return;
    }

    appendMessage("user", message);
    $input.val("");
    sendMessageToBot(message);
  });

  // 初回起動時にウェルカムメッセージを表示
  appendMessage("bot", "こんにちは！Leapnetサポートへようこそ。ご質問があればお聞かせください。");
});
