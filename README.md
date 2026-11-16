# Telegram bot for betting slip analysis

Telegram bot only for the first version (no Mini App). Users register with the affiliate link, a first-deposit postback unlocks access, then users send a betting slip screenshot to the bot. GPT analyzes the visible details. The daily limit is 3 successful analyses per UTC day.

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
- To use the in-bot admin panel, run `/myid` in the bot, copy your numeric Telegram ID, set `ADMIN_IDS` to that value in Bothost, and restart/redeploy.
- Add the main bot as an administrator to the private channel that receives affiliate postbacks.

## Admin panel inside Telegram

Send `/admin` to open the inline panel. Its buttons appear under the message. The previous panel message is deleted when you select a section. You can edit the referral link, promo code, and built-in Russian and English bot copy. The `/myid` command shows the Telegram ID required for `ADMIN_IDS`.

The bot can accept the base affiliate link as shown in the 1win panel and automatically append a unique `sub1` for each user. If the URL template already contains `sub1={click_id}` (or `{sub1}`), it substitutes the unique ID there. Configure the postback message in the format `{sub1}|Firstdep|{amount}`; registration events may use `Registration` or `Reg`. Verify these labels and the returned `sub1` with test events before live use.

## Notes

- GPT analysis uses only the screenshot; this version does not retrieve live odds, lineups, injuries, or sports statistics.
- Images are sent to the OpenAI API for analysis and are not stored in this app.
- `.env` and API credentials must never be committed to GitHub.

