import { Router } from "express";
import { initiatePayment, checkPayment, PLANS } from "../lib/cinetpay.js";
import { logger } from "../lib/logger.js";

export const paymentRouter = Router();

// Stockage simple des abonnements actifs (en prod → base de données Supabase)
const subscriptions = new Map();

/* ── GET /api/payments/plans
   Retourne les plans disponibles */
paymentRouter.get("/plans", (req, res) => {
  res.json({ plans: Object.values(PLANS) });
});

/* ── POST /api/payments/initiate
   Initie un paiement Mobile Money
   Corps : { planId, customerName, customerEmail, customerPhone, customerId } */
paymentRouter.post("/initiate", async (req, res) => {
  const { planId, customerName, customerEmail, customerPhone, customerId } = req.body;

  if (!planId || !customerPhone || !customerId) {
    return res.status(400).json({
      error: "planId, customerPhone et customerId sont requis",
    });
  }

  try {
    const result = await initiatePayment({
      planId,
      customerName: customerName ?? "Client RIAL AI",
      customerEmail: customerEmail ?? "",
      customerPhone,
      customerId,
    });

    // Enregistrer la transaction en attente
    subscriptions.set(result.transactionId, {
      customerId,
      planId,
      status: "pending",
      transactionId: result.transactionId,
      createdAt: new Date().toISOString(),
    });

    res.json({
      paymentUrl: result.paymentUrl,
      transactionId: result.transactionId,
      plan: result.plan,
      message: "Redirigez le client vers paymentUrl pour finaliser le paiement",
    });
  } catch (err) {
    logger.error(`Erreur initiation paiement: ${err.message}`);
    res.status(500).json({ error: err.message });
  }
});

/* ── POST /api/payments/notify
   Webhook appelé automatiquement par CinetPay après paiement
   ⚠️ Route publique — CinetPay n'envoie pas de clé API */
paymentRouter.post("/notify", async (req, res) => {
  const { cpm_trans_id, cpm_site_id } = req.body;

  logger.info(`[CinetPay] Notification reçue — transaction: ${cpm_trans_id}`);

  try {
    // Vérifier le statut réel auprès de CinetPay
    const payment = await checkPayment(cpm_trans_id);

    if (payment.status === "ACCEPTED") {
      const sub = subscriptions.get(cpm_trans_id);
      if (sub) {
        sub.status = "active";
        sub.activatedAt = new Date().toISOString();
        sub.paidAt = payment.paidAt;
        sub.paymentMethod = payment.paymentMethod;
        subscriptions.set(cpm_trans_id, sub);

        logger.info(
          `[CinetPay] ✅ Paiement accepté — client ${sub.customerId} — plan ${sub.planId}`
        );

        // TODO : activer l'abonnement en base de données (Supabase)
        // TODO : envoyer un SMS/WhatsApp de confirmation au client
      }
    } else {
      logger.warn(`[CinetPay] Paiement non accepté — statut: ${payment.status}`);
    }

    // CinetPay attend toujours un 200
    res.status(200).json({ message: "OK" });
  } catch (err) {
    logger.error(`Erreur webhook CinetPay: ${err.message}`);
    res.status(200).json({ message: "OK" }); // toujours 200 pour CinetPay
  }
});

/* ── GET /api/payments/status/:transactionId
   Vérifie le statut d'un paiement */
paymentRouter.get("/status/:transactionId", async (req, res) => {
  const { transactionId } = req.params;

  try {
    const payment = await checkPayment(transactionId);
    const sub = subscriptions.get(transactionId);
    res.json({ payment, subscription: sub ?? null });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

/* ── GET /api/payments/subscriptions
   Liste tous les abonnements (protégé) */
paymentRouter.get("/subscriptions", (req, res) => {
  const list = Array.from(subscriptions.values());
  res.json({
    total: list.length,
    active: list.filter((s) => s.status === "active").length,
    subscriptions: list,
  });
});
