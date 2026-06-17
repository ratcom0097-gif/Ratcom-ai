import Anthropic from "@anthropic-ai/sdk";
import { logger } from "./logger.js";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// Historique des conversations en mémoire (sessionId+phone → messages[])
const conversationHistory = new Map();
const MAX_HISTORY = 20; // Garder les 20 derniers échanges

export async function askClaude({ userMessage, senderPhone, systemPrompt }) {
  const historyKey = senderPhone;

  // Récupérer ou initialiser l'historique
  if (!conversationHistory.has(historyKey)) {
    conversationHistory.set(historyKey, []);
  }
  const history = conversationHistory.get(historyKey);

  // Ajouter le message utilisateur
  history.push({ role: "user", content: userMessage });

  // Limiter l'historique
  if (history.length > MAX_HISTORY) {
    history.splice(0, history.length - MAX_HISTORY);
  }

  try {
    const response = await client.messages.create({
      model: "claude-sonnet-4-6",
      max_tokens: 1024,
      system: systemPrompt,
      messages: history,
    });

    const reply = response.content[0]?.text ?? "Je n'ai pas pu générer une réponse.";

    // Ajouter la réponse à l'historique
    history.push({ role: "assistant", content: reply });

    return reply;
  } catch (err) {
    logger.error(`Erreur Claude API: ${err.message}`);
    throw err;
  }
}

export function clearHistory(senderPhone) {
  conversationHistory.delete(senderPhone);
}
