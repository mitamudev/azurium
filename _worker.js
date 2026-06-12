export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/load" || url.pathname === "/load/") {
      const accept = request.headers.get("accept") || "";
      const userAgent = request.headers.get("user-agent") || "";
      const lowerAgent = userAgent.toLowerCase();
      const isLoaderClient =
        !accept.toLowerCase().includes("text/html") &&
        (lowerAgent.includes("roblox") || lowerAgent.includes("wininet"));

      if (!isLoaderClient) {
        const deniedUrl = new URL("/denied.html", request.url);
        const denied = await env.ASSETS.fetch(deniedUrl);

        return new Response(denied.body, {
          status: 403,
          headers: {
            "content-type": "text/html; charset=utf-8",
            "cache-control": "no-store",
            "x-robots-tag": "noindex, nofollow, noarchive",
          },
        });
      }
    }

    return env.ASSETS.fetch(request);
  },
};
