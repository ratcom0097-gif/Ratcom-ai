import "dotenv/config";
import express from "express";
import { sessionRouter } from "./routes/sessions.js";
import { webhookRouter } from "./routes/webhooks.js";
import { healthRouter } from "./routes/health.js";
import { paymentRouter } from "./routes/payments.js";
import { requireApiKey } from "./middleware/auth.js";
import { logger } from "./lib/logger.js";

const app = express();
const PORT = process.env.PORT || 3000;

// ── Middleware ──────────────────────────────────────────
app.use(express.json());
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`);
  next();
});

// ── Routes publiques ───────────────────────────────────
app.use("/health", healthRouter);
app.use("/api/payments/notify", paymentRouter); // webhook CinetPay — public

// ── Routes protégées ───────────────────────────────────
app.use("/api/sessions", requireApiKey, sessionRouter);
app.use("/api/webhooks", requireApiKey, webhookRouter);
app.use("/api/payments", requireApiKey, paymentRouter);

// ── Erreurs globales ───────────────────────────────────
app.use((err, req, res, next) => {
  logger.error(err.message);
  res.status(500).json({ error: "Erreur interne du serveur" });
});

app.listen(PORT, () => {
  logger.info(`🚀 RIAL AI Backend démarré sur le port ${PORT}`);
});
