# Telegram bot for betting slip analysis

First version: Telegram bot only (no Mini App). Users request access, registration and first-deposit events arrive as posts in a private Telegram channel, and GPT analyzes a screenshot sent to the bot. Daily quota is 3 successful analyses per UTC day (a failed API request is refunded).

## Local setup

1. Install Python 3.11+.
2. Copy `.env.example` to `.env` and fill in the secrets and IDs.
3. Install dependencies: `python -m pip install -r requirements.txt`.
4. Start the bot and health endpoint: `python main.py`.

The bot polls Telegram updates and serves `GET /health` on port 8000 (or the `PORT` environment variable).

## Telegram and affiliate setup

- Add the main bot to the private postback channel. Set `POSTBACK_CHANNEL_ID` to that channel's numeric ID (usually starts with `-100`). The bot needs to receive channel posts.
- Configure the affiliate postback so the message is pipe-separated, e.g. `{sub1}|Firstdep|{amount}`. The first field should be the `sub1` click ID, and the event should include `Firstdep`, `deposit`, `registration`, or `reg`.
- Set `ADMIN_IDS` to comma-separated numeric Telegram user IDs if you want to use admin commands in the bot (optional when using the web panel).
- Set `ADMIN_USERNAME` and a strong `ADMIN_PASSWORD`; the private settings page is available at `/admin` on the deployed service.
- As an admin, use `/set_referral https://affiliate.example/link?sub1={click_id}` and `/set_promo CODE`. The bot replaces `{click_id}` (or `{sub1}`) for each user and stores the mapping. If no marker appears in the URL, it appends `sub1=<click_id>`.
- Use `/get_referral` and `/get_promo` to inspect the settings. `/set_promo -` clears the promo code.

Before using live traffic, verify with test postbacks that the `sub1` value reaches the channel unchanged and matches the click ID in the generated affiliate link. The event parser recognizes registration/deposit event names; adjust it if the affiliate panel uses other labels.

## Admin commands

- `/admin` — show command help.
- `/set_referral <URL>` — update affiliate URL. Include `sub1={click_id}` in the URL template if the affiliate system supports it.
- `/set_promo <code or ->` — set or clear promo code.
- `/get_referral`, `/get_promo` — inspect current settings. You can also edit both values in the password-protected `/admin` web page.

## Deploying on Bothost

Connect the GitHub repository in Bothost and let it install dependencies from the root `requirements.txt`. The root `main.py` starts the bot and the `/health` and password-protected `/admin` web routes. In the bot settings, set the Python entrypoint to `main.py` if Bothost does not detect it automatically.

Add runtime values in the Bothost dashboard under the bot's environment variable settings. `BOT_TOKEN` is supplied by Bothost's Telegram bot setup; check that it is available to the container. Add `OPENAI_API_KEY`, `POSTBACK_CHANNEL_ID`, `ADMIN_PASSWORD`, and optionally `ADMIN_USERNAME`, `ADMIN_IDS`, `OPENAI_MODEL`, `DAILY_ANALYSIS_LIMIT`, and `DB_PATH` (set it to `/app/data/bot.sqlite3`).

The web admin page requires a public domain/HTTPS route and the web port configured to match the `PORT` environment value (the app defaults to 8000 when it is not set). Open `https://<your-bot-domain>/admin` after deployment. The referral URL template and promo code are entered on this page, not in GitHub or environment variables.

SQLite stores the database in a single file. On Bothost set `DB_PATH=/app/data/bot.sqlite3`, because `/app/data` is the persistent storage directory. Local development defaults to `./data/bot.sqlite3`.

All built-in Russian and English bot copy, including button labels, is editable on `/admin`. GPT's generated analysis is dynamic; its system instructions are separate from these editable message templates.

## Notes

- Analysis is based only on what is visible in the submitted screenshot. This version does not query live odds, lineups, injuries, or sports statistics.
- Images are downloaded to memory for the request and are not stored by this app. OpenAI API data handling is subject to your API account's terms/settings.
- `OPENAI_MODEL` can be changed in the hosting environment to another vision-capable model available to your API account.
- Never commit `.env` or publish bot/API credentials.

