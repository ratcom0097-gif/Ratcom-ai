import { logger } from "./logger.js";

/*
  Synchronise chaque échange dans une Google Sheet.
  Structure des colonnes :
  Date | Session | Téléphone | Message client | Réponse IA
  
  Pour activer : remplissez GOOGLE_SERVICE_ACCOUNT_EMAIL, GOOGLE_PRIVATE_KEY
  et GOOGLE_SHEET_ID dans votre .env.
*/

let sheetsClient = null;

async function getClient() {
  if (sheetsClient) return sheetsClient;
  if (!process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL || !process.env.GOOGLE_PRIVATE_KEY) {
    return null; // Sheets non configuré
  }

  // Import dynamique pour éviter l'erreur si googleapis n'est pas installé
  try {
    const { google } = await import("googleapis");
    const auth = new google.auth.JWT(
      process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
      null,
      process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, "\n"),
      ["https://www.googleapis.com/auth/spreadsheets"]
    );
    sheetsClient = google.sheets({ version: "v4", auth });
    return sheetsClient;
  } catch (e) {
    logger.warn("googleapis non installé — synchronisation Sheets désactivée");
    return null;
  }
}

export async function syncToSheets({ sessionId, senderPhone, userMessage, aiReply }) {
  const client = await getClient();
  if (!client || !process.env.GOOGLE_SHEET_ID) return;

  const now = new Date().toLocaleString("fr-FR", { timeZone: "Africa/Douala" });
  const row = [now, sessionId, senderPhone, userMessage, aiReply];

  await client.spreadsheets.values.append({
    spreadsheetId: process.env.GOOGLE_SHEET_ID,
    range: "Conversations!A:E",
    valueInputOption: "USER_ENTERED",
    requestBody: { values: [row] },
  });

  logger.info(`[Sheets] Ligne ajoutée pour ${senderPhone}`);
}
