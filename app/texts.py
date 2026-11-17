TEXTS = {
    "ru": {
        "button_instruction": "📚 Инструкция",
        "button_language": "🌐 Выбрать язык",
        "button_signal": "🎯 Получить сигнал",
        "button_open_app": "📲 Открыть анализ",
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
        "send_image": "Доступ открыт. Нажмите «Открыть анализ» и загрузите скриншот купона. Лимит — 3 анализа за сутки по UTC. Если кнопка приложения пока не настроена, отправьте изображение прямо сюда.",
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
        "button_text_edit": "✏️ Изменить текст",
        "button_text_reset": "↩️ Вернуть стандартный",
        "button_text_reset_yes": "Да, вернуть стандартный",
        "button_text_reset_no": "Нет, оставить как есть",
        "admin_panel": "Панель администратора. Выберите раздел:",
        "admin_choose_setting": "Что изменить?",
        "admin_choose_category": "Сначала выберите категорию текстов:",
        "admin_choose_text": "Выберите сообщение, чтобы посмотреть его целиком:",
        "admin_text_preview": "{label}\n\nТекущий текст:\n{current}",
        "admin_text_edit_prompt": "Отправьте новый вариант текста одним сообщением. Переносы строк сохраняются.",
        "admin_text_reset_confirm": "Вернуть для этого сообщения стандартный текст? Ваш текущий вариант будет удалён.",
        "admin_text_reset_done": "Стандартный текст восстановлен.",
        "text_group_messages": "💬 Сообщения пользователям",
        "text_group_buttons": "🔘 Кнопки и меню",
        "text_group_affiliate": "🔗 Регистрация и партнёрская ссылка",
        "text_group_admin": "⚙️ Тексты админ-панели",
        "admin_edit_link_prompt": "Отправьте базовую партнёрскую ссылку 1win. Бот сам добавит уникальный sub1 для каждого пользователя. Если ссылка уже содержит шаблон {click_id} или {sub1}, бот подставит ID вместо него.",
        "admin_edit_promo_prompt": "Отправьте новый промокод. Чтобы убрать промокод, отправьте дефис: -",
        "admin_edit_text_prompt": "Текущий текст:\n{current}\n\nОтправьте новое сообщение с текстом. Переносы строк сохраняются.",
        "admin_saved": "✅ Сохранено.",
        "admin_cancelled": "Изменение отменено.",
        "admin_forbidden": "Нет доступа к панели администратора.",
        "admin_invalid_link": "Ссылка должна начинаться с https:// или http://.",
        "admin_id_reply": "Ваш Telegram ID: {user_id}",
    },
    "en": {
        "button_instruction": "📚 Instructions",
        "button_language": "🌐 Language",
        "button_signal": "🎯 Get analysis",
        "button_open_app": "📲 Open analysis",
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
        "send_image": "Access is enabled. Tap “Open analysis” and upload a betting slip screenshot. Limit: 3 analyses per day (UTC). If the app button is not configured yet, send the image here.",
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
        "button_text_edit": "✏️ Edit text",
        "button_text_reset": "↩️ Restore default",
        "button_text_reset_yes": "Yes, restore default",
        "button_text_reset_no": "No, keep current text",
        "admin_panel": "Admin panel. Choose a section:",
        "admin_choose_setting": "What would you like to change?",
        "admin_choose_category": "First choose a text category:",
        "admin_choose_text": "Choose a message to preview it in full:",
        "admin_text_preview": "{label}\n\nCurrent text:\n{current}",
        "admin_text_edit_prompt": "Send the replacement text in one message. Line breaks are preserved.",
        "admin_text_reset_confirm": "Restore the default text for this message? Your custom version will be removed.",
        "admin_text_reset_done": "The default text has been restored.",
        "text_group_messages": "💬 User messages",
        "text_group_buttons": "🔘 Buttons and menus",
        "text_group_affiliate": "🔗 Registration and affiliate link",
        "text_group_admin": "⚙️ Admin panel text",
        "admin_edit_link_prompt": "Send the base 1win affiliate link. The bot will add a unique sub1 for each user. If the link already contains {click_id} or {sub1}, the bot will replace it with that user's ID.",
        "admin_edit_promo_prompt": "Send the new promo code. To clear it, send a hyphen: -",
        "admin_edit_text_prompt": "Current text:\n{current}\n\nSend a new message with the replacement text. Line breaks are preserved.",
        "admin_saved": "✅ Saved.",
        "admin_cancelled": "Change cancelled.",
        "admin_forbidden": "You do not have access to the admin panel.",
        "admin_invalid_link": "The URL must start with https:// or http://.",
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


def clear_custom_text(language: str, key: str) -> None:
    if language in CUSTOM_TEXTS:
        CUSTOM_TEXTS[language].pop(key, None)


def text_keys() -> list[str]:
    return list(TEXTS["ru"].keys())


TEXT_CATEGORIES = {
    "user_messages": [
        "welcome", "menu", "instruction", "need_registration", "need_deposit",
        "send_image", "limit", "analyzing", "analysis_error", "image_only", "risk",
        "registered", "activated", "choose_language",
    ],
    "buttons": [
        "button_instruction", "button_language", "button_signal", "button_open_app", "button_register",
        "language_russian", "language_english", "button_back", "button_cancel",
        "button_admin", "button_admin_settings", "button_edit_ru", "button_edit_en",
        "button_set_link", "button_set_promo", "button_text_edit", "button_text_reset",
    ],
    "affiliate": [
        "promo_prefix", "no_promo", "no_link", "referral_unset", "promo_unset",
        "set_referral_usage", "set_promo_usage",
        "admin_edit_link_prompt", "admin_edit_promo_prompt", "admin_invalid_link",
    ],
}

TEXT_LABELS = {
    "ru": {
        "welcome": "Приветствие", "menu": "Заголовок главного меню", "instruction": "Инструкция",
        "choose_language": "Приглашение выбрать язык", "need_registration": "Текст перед регистрацией",
        "need_deposit": "Текст после регистрации, до депозита", "send_image": "Приглашение отправить скриншот",
        "no_link": "Сообщение, если ссылка не задана", "limit": "Лимит анализов исчерпан",
        "analyzing": "Сообщение во время анализа", "analysis_error": "Ошибка анализа",
        "image_only": "Подсказка о формате изображения", "risk": "Предупреждение о риске",
        "registered": "Подтверждение регистрации", "activated": "Подтверждение депозита",
        "button_instruction": "Кнопка инструкции", "button_language": "Кнопка выбора языка",
        "button_signal": "Кнопка запроса сигнала", "button_open_app": "Кнопка открытия Mini App",
        "button_register": "Кнопка регистрации",
        "language_russian": "Язык: русский", "language_english": "Язык: английский",
        "button_back": "Кнопка назад", "button_cancel": "Кнопка отмены",
        "button_admin": "Кнопка админ-панели", "button_admin_settings": "Кнопка настроек партнёрки",
        "button_edit_ru": "Кнопка русских текстов", "button_edit_en": "Кнопка английских текстов",
        "button_set_link": "Кнопка изменения ссылки", "button_set_promo": "Кнопка изменения промокода",
        "button_text_edit": "Кнопка изменения текста", "button_text_reset": "Кнопка возврата стандартного текста",
        "button_text_reset_yes": "Подтверждение сброса текста", "button_text_reset_no": "Отмена сброса текста",
        "promo_prefix": "Подпись перед промокодом", "no_promo": "Текст без промокода",
        "no_link": "Сообщение, если ссылка не задана", "referral_unset": "Ответ админа: ссылка не задана",
        "promo_unset": "Ответ админа: промокод не задан", "set_referral_usage": "Подсказка команды смены ссылки",
        "set_promo_usage": "Подсказка команды смены промокода", "admin_edit_link_prompt": "Запрос новой ссылки",
        "admin_edit_promo_prompt": "Запрос нового промокода", "admin_invalid_link": "Ошибка формата ссылки",
    },
    "en": {
        "welcome": "Welcome message", "menu": "Main menu heading", "instruction": "Instructions",
        "choose_language": "Language selection prompt", "need_registration": "Before registration",
        "need_deposit": "After registration, before deposit", "send_image": "Request for a screenshot",
        "no_link": "Message when no link is set", "limit": "Daily analysis limit reached",
        "analyzing": "Analysis in progress", "analysis_error": "Analysis error",
        "image_only": "Image format hint", "risk": "Risk warning", "registered": "Registration confirmation",
        "activated": "Deposit confirmation", "button_instruction": "Instructions button",
        "button_language": "Language button", "button_signal": "Request analysis button",
        "button_open_app": "Open Mini App button",
        "button_register": "Registration button", "language_russian": "Russian language option",
        "language_english": "English language option", "button_back": "Back button",
        "button_cancel": "Cancel button", "button_admin": "Admin panel button",
        "button_admin_settings": "Affiliate settings button", "button_edit_ru": "Russian texts button",
        "button_edit_en": "English texts button", "button_set_link": "Change link button",
        "button_set_promo": "Change promo button", "button_text_edit": "Edit text button",
        "button_text_reset": "Restore default text button", "promo_prefix": "Promo code label",
        "button_text_reset_yes": "Confirm restore text", "button_text_reset_no": "Cancel text restore",
        "no_promo": "Message when no promo is set", "referral_unset": "Admin: link not set",
        "promo_unset": "Admin: promo not set", "set_referral_usage": "Set link command hint",
        "set_promo_usage": "Set promo command hint", "admin_edit_link_prompt": "New link prompt",
        "admin_edit_promo_prompt": "New promo prompt", "admin_invalid_link": "Invalid link format message",
    },
}


def text_categories(lang: str) -> list[tuple[str, str]]:
    language = lang if lang in TEXTS else "ru"
    return [(key, t(language, f"text_group_{key}")) for key in (*TEXT_CATEGORIES.keys(), "admin")]


def category_text_keys(category: str) -> list[str]:
    groups = {key: list(values) for key, values in TEXT_CATEGORIES.items()}
    groups["admin"] = [key for key in text_keys() if not any(key in values for values in groups.values())]
    return [key for key in groups.get(category, []) if key in TEXTS["ru"]]


def text_label(lang: str, key: str) -> str:
    language = lang if lang in TEXT_LABELS else "ru"
    return TEXT_LABELS[language].get(key, key.replace("_", " ").capitalize())


def t(lang: str, key: str) -> str:
    language = lang if lang in TEXTS else "ru"
    return CUSTOM_TEXTS.get(language, {}).get(key, TEXTS[language].get(key, TEXTS["ru"].get(key, key)))

