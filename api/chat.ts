// Vercel Serverless Function — Cytria AI Copilot (MiniMax M3)
import { readFileSync, existsSync } from "fs";
import { join } from "path";

export const config = {
  runtime: "nodejs",
};

export default async function handler(req: any, res: any) {
  // CORS Headers
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    const messages = body.messages || [];
    const activeSuite = body.active_suite || "MARKET";

    const apiKey = process.env.MINIMAX_API_KEY || "";
    const baseUrl = process.env.MINIMAX_BASE_URL || "https://api.minimax.io/anthropic";
    const model = process.env.MINIMAX_MODEL || "MiniMax-M3";

    // System prompt with Swiss French real estate rules
    let rulesText = "";
    try {
      const p = join(process.cwd(), "Prompts", "swiss_french_real_estate_rules.md");
      if (existsSync(p)) rulesText = readFileSync(p, "utf-8");
    } catch (e) {}

    const systemPrompt = `
Tu es CYTRIA COPILOT, l'intelligence foncière et notariée de Genève (FAO × SITG).
Mode actif : ${activeSuite} (Marché / Sourcing / Agency BI).
${rulesText}

Tu réponds de façon synthétique, rigoureuse et élégante en respectant scrupuleusement la typographie suisse (CHF 1'450'000, 1'200 m²).
Si des parcelles ou adresses genevoises précises sont identifiées, tu peux inclure un bloc \`\`\`map_actions avec des coordonnées pour piloter la carte.
`.trim();

    if (!apiKey || apiKey.includes("votre_cle_api")) {
      return res.status(200).json({
        reply: "### 🇨🇭 Cytria Copilot (Vercel Node)\n\nLe copilote est prêt. Veuillez configurer la variable d'environnement `MINIMAX_API_KEY` dans vos **Vercel Project Settings > Environment Variables** pour activer le modèle MiniMax M3.",
        map_actions: [],
        model_used: "MiniMax-M3 (Attente Clé API Vercel)",
        tools_called: []
      });
    }

    // Call MiniMax
    const isAnthropic = baseUrl.includes("/anthropic");
    const endpoint = isAnthropic ? `${baseUrl.replace(/\/+$/, "")}/v1/messages` : `${baseUrl.replace(/\/+$/, "")}/text/chatcompletion_v2`;

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${apiKey}`
    };

    let payload: any;
    if (isAnthropic) {
      headers["anthropic-version"] = "2023-06-01";
      payload = {
        model,
        max_tokens: 1500,
        system: systemPrompt,
        messages: messages.filter((m: any) => m.role !== "system"),
      };
    } else {
      payload = {
        model,
        messages: [{ role: "system", content: systemPrompt }, ...messages],
        temperature: 0.15,
      };
    }

    const apiRes = await fetch(endpoint, {
      method: "POST",
      headers,
      body: JSON.stringify(payload)
    });

    if (!apiRes.ok) {
      const err = await apiRes.text();
      return res.status(apiRes.status).json({ error: `MiniMax API Error: ${err}` });
    }

    const data = await apiRes.json();
    let replyText = "";
    if (isAnthropic) {
      const textBlock = data.content?.find((c: any) => c.type === "text");
      replyText = textBlock?.text || "";
    } else {
      replyText = data.choices?.[0]?.message?.content || "";
    }

    // Extract map actions if present
    const mapActions: any[] = [];
    const regex = /```map_actions\s*([\s\S]*?)\s*```/i;
    const match = replyText.match(regex);
    if (match && match[1]) {
      try {
        const parsed = JSON.parse(match[1]);
        if (Array.isArray(parsed)) mapActions.push(...parsed);
        replyText = replyText.replace(regex, "").trim();
      } catch (e) {}
    }

    return res.status(200).json({
      reply: replyText,
      map_actions: mapActions,
      model_used: model,
      tools_called: []
    });

  } catch (error: any) {
    return res.status(500).json({ error: error.message || "Erreur serveur Copilot Vercel" });
  }
}
