$(function () {
  const $launcher = $(".chatbot-launcher");
  const $container = $(".chatbot-container");
  const $messages = $("#chatbotMessages");
  const $form = $("#chatbotForm");
  const $input = $("#chatbotInput");
  let isOpen = false;
  const conversationHistory = [];

  const API_ENDPOINT = 'https://blue-dream-a358.bing-bai-60c.workers.dev/chat';
  //const API_ENDPOINT = 'http://127.0.0.1:8000/chat'; // localテスト
  //const API_KEY = "7378f458-1142-4b";

  const RATING_ENDPOINT = API_ENDPOINT.replace(/\/chat$/, "/chat_rating");
  const ratingLabels = [5, 4, 3, 2, 1];
  const ratingLabelMap = {
    5: "とても良い",
    4: "良い",
    3: "普通",
    2: "悪い",
    1: "とても悪い",
  };
  　
  function generateRequestId() {
    if (window.crypto?.randomUUID) {
      return window.crypto.randomUUID();
    }
    return `req_${Date.now()}_${Math.random().toString(16).slice(2)}`;
  }

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

  function appendMessage(role, content,  options = {}) {
    const isUser = role === "user";
    const $message = $(`<div class="chatbot-message ${isUser ? "user" : "bot"}">
      ${isUser ? "" : '<div class="chatbot-avatar" aria-hidden="true">LN</div>'}
      <div class="chatbot-bubble"></div>
    </div>`);
    $message.find(".chatbot-bubble").text(content);
    $messages.append($message);
    $messages.scrollTop($messages.prop("scrollHeight"));
    if (options.trackHistory) {
      conversationHistory.push({
        role: options.historyRole || (isUser ? "user" : "assistant"),
        content,
      });
    }
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

  function appendRatingButtons(requestId) {
    const $ratingContainer = $('<div class="chatbot-rating"></div>');
    const $description = $('<p class="chatbot-rating-description" aria-live="polite"></p>');

    ratingLabels.forEach((rating) => {
      const $button = $(`
        <button type="button" class="chatbot-rating-button" data-rating="${rating}">
          ${rating}
        </button>
      `);
      $button.on("mouseenter focus", function () {
        $description.text(`評価 ${rating}: ${ratingLabelMap[rating]}`).addClass("is-visible");
      });

      $button.on("mouseleave blur", function () {
        $description.text("").removeClass("is-visible");
      });

      $button.on("click", function () {
        $ratingContainer.find(".chatbot-rating-button").prop("disabled", true);
        $button.addClass("is-selected");

        $.ajax({
          url: RATING_ENDPOINT,
          method: "POST",
          contentType: "application/json",
          data: JSON.stringify({
            requestId,
            rating,
          }),
        }).fail(function (xhr, status) {
          console.error("Chat rating API error", status, xhr);
        });
      });
      $ratingContainer.append($button);
    });

    $ratingContainer.append($description);
    $messages.append($ratingContainer);
    $messages.scrollTop($messages.prop("scrollHeight"));
  }

  function sendMessageToBot(message, history) {
    const requestId = generateRequestId();
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
        history,
        requestId,
      }),
    })
      .done(function (response) {
        const botMessage = response?.answer || "回答を取得できませんでした。";
        appendMessage("bot", botMessage, { trackHistory: true, historyRole: "assistant" });

        if (response?.source_summary) {
          appendMessage(
            "bot",
            `参考情報:\n${response.source_summary}`
          );
        }

        appendRatingButtons(requestId);
      })
      .fail(function (xhr, status) {
        console.error("Chatbot API error", status, xhr);
        appendMessage("bot", "申し訳ありません。現在サーバーに接続できませんでした。",  { trackHistory: false });
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

    const historyForRequest = [...conversationHistory];
    appendMessage("user", message, { trackHistory: true, historyRole: "user" });
    $input.val("");
    sendMessageToBot(message, historyForRequest);
  });

  // 初回起動時にウェルカムメッセージを表示
  appendMessage("bot", "こんにちは！Leapnetサポートへようこそ。ご質問があればお聞かせください。", { trackHistory: false });
});
