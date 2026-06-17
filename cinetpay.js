import axios from "axios";
import { logger } from "../lib/logger.js";

/*
  CinetPay — Paiements Mobile Money pour RIAL AI
  Supports : Orange Money, MTN MoMo, Moov, Wave
  Docs : https://docs.cinetpay.com
*/

const CINETPAY_API = "https://api-checkout.cinetpay.com/v2/payment";
const SITE_ID = process.env.CINETPAY_SITE_ID;
const API_KEY = process.env.CINETPAY_API_KEY;

// ── Plans RIAL AI ─────────────────────────────────────
export const PLANS = {
  starter: {
    id: "starter",
    name: "RIAL AI Starter",
    amount: 5000,
    currency: "XAF",
    messages: 1000,
    lines: 1,
  },
  pme: {
    id: "pme",
    name: "RIAL AI PME",
    amount: 10000,
    currency: "XAF",
    messages: 5000,
    lines: 3,
  },
  business: {
    id: "business",
    name: "RIAL AI Business Pro",
    amount: 25000,
    currency: "XAF",
    messages: -1, // illimité
    lines: 10,
  },
  premium: {
    id: "premium",
    name: "RIAL AI Premium",
    amount: 50000,
    currency: "XAF",
    messages: -1,
    lines: -1,
  },
};

/* ────────────────────────────────────────────────────
   Initier un paiement CinetPay
   Retourne : { paymentUrl, transactionId }
──────────────────────────────────────────────────── */
export async function initiatePayment({ planId, customerName, customerEmail, customerPhone, customerId }) {
  const plan = PLANS[planId];
  if (!plan) throw new Error(`Plan inconnu : ${planId}`);

  const transactionId = `RIAL-${customerId}-${Date.now()}`;

  const payload = {
    apikey: API_KEY,
    site_id: SITE_ID,
    transaction_id: transactionId,
    amount: plan.amount,
    currency: plan.currency,
    alternative_currency: "",
    description: `Abonnement ${plan.name} — 1 mois`,
    customer_id: customerId,
    customer_name: customerName,
    customer_email: customerEmail,
    customer_phone_number: customerPhone,
    customer_address: "Douala, Cameroun",
    customer_city: "Douala",
    customer_country: "CM",
    customer_state: "CM",
    customer_zip_code: "00237",
    notify_url: `${process.env.BACKEND_URL}/api/payments/notify`,
    return_url: `${process.env.FRONTEND_URL}/dashboard?payment=success`,
    channels: "MOBILE_MONEY",
    metadata: JSON.stringify({ planId, customerId }),
    lang: "fr",
    invoice_data: {
      Plan: plan.name,
      Messages: plan.messages === -1 ? "Illimités" : `${plan.messages}/mois`,
      Lignes: plan.lines === -1 ? "Illimitées" : plan.lines,
    },
  };

  const res = await axios.post(CINETPAY_API, payload);

  if (res.data.code !== "201") {
    logger.error(`CinetPay erreur: ${JSON.stringify(res.data)}`);
    throw new Error(res.data.message ?? "Erreur CinetPay");
  }

  logger.info(`[CinetPay] Paiement initié — ${transactionId} — ${plan.amount} XAF`);

  return {
    paymentUrl: res.data.data.payment_url,
    transactionId,
    plan,
  };
}

/* ────────────────────────────────────────────────────
   Vérifier le statut d'une transaction
──────────────────────────────────────────────────── */
export async function checkPayment(transactionId) {
  const res = await axios.post("https://api-checkout.cinetpay.com/v2/payment/check", {
    apikey: API_KEY,
    site_id: SITE_ID,
    transaction_id: transactionId,
  });

  return {
    status: res.data.data?.status,        // ACCEPTED | REFUSED | PENDING
    amount: res.data.data?.amount,
    paymentMethod: res.data.data?.payment_method,
    paidAt: res.data.data?.payment_date,
  };
}
