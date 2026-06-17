import { Router } from "express";

export const webhookRouter = Router();

// Stockage simple des configs webhook par session
const webhookConfigs = new Map();

/* GET /api/webhooks
   Liste les webhooks configurés */
webhookRouter.get("/", (req, res) => {
  const list = [];
  for (const [sessionId, config] of webhookConfigs.entries()) {
    list.push({ sessionId, ...config });
  }
  res.json({ webhooks: list });
});

/* POST /api/webhooks
   Configure un webhook sortant pour une session
   Corps : { sessionId, url, events? } */
webhookRouter.post("/", (req, res) => {
  const { sessionId, url, events } = req.body;
  if (!sessionId || !url) {
    return res.status(400).json({ error: "sessionId et url requis" });
  }

  webhookConfigs.set(sessionId, {
    url,
    events: events ?? ["message.received", "message.sent"],
    createdAt: new Date().toISOString(),
  });

  res.json({
    message: "Webhook configuré",
    sessionId,
    url,
    webhookUrl: `${req.protocol}://${req.get("host")}/api/webhooks/incoming/${sessionId}`,
  });
});

/* DELETE /api/webhooks/:sessionId
   Supprime la config webhook d'une session */
webhookRouter.delete("/:sessionId", (req, res) => {
  if (!webhookConfigs.has(req.params.sessionId)) {
    return res.status(404).json({ error: "Webhook introuvable" });
  }
  webhookConfigs.delete(req.params.sessionId);
  res.json({ message: "Webhook supprimé" });
});

export function getWebhookConfig(sessionId) {
  return webhookConfigs.get(sessionId) ?? null;
}
