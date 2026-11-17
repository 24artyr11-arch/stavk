# Telegram bot and Mini App for betting slip analysis

Users register with the affiliate link, and the first-deposit postback unlocks access. They can then open the Telegram Mini App, select a sport, and upload a betting slip screenshot for GPT analysis. The daily limit is 3 successful analyses per UTC day. The existing bot screenshot flow remains available.

## Local setup

1. Install Python 3.11+.
2. Copy `.env.example` to `.env` and fill in the secrets and IDs.
3. Install packages: `python -m pip install -r requirements.txt`.
4. Run: `python main.py`.

## Bothost setup

- Connect the GitHub repository, branch `main`, and set the Python entrypoint to `main.py`.
- Set `DB_PATH=/app/data/bot.sqlite3` so SQLite lives in Bothost's persistent data directory.
- Bothost supplies the Telegram `BOT_TOKEN` when the Telegram bot is configured.
- Set `OPENAI_API_KEY` and the numeric `POSTBACK_CHANNEL_ID` in the environment settings.
- Enable a public HTTPS domain for the app in Bothost, set its internal port to `3000`, and set `PORT=3000` in the environment. Set `WEBAPP_URL` to the exact public HTTPS address Bothost assigns (for example, `https://myapp.bothost.ru`). The application serves the Mini App and bot from the same process.
- To use the in-bot admin panel, run `/myid` in the bot, copy your numeric Telegram ID, set `ADMIN_IDS` to that value in Bothost, and restart/redeploy.
- Add the main bot as an administrator to the private channel that receives affiliate postbacks.

## Admin panel inside Telegram

Send `/admin` to open the inline panel. Choose **Texts and media**, then a language, category, and message. For each message, edit its text, attach or remove a photo, change its related button labels, or edit the registration promo code. New text, photo, link, and promo values appear in a preview and are applied only after Save; Cancel discards them. **User analytics** shows registrations, first deposits, active users, and analysis counts.

Confirmed text, image file IDs, button labels, promo code, affiliate link, and analytics source data are stored in SQLite. On Bothost, set `DB_PATH=/app/data/bot.sqlite3`; Bothost preserves `/app/data` across rebuilds. Unconfirmed editor drafts are held in memory and are discarded if the bot restarts before Save.

The bot can accept the base affiliate link as shown in the 1win panel and automatically append a unique `sub1` for each user. If the URL template already contains `sub1={click_id}` (or `{sub1}`), it substitutes the unique ID there. Configure the postback message in the format `{sub1}|Firstdep|{amount}`; registration events may use `Registration` or `Reg`. Verify these labels and the returned `sub1` with test events before live use.

## Notes

- GPT analysis uses only the screenshot; this version does not retrieve live odds, lineups, injuries, or sports statistics.
- The Mini App validates Telegram `initData` on the server before checking access or accepting an image. It shares the same SQLite activation status and UTC daily limit as the bot.
- Images are sent to the OpenAI API for analysis and are not retained by this app. The selected sport is sent as context; the model can still report that the screenshot does not match the selection.
- `.env` and API credentials must never be committed to GitHub.

