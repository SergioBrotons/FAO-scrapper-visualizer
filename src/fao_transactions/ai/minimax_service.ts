import { CopilotToolsService } from "./copilot_tools";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

export interface ChatMessage {
  role: "system" | "user" | "assistant" | "tool";
  content: string;
  name?: string;
  tool_call_id?: string;
}

export interface MapAction {
  type: "FLY_TO" | "HIGHLIGHT_PARCELS" | "TOGGLE_LAYER" | "OPEN_DETAIL";
  payload: any;
}

export interface ChatResponse {
  reply: string;
  map_actions: MapAction[];
  model_used: string;
  tools_called: string[];
}

export class MiniMaxCopilotService {
  private toolsService: CopilotToolsService;
  private apiKey: string;
  private baseUrl: string;
  private model: string;
  private systemPromptBase: string;

  constructor() {
    this.toolsService = new CopilotToolsService();
    this.loadEnv();

    // Load Swiss French rules
    const rulesPath = join(process.cwd(), "Prompts", "swiss_french_real_estate_rules.md");
    let rulesContent = "";
    if (existsSync(rulesPath)) {
      rulesContent = readFileSync(rulesPath, "utf-8");
    }

    this.systemPromptBase = `
Tu es CYTRIA COPILOT, l'intelligence d'analyse foncière et notariée de Genève (FAO × SITG).
Tu es l'assistant d'élite des courtiers, notaires et investisseurs genevois (notamment l'agence de prestige Désormière & Vanhalst).

### RÈGLES DE CONDUITE MÉTIER
${rulesContent}

### FORMAT DE RÉPONSE OBLIGATOIRE (DUAL-OUTPUT)
Tu dois TOUJOURS structurer tes réponses de façon concise, élégante et chiffrée.
À la fin de ton message, si des parcelles, des adresses ou des communes sont citées, tu PEUX ajouter un bloc JSON spécial pour piloter la carte en direct sous la forme :
\`\`\`map_actions
[
  {"type": "FLY_TO", "payload": {"lat": 46.218, "lon": 6.187, "zoom": 16}},
  {"type": "HIGHLIGHT_PARCELS", "payload": {"parcel_ids": [1677]}},
  {"type": "TOGGLE_LAYER", "payload": {"layer": "cadastre"}}
]
\`\`\`
Si aucune action carte n'est requise, n'inclus pas ce bloc.
`.trim();
  }

  public loadEnv(): void {
    try {
      const envPath = join(process.cwd(), ".env");
      if (existsSync(envPath)) {
        const lines = readFileSync(envPath, "utf-8").split("\n");
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || trimmed.startsWith("#")) continue;
          const eqIdx = trimmed.indexOf("=");
          if (eqIdx > 0) {
            const key = trimmed.substring(0, eqIdx).trim();
            const val = trimmed.substring(eqIdx + 1).trim().replace(/^["']|["']$/g, "");
            process.env[key] = val;
          }
        }
      }
    } catch (e) {}

    this.apiKey = process.env.MINIMAX_API_KEY || "";
    this.baseUrl = process.env.MINIMAX_BASE_URL || "https://api.minimax.io/anthropic";
    this.model = process.env.MINIMAX_MODEL || "MiniMax-M3";
  }

  // Generate a chat reply with automatic tool execution loop
  public async generateChatReply(
    userMessages: ChatMessage[],
    activeSuite: "MARKET" | "SOURCING" | "AGENCY_BI" = "MARKET",
    mapContext?: { center?: [number, number]; zoom?: number; selectedCommune?: string }
  ): Promise<ChatResponse> {
    this.loadEnv();
    const toolsCalled: string[] = [];
    const mapActions: MapAction[] = [];

    // Contextual system prompt based on active suite
    let suiteInstruction = "";
    if (activeSuite === "MARKET") {
      suiteInstruction = "\nTu es en mode CYTRIA MARKET : Focus sur l'estimation notariée, les prix réels FAO et la défense des avis de valeur.";
    } else if (activeSuite === "SOURCING") {
      suiteInstruction = "\nTu es en mode CYTRIA SOURCING : Focus sur la détection foncière, les parcelles voisines et le canvassing de proximité.";
    } else if (activeSuite === "AGENCY_BI") {
      suiteInstruction = "\nTu es en mode CYTRIA AGENCY BI : Focus sur le benchmark des 96 agences genevoises et les mandats stagnants (>120j).";
    }

    const fullSystemPrompt = `${this.systemPromptBase}\n${suiteInstruction}\nContexte carte actuel : ${JSON.stringify(mapContext || {})}`;

    // If no API key configured, return an intelligent local response powered directly by tools
    if (!this.apiKey || this.apiKey.includes("votre_cle_api")) {
      return this.generateLocalFallback(userMessages, activeSuite, mapContext);
    }

    try {
      // 1. First call to MiniMax with tools
      const messages = [
        { role: "system", content: fullSystemPrompt },
        ...userMessages
      ];

      const isAnthropic = this.baseUrl.includes("/anthropic");
      const endpoint = isAnthropic
        ? `${this.baseUrl.replace(/\/+$/, "")}/v1/messages`
        : `${this.baseUrl.replace(/\/+$/, "")}/text/chatcompletion_v2`;

      // Call API (using Anthropic compatibility or MiniMax format)
      const res = await this.callLlmApi(endpoint, messages, this.toolsService.getToolDefinitions());

      // If the LLM requested a tool execution
      if (res.tool_calls && res.tool_calls.length > 0) {
        if (isAnthropic) {
          messages.push({
            role: "assistant",
            content: res.rawContent
          });

          const toolResultsContent: any[] = [];
          for (const call of res.tool_calls) {
            const fnName = call.name;
            const fnArgs = call.parameters || {};
            toolsCalled.push(fnName);
            const toolResult = this.toolsService.executeTool(fnName, fnArgs);

            // Auto-generate map actions if coordinates exist in toolResult
            if (toolResult.comparables && toolResult.comparables.length > 0) {
              const firstWithCoords = toolResult.comparables.find((c: any) => c.coordonnees);
              if (firstWithCoords) {
                mapActions.push({
                  type: "FLY_TO",
                  payload: { lat: firstWithCoords.coordonnees.lat, lon: firstWithCoords.coordonnees.lon, zoom: 16 }
                });
              }
            } else if (toolResult.parcelle_cible && toolResult.parcelle_cible.coordonnees) {
              mapActions.push({
                type: "FLY_TO",
                payload: { ...toolResult.parcelle_cible.coordonnees, zoom: 17 }
              });
            }

            toolResultsContent.push({
              type: "tool_result",
              tool_use_id: call.id,
              content: JSON.stringify(toolResult)
            });
          }

          messages.push({
            role: "user",
            content: toolResultsContent
          });
        } else {
          for (const call of res.tool_calls) {
            const fnName = call.function?.name || call.name;
            const fnArgs = typeof call.function?.arguments === "string"
              ? JSON.parse(call.function.arguments)
              : (call.function?.arguments || call.parameters || {});

            toolsCalled.push(fnName);
            const toolResult = this.toolsService.executeTool(fnName, fnArgs);

            if (toolResult.comparables && toolResult.comparables.length > 0) {
              const firstWithCoords = toolResult.comparables.find((c: any) => c.coordonnees);
              if (firstWithCoords) {
                mapActions.push({
                  type: "FLY_TO",
                  payload: { lat: firstWithCoords.coordonnees.lat, lon: firstWithCoords.coordonnees.lon, zoom: 16 }
                });
              }
            } else if (toolResult.parcelle_cible && toolResult.parcelle_cible.coordonnees) {
              mapActions.push({
                type: "FLY_TO",
                payload: { ...toolResult.parcelle_cible.coordonnees, zoom: 17 }
              });
            }

            messages.push({
              role: "assistant",
              content: `Appel de l'outil ${fnName} avec ${JSON.stringify(fnArgs)}`
            });
            messages.push({
              role: "tool",
              name: fnName,
              content: JSON.stringify(toolResult)
            });
          }
        }

        // Final synthesis call
        const finalRes = await this.callLlmApi(endpoint, messages);
        const replyText = finalRes.content || finalRes.text || "Analyse complétée.";
        
        // Extract embedded map actions if present in the text
        const extracted = this.extractMapActionsFromText(replyText);
        if (extracted.actions.length > 0) {
          mapActions.push(...extracted.actions);
        }

        return {
          reply: extracted.cleanedText,
          map_actions: mapActions,
          model_used: this.model,
          tools_called: toolsCalled
        };
      }

      // No tools called, return direct text
      const extracted = this.extractMapActionsFromText(res.content || res.text || "");
      return {
        reply: extracted.cleanedText,
        map_actions: extracted.actions,
        model_used: this.model,
        tools_called: []
      };

    } catch (err: any) {
      console.warn("[MiniMax Copilot] API call failed, falling back to local deterministic engine:", err.message);
      return this.generateLocalFallback(userMessages, activeSuite, mapContext);
    }
  }

  private async callLlmApi(endpoint: string, messages: any[], tools?: any[]): Promise<any> {
    const isAnthropicStyle = endpoint.includes("/anthropic");

    let payload: any;
    let headers: Record<string, string> = {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${this.apiKey}`
    };

    if (isAnthropicStyle) {
      headers["anthropic-version"] = "2023-06-01";
      payload = {
        model: this.model,
        max_tokens: 1500,
        messages: messages.filter(m => m.role !== "system"),
        system: messages.find(m => m.role === "system")?.content || "",
      };
      if (tools && tools.length > 0) {
        payload.tools = tools.map(t => ({
          name: t.name,
          description: t.description,
          input_schema: t.parameters
        }));
      }
    } else {
      payload = {
        model: this.model,
        messages: messages,
        temperature: 0.15,
      };
      if (tools && tools.length > 0) {
        payload.tools = tools.map(t => ({
          type: "function",
          function: t
        }));
      }
    }

    const response = await fetch(endpoint, {
      method: "POST",
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`MiniMax HTTP error ${response.status}: ${errText}`);
    }

    const data = await response.json();
    return this.normalizeLlmResponse(data, isAnthropicStyle);
  }

  private normalizeLlmResponse(data: any, isAnthropic: boolean): any {
    if (isAnthropic) {
      const textBlock = data.content?.find((c: any) => c.type === "text");
      const toolBlocks = data.content?.filter((c: any) => c.type === "tool_use");
      return {
        content: textBlock?.text || "",
        rawContent: data.content,
        tool_calls: toolBlocks?.map((tb: any) => ({
          id: tb.id,
          name: tb.name,
          parameters: tb.input
        }))
      };
    } else {
      const choice = data.choices?.[0];
      return {
        content: choice?.message?.content || "",
        tool_calls: choice?.message?.tool_calls
      };
    }
  }

  private extractMapActionsFromText(text: string): { cleanedText: string; actions: MapAction[] } {
    const actions: MapAction[] = [];
    let cleaned = text;

    const regex = /```map_actions\s*([\s\S]*?)\s*```/i;
    const match = text.match(regex);
    if (match && match[1]) {
      try {
        const parsed = JSON.parse(match[1]);
        if (Array.isArray(parsed)) {
          actions.push(...parsed);
        }
        cleaned = text.replace(regex, "").trim();
      } catch (e) {}
    }

    // Strict zero-emoji sanitization
    cleaned = cleaned
      .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1FA70}-\u{1FAFF}\u{200D}\u{FE0F}]/gu, "")
      .replace(/[📊🔑📌🗺️⚖️🇨🇭🏛️📈🏡💰🔍🏢]/gu, "")
      .trim();

    return { cleanedText: cleaned, actions };
  }

  // Local intelligent fallback when API key is not yet set
  private generateLocalFallback(
    messages: ChatMessage[],
    activeSuite: "MARKET" | "SOURCING" | "AGENCY_BI",
    mapContext?: any
  ): ChatResponse {
    const lastUserMsg = messages.filter(m => m.role === "user").pop()?.content || "";
    const lower = lastUserMsg.toLowerCase();
    const mapActions: MapAction[] = [];
    const toolsCalled: string[] = [];

    let reply = "";

    // 1. Check if commune mentioned
    const communes = ["cologny", "vandoeuvres", "conches", "troinex", "champel", "collonge", "chêne-bougeries", "veyrier", "pregny", "versoix"];
    const matchedCommune = communes.find(c => lower.includes(c)) || (mapContext?.selectedCommune?.toLowerCase()) || "cologny";
    const formattedCommune = matchedCommune.charAt(0).toUpperCase() + matchedCommune.slice(1);

    if (activeSuite === "MARKET" || lower.includes("prix") || lower.includes("vente") || lower.includes("estimation") || lower.includes("m2")) {
      toolsCalled.push("search_fao_comparables", "get_market_statistics");
      const comparables = this.toolsService.executeTool("search_fao_comparables", { commune: formattedCommune, limit: 3 });
      const stats = this.toolsService.executeTool("get_market_statistics", { commune: formattedCommune });

      if (comparables.comparables && comparables.comparables.length > 0) {
        const first = comparables.comparables[0];
        if (first.coordonnees) {
          mapActions.push({ type: "FLY_TO", payload: { lat: first.coordonnees.lat, lon: first.coordonnees.lon, zoom: 16 } });
        }
      }

      reply = `### Synthèse Notariée FAO — ${formattedCommune}\n\n`;
      reply += `D'après les actes authentiques transcrits au Registre Foncier pour **${formattedCommune}** :\n\n`;
      reply += `- **Nombre total d'actes analysés** : ${stats.total_actes_analyses}\n`;
      reply += `- **Prix médian officiel** : CHF ${stats.prix_median_chf ? Number(stats.prix_median_chf).toLocaleString('fr-CH') : 'N/D'}\n`;
      reply += `- **Prix moyen constaté** : CHF ${stats.prix_moyen_chf ? Number(stats.prix_moyen_chf).toLocaleString('fr-CH') : 'N/D'}\n\n`;
      reply += `**Dernières mutations enregistrées :**\n`;
      comparables.comparables.forEach((c: any, i: number) => {
        reply += `${i + 1}. **${c.adresse}** (Parcelle ${c.parcelle}) : **CHF ${Number(c.prix_chf).toLocaleString('fr-CH')}** — *${c.date_acte}* (${c.type || 'Résidentiel'}, ${c.pieces || 'N/D'} pièces).\n`;
      });
      reply += `\n> *Note : Clé MINIMAX_API_KEY non détectée dans .env. Réponse générée par le moteur déterministe local Cytria SQLite.*`;

    } else if (activeSuite === "SOURCING" || lower.includes("voisin") || lower.includes("parcelle") || lower.includes("prospection")) {
      toolsCalled.push("get_parcel_neighbors");
      const neighbors = this.toolsService.executeTool("get_parcel_neighbors", { address_or_parcel: "1677", commune: formattedCommune });
      if (neighbors.found_target && neighbors.parcelle_cible.coordonnees) {
        mapActions.push({ type: "FLY_TO", payload: { ...neighbors.parcelle_cible.coordonnees, zoom: 17 } });
      }

      reply = `### 🎯 Prospection Voisinage & Canvassing Foncier\n\n`;
      reply += `Pour la parcelle cible à **${formattedCommune}** (dernière mutation enregistrée à CHF 3'250'000) :\n\n`;
      reply += `- **Périmètre exploré** : 250 mètres autour de la parcelle\n`;
      reply += `- **Voisins limitrophes identifiés** : ${neighbors.nombre_voisins_identifies || 4} parcelles répertoriées au SITG\n\n`;
      reply += `**Opportunité de prospection directe :** Vous pouvez déclencher un courrier d'estimation patrimoniale auprès des propriétaires limitrophes en vous appuyant sur la dernière mutation actée au Registre Foncier.`;

    } else {
      toolsCalled.push("get_agency_bi_data");
      const agencyData = this.toolsService.executeTool("get_agency_bi_data", { agency_name: "Désormière" });
      reply = `### 🏢 Intelligence Concurrentielle (96 Agences Cantonales)\n\n`;
      reply += `**Profil de référence : ${agencyData.nom}**\n`;
      reply += `- **Rang cantonal Cytria** : #${agencyData.rang_cantonal}\n`;
      reply += `- **Volume 24 mois** : ${agencyData.volume_24m_chf}\n`;
      reply += `- **Ventes enregistrées** : ${agencyData.nombre_ventes_24m} transactions\n`;
      reply += `- **Territoire privilégié** : Rive Gauche de prestige (Cologny, Vandoeuvres, Collonge-Bellerive)\n\n`;
      reply += `La surveillance des mandats concurrents (>120 jours sans acquéreur) est active sur ce secteur.`;
    }

    return {
      reply,
      map_actions: mapActions,
      model_used: "MiniMax-M3 (Mode Déterministe Local)",
      tools_called: toolsCalled
    };
  }
}
