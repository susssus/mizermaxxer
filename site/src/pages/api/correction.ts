import type { APIRoute } from "astro";
import { checkBotId } from "botid/server";

export const prerender = false;

const GITHUB_ISSUES_URL =
  "https://github.com/susssus/mizermaxxer/issues/new?labels=correction&title=Archive%20correction";

export const POST: APIRoute = async ({ request }) => {
  const verification = await checkBotId();

  if (verification.isBot) {
    return new Response(JSON.stringify({ error: "Access denied" }), {
      status: 403,
      headers: { "Content-Type": "application/json" },
    });
  }

  let body: { message?: string; source?: string } = {};
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const message = body.message?.trim();
  if (!message) {
    return new Response(JSON.stringify({ error: "message is required" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  // Corrections are tracked on GitHub; this endpoint is bot-gated for future in-site forms.
  return new Response(
    JSON.stringify({
      ok: true,
      message: "Correction received. For now, please also open a GitHub issue with your source.",
      github_issues_url: GITHUB_ISSUES_URL,
    }),
    {
      status: 202,
      headers: { "Content-Type": "application/json" },
    },
  );
};
