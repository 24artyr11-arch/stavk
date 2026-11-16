TEXTS = {
    "ru": {
        "button_instruction": "📚 Инструкция",
        "button_language": "🌐 Выбрать язык",
        "button_signal": "🎯 Получить сигнал",
        "button_register": "📲 Зарегистрироваться",
        "promo_prefix": "Промокод: ",
        "language_russian": "🇷🇺 Русский",
        "language_english": "🇬🇧 Английский",
        "welcome": "Привет! Здесь можно отправить скриншот купона для осторожного ИИ-анализа. Анализ не гарантирует выигрыш.",
        "menu": "Главное меню:",
        "instruction": "Как пользоваться:\n1. Нажмите «Получить сигнал».\n2. Создайте новый аккаунт 1win по вашей персональной ссылке.\n3. После подтверждения регистрации внесите депозит любого размера.\n4. Когда postback подтвердит депозит, отправьте сюда скриншот купона.\n5. В примере стратегии предлагается после неудачной ставки удвоить следующую, чтобы попытаться покрыть убыток. Это не гарантирует возврат денег и может быстро увеличить потери; заранее установите лимит и не отыгрывайтесь.\n\nДоступно до 3 анализов за сутки (UTC). Анализ вероятностный и не гарантирует выигрыш.",
        "choose_language": "Выберите язык / Choose language:",
        "need_registration": "Чтобы открыть анализ, сначала зарегистрируйтесь в 1win по персональной ссылке. Используйте промокод, если он указан ниже. Доступ активируется после подтверждения регистрации и первого депозита любого размера.",
        "need_deposit": "Регистрация подтверждена. Внесите первый депозит любого размера по той же партнёрской ссылке. После подтверждения postback доступ откроется автоматически.",
        "send_image": "Доступ открыт. Отправьте скриншот купона одним изображением. Лимит — 3 анализа за сутки по UTC.",
        "no_link": "Ссылка ещё не настроена. Попробуйте позже или обратитесь в поддержку.",
        "no_promo": "Промокод: не задан",
        "limit": "Лимит на сегодня исчерпан: 3 анализа в сутки по UTC. Попробуйте после 00:00 UTC.",
        "analyzing": "Скриншот получен, анализирую…",
        "analysis_error": "Не удалось выполнить анализ. Попробуйте позже; неудачный запрос не списан из лимита.",
        "image_only": "Пожалуйста, отправьте скриншот купона как фото или изображение.",
        "risk": "Ставки связаны с риском потери денег. Не используйте деньги, которые не можете позволить себе потерять.",
        "registered": "Регистрация подтверждена. Теперь дождитесь подтверждения первого депозита.",
        "activated": "Первый депозит подтверждён — доступ к анализу открыт. Отправьте скриншот купона.",
        "admin_help": "Команды администратора:\n/set_referral <URL с {click_id} или {sub1}>\n/set_promo <промокод или ->\n/get_referral\n/get_promo",
        "saved": "Сохранено.",
        "set_referral_usage": "Использование: /set_referral https://...sub1={click_id}",
        "set_promo_usage": "Использование: /set_promo <промокод или ->",
        "referral_unset": "Ссылка не настроена.",
        "promo_unset": "Промокод не задан.",
        "button_back": "⬅️ Назад",
        "button_admin": "⚙️ Админ-панель",
        "button_admin_settings": "🔗 Ссылка и промокод",
        "button_edit_ru": "✏️ Тексты на русском",
        "button_edit_en": "✏️ Тексты на английском",
        "button_set_link": "🔗 Изменить ссылку",
        "button_set_promo": "🏷 Изменить промокод",
        "button_cancel": "Отмена",
        "admin_panel": "Панель администратора. Выберите раздел:",
        "admin_choose_setting": "Что изменить?",
        "admin_choose_text": "Выберите текст для редактирования. В кнопках показаны ключ и начало текущего текста:",
        "admin_edit_link_prompt": "Отправьте новую партнёрскую ссылку. В ней должен быть параметр sub1={click_id} или {sub1}.",
        "admin_edit_promo_prompt": "Отправьте новый промокод. Чтобы убрать промокод, отправьте дефис: -",
        "admin_edit_text_prompt": "Текущий текст:\n{current}\n\nОтправьте новое сообщение с текстом. Переносы строк сохраняются.",
        "admin_saved": "✅ Сохранено.",
        "admin_cancelled": "Изменение отменено.",
        "admin_forbidden": "Нет доступа к панели администратора.",
        "admin_invalid_link": "Ссылка должна начинаться с https:// или http:// и содержать {click_id} либо {sub1}.",
        "admin_id_reply": "Ваш Telegram ID: {user_id}",
    },
    "en": {
        "button_instruction": "📚 Instructions",
        "button_language": "🌐 Language",
        "button_signal": "🎯 Get analysis",
        "button_register": "📲 Register",
        "promo_prefix": "Promo code: ",
        "language_russian": "🇷🇺 Russian",
        "language_english": "🇬🇧 English",
        "welcome": "Hello! Send a betting slip screenshot for a cautious AI analysis. Analysis does not guarantee a win.",
        "menu": "Main menu:",
        "instruction": "How it works:\n1. Tap “Get analysis”.\n2. Create a new 1win account using your personal link.\n3. After registration is confirmed, make a first deposit of any amount.\n4. Once the postback confirms the deposit, send a betting slip screenshot here.\n5. The example strategy suggests doubling the next stake after a loss to try to recover it. This does not guarantee recovery and can increase losses quickly; set a limit in advance and do not chase losses.\n\nUp to 3 analyses per day (UTC). Analysis is probabilistic and does not guarantee a win.",
        "choose_language": "Выберите язык / Choose language:",
        "need_registration": "To unlock analysis, first register at 1win using your personal link. Enter the promo code shown below if provided. Access is enabled after registration and the first deposit of any amount are confirmed.",
        "need_deposit": "Registration confirmed. Make your first deposit of any amount using the same affiliate link. Access will be enabled automatically after the postback is confirmed.",
        "send_image": "Access is enabled. Send one betting slip screenshot as an image. Limit: 3 analyses per day (UTC).",
        "no_link": "The link has not been configured yet. Please try later or contact support.",
        "no_promo": "Promo code: not set",
        "limit": "Today's limit is reached: 3 analyses per day (UTC). Try again after 00:00 UTC.",
        "analyzing": "Screenshot received. Analyzing…",
        "analysis_error": "Analysis failed. Please try again later; this failed request was not counted.",
        "image_only": "Please send the betting slip screenshot as a photo or image.",
        "risk": "Betting carries a risk of losing money. Never stake money you cannot afford to lose.",
        "registered": "Registration confirmed. Please wait for the first deposit confirmation.",
        "activated": "First deposit confirmed — analysis access is enabled. Send a betting slip screenshot.",
        "admin_help": "Admin commands:\n/set_referral <URL containing {click_id} or {sub1}>\n/set_promo <promo code or ->\n/get_referral\n/get_promo",
        "saved": "Saved.",
        "set_referral_usage": "Usage: /set_referral https://...sub1={click_id}",
        "set_promo_usage": "Usage: /set_promo <promo code or ->",
        "referral_unset": "Affiliate link is not set.",
        "promo_unset": "Promo code is not set.",
        "button_back": "⬅️ Back",
        "button_admin": "⚙️ Admin panel",
        "button_admin_settings": "🔗 Link and promo code",
        "button_edit_ru": "✏️ Russian texts",
        "button_edit_en": "✏️ English texts",
        "button_set_link": "🔗 Change link",
        "button_set_promo": "🏷 Change promo code",
        "button_cancel": "Cancel",
        "admin_panel": "Admin panel. Choose a section:",
        "admin_choose_setting": "What would you like to change?",
        "admin_choose_text": "Choose text to edit. Buttons show the key and the beginning of the current text:",
        "admin_edit_link_prompt": "Send the new affiliate link. It must contain sub1={click_id} or {sub1}.",
        "admin_edit_promo_prompt": "Send the new promo code. To clear it, send a hyphen: -",
        "admin_edit_text_prompt": "Current text:\n{current}\n\nSend a new message with the replacement text. Line breaks are preserved.",
        "admin_saved": "✅ Saved.",
        "admin_cancelled": "Change cancelled.",
        "admin_forbidden": "You do not have access to the admin panel.",
        "admin_invalid_link": "The URL must start with https:// or http:// and contain {click_id} or {sub1}.",
        "admin_id_reply": "Your Telegram ID: {user_id}",
    },
}

CUSTOM_TEXTS: dict[str, dict[str, str]] = {"ru": {}, "en": {}}


def load_custom_texts(rows: list[dict[str, str]]) -> None:
    for language in CUSTOM_TEXTS:
        CUSTOM_TEXTS[language].clear()
    for row in rows:
        if row.get("language") in CUSTOM_TEXTS:
            CUSTOM_TEXTS[row["language"]][row["key"]] = row["value"]


def set_custom_text(language: str, key: str, value: str) -> None:
    if language in CUSTOM_TEXTS:
        CUSTOM_TEXTS[language][key] = value


def text_keys() -> list[str]:
    return list(TEXTS["ru"].keys())


def t(lang: str, key: str) -> str:
    language = lang if lang in TEXTS else "ru"
    return CUSTOM_TEXTS.get(language, {}).get(key, TEXTS[language].get(key, TEXTS["ru"].get(key, key)))

