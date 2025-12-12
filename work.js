// ← ここに FastAPI が動いているホスト名を入れてください
// 例）http://api-backend.inside.ai:8000
//const API_ORIGIN = "http://34.153.204.67:8000";
const API_ORIGIN = "http://leapnet-chatbot-api.inside.ai:8000";

// 許可する Origin 一覧（追加したいときはここに追加）
const ALLOWED_ORIGINS = [
  "https://help-leapnet.inside.ai",
  "https://help-leapnet.zendesk.com"
];

function getAllowedOrigin(origin) {
  return ALLOWED_ORIGINS.includes(origin) ? origin : "";
}


export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const allowOrigin = getAllowedOrigin(origin);

    // --- Preflight (OPTIONS) ---
    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "Access-Control-Allow-Origin": allowOrigin,
          "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, Authorization",
          "Access-Control-Max-Age": "86400",
        },
      });
    }

    // --- プロキシ対象パス ---
    const proxyTargets = ["/chat", "/test/chat"];

    if (proxyTargets.includes(url.pathname)) {
      const targetUrl = API_ORIGIN + url.pathname;

      const headers = new Headers();
      const contentType = request.headers.get("Content-Type");
      if (contentType) headers.set("Content-Type", contentType);

      const init = {
        method: request.method,
        headers,
        body: request.body,
      };

      let apiResponse;
      try {
        apiResponse = await fetch(targetUrl, init);
      } catch (e) {
        return new Response(
          JSON.stringify({
            error: "Upstream fetch failed",
            detail: String(e),
            target: targetUrl,
          }),
          {
            status: 502,
            headers: {
              "Content-Type": "application/json",
              "Access-Control-Allow-Origin": allowOrigin,
            },
          }
        );
      }

      const respBody = await apiResponse.text();
      const respHeaders = new Headers(apiResponse.headers);
      respHeaders.set("Access-Control-Allow-Origin", allowOrigin);
      respHeaders.set("Access-Control-Allow-Credentials", "true");

      return new Response(respBody, {
        status: apiResponse.status,
        headers: respHeaders,
      });
    }

    // --- 対象外は404 ---
    return new Response("Not Found", { status: 404 });
  },
};
