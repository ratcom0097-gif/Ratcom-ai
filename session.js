import makeWASocket, {
  useMultiFileAuthState,
  DisconnectReason,
  fetchLatestBaileysVersion,
} from "@whiskeysockets/baileys";
import { Boom } from "@hapi/boom";
import qrcode from "qrcode";
import { logger } from "../lib/logger.js";
import { askClaude } from "./claude.js";
import { syncToSheets } from "./sheets.js";
import { syncToHubspot } from "./hubspot.js";
import { notifyWebhook } from "./webhook.js";
import path from "path";
import fs from "fs";

// sessions actives en mémoire : sessionId → { socket, status, qr, phone }
const sessions = new Map();

const SESSIONS_DIR = "./sessions_auth";
if (!fs.existsSync(SESSIONS_DIR)) fs.mkdirSync(SESSIONS_DIR);

/* ────────────────────────────────────────────────────────────
   Créer ou reprendre une session WhatsApp
   sessionId  : identifiant unique du client (ex: "client_abc")
   aiPrompt   : prompt système IA personnalisé par client
   onQR       : callback appelé avec le QR code en base64 PNG
   onReady    : callback appelé quand la session est connectée
──────────────────────────────────────────────────────────── */
export async function createSession({ sessionId, aiPrompt, onQR, onReady }) {
  if (sessions.has(sessionId)) {
    logger.warn(`Session ${sessionId} déjà existante`);
    return sessions.get(sessionId);
  }

  const authDir = path.join(SESSIONS_DIR, sessionId);
  const { state, saveCreds } = await useMultiFileAuthState(authDir);
  const { version } = await fetchLatestBaileysVersion();

  const sock = makeWASocket({
    version,
    auth: state,
    printQRInTerminal: false,
    logger: logger.child({ module: "baileys" }),
  });

  const session = { socket: sock, status: "pending", qr: null, phone: null };
  sessions.set(sessionId, session);

  // ── Événements de connexion ──────────────────────────
  sock.ev.on("connection.update", async (update) => {
    const { connection, lastDisconnect, qr } = update;

    if (qr) {
      // Générer le QR code en base64 PNG pour l'afficher dans le dashboard
      const qrBase64 = await qrcode.toDataURL(qr);
      session.qr = qrBase64;
      session.status = "qr_ready";
      logger.info(`[${sessionId}] QR code généré`);
      if (onQR) onQR(qrBase64);
    }

    if (connection === "open") {
      session.status = "connected";
      session.phone = sock.user?.id?.split(":")[0] ?? "inconnu";
      session.qr = null;
      logger.info(`[${sessionId}] Connecté — ${session.phone}`);
      if (onReady) onReady(session.phone);
    }

    if (connection === "close") {
      const shouldReconnect =
        new Boom(lastDisconnect?.error)?.output?.statusCode !==
        DisconnectReason.loggedOut;

      logger.warn(`[${sessionId}] Déconnecté. Reconnexion: ${shouldReconnect}`);
      session.status = "disconnected";
      sessions.delete(sessionId);

      if (shouldReconnect) {
        // Attendre 3 secondes puis reconnecter
        setTimeout(() => createSession({ sessionId, aiPrompt, onQR, onReady }), 3000);
      }
    }
  });

  // ── Sauvegarde des credentials ───────────────────────
  sock.ev.on("creds.update", saveCreds);

  // ── Réception des messages entrants ─────────────────
  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;

    for (const msg of messages) {
      // Ignorer nos propres messages et les messages sans contenu texte
      if (msg.key.fromMe) continue;
      const text =
        msg.message?.conversation ||
        msg.message?.extendedTextMessage?.text;
      if (!text) continue;

      const from = msg.key.remoteJid;
      const senderPhone = from.replace("@s.whatsapp.net", "");
      logger.info(`[${sessionId}] Message reçu de ${senderPhone}: ${text}`);

      try {
        // 1. Réponse IA via Claude
        const reply = await askClaude({
          userMessage: text,
          senderPhone,
          systemPrompt: aiPrompt || defaultSystemPrompt(sessionId),
        });

        // 2. Envoyer la réponse WhatsApp
        await sock.sendMessage(from, { text: reply });
        logger.info(`[${sessionId}] Réponse envoyée à ${senderPhone}`);

        // 3. Synchronisation Google Sheets (asynchrone, ne bloque pas)
        syncToSheets({ sessionId, senderPhone, userMessage: text, aiReply: reply }).catch(
          (e) => logger.error(`Sheets sync error: ${e.message}`)
        );

        // 4. Synchronisation HubSpot (asynchrone)
        syncToHubspot({ sessionId, senderPhone, userMessage: text, aiReply: reply }).catch(
          (e) => logger.error(`HubSpot sync error: ${e.message}`)
        );

        // 5. Notification webhook sortant (asynchrone)
        notifyWebhook({ sessionId, senderPhone, userMessage: text, aiReply: reply }).catch(
          (e) => logger.error(`Webhook error: ${e.message}`)
        );
      } catch (err) {
        logger.error(`[${sessionId}] Erreur traitement message: ${err.message}`);
      }
    }
  });

  return session;
}

/* ── Helpers ─────────────────────────────────────────── */

export function getSession(sessionId) {
  return sessions.get(sessionId) ?? null;
}

export function getAllSessions() {
  const result = [];
  for (const [id, s] of sessions.entries()) {
    result.push({ id, status: s.status, phone: s.phone });
  }
  return result;
}

export async function deleteSession(sessionId) {
  const session = sessions.get(sessionId);
  if (!session) return false;
  try {
    await session.socket.logout();
  } catch (_) {}
  sessions.delete(sessionId);
  // Supprimer les credentials stockés
  const authDir = path.join(SESSIONS_DIR, sessionId);
  if (fs.existsSync(authDir)) fs.rmSync(authDir, { recursive: true });
  return true;
}

function defaultSystemPrompt(sessionId) {
  return `Tu es un assistant WhatsApp intelligent propulsé par RIAL AI.
Tu représentes l'entreprise associée à la session ${sessionId}.
Réponds de manière professionnelle, concise et utile.
Si tu ne connais pas la réponse, dis-le poliment et propose de transférer à un humain.
Réponds dans la même langue que le client.`;
}
