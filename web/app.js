const tg = window.Telegram && window.Telegram.WebApp;
const MAX_FILE_SIZE = 10 * 1024 * 1024;

const COPY = {
  ru: {
    eyebrow: "СПОРТИВНАЯ АНАЛИТИКА", title: "AI анализ ставки", language_label: "Язык",
    quota_label: "Анализы сегодня", quota_loading: "Загрузка…", quota: "Осталось: {remaining} из {limit}",
    sport_title: "Выберите вид спорта", sport_help: "Укажите спорт, который указан в купоне.", sport_label: "Вид спорта", sport_select: "Выберите вид спорта",
    sport_football: "Футбол", sport_basketball: "Баскетбол", sport_hockey: "Хоккей", sport_tennis: "Теннис",
    sport_volleyball: "Волейбол", sport_table_tennis: "Настольный теннис", sport_boxing_mma: "Бокс / MMA", sport_esports: "Киберспорт", sport_other: "Другое",
    upload_title: "Добавьте скриншот", upload_help: "На изображении должны быть видны событие, исход и коэффициент.",
    choose_image: "Выбрать изображение", image_formats: "JPEG, PNG или WebP · до 10 МБ", remove_image: "Убрать",
    analyze_button: "Проанализировать купон", analyzing: "Анализируем скриншот…", choose_first: "Сначала выберите скриншот.",
    too_large: "Файл больше 10 МБ. Выберите изображение меньшего размера.", unsupported: "Поддерживаются только JPEG, PNG и WebP.",
    result_title: "Результат анализа", disclaimer: "Уверенность ИИ (70–85%) — субъективная оценка модели, не вероятность выигрыша. При нехватке данных сигнал будет предварительным. Анализ не учитывает актуальные составы и движение коэффициентов; ставки связаны с риском потери денег.",
    invalid_data: "Не удалось подтвердить Telegram. Закройте Mini App и откройте его снова из бота.",
    deposit_required: "Доступ пока не активирован. Сначала завершите регистрацию и внесите первый депозит, затем дождитесь подтверждения в боте.",
    daily_limit: "Лимит на сегодня исчерпан. Новые анализы будут доступны после 00:00 UTC.",
    generic_error: "Не удалось выполнить анализ. Попробуйте ещё раз.", language_error: "Не удалось сохранить язык.",
  },
  en: {
    eyebrow: "SPORTS ANALYSIS", title: "AI Bet Analysis", language_label: "Language",
    quota_label: "Analyses today", quota_loading: "Loading…", quota: "Remaining: {remaining} of {limit}",
    sport_title: "Choose a sport", sport_help: "Select the sport shown on the slip.", sport_label: "Sport", sport_select: "Choose a sport",
    sport_football: "Football", sport_basketball: "Basketball", sport_hockey: "Hockey", sport_tennis: "Tennis",
    sport_volleyball: "Volleyball", sport_table_tennis: "Table tennis", sport_boxing_mma: "Boxing / MMA", sport_esports: "Esports", sport_other: "Other",
    upload_title: "Add a screenshot", upload_help: "The event, selection, and odds should be visible.",
    choose_image: "Choose an image", image_formats: "JPEG, PNG, or WebP · up to 10 MB", remove_image: "Remove",
    analyze_button: "Analyze slip", analyzing: "Analyzing screenshot…", choose_first: "Choose a screenshot first.",
    too_large: "File is over 10 MB. Choose a smaller image.", unsupported: "Only JPEG, PNG, and WebP are supported.",
    result_title: "Analysis result", disclaimer: "AI confidence (70–85%) is a subjective model rating, not the probability of winning. With limited screenshot data, the pick is preliminary. The analysis excludes current lineups and odds movement; betting carries a risk of financial loss.",
    invalid_data: "Telegram could not be verified. Close the Mini App and reopen it from the bot.",
    deposit_required: "Access is not active yet. Complete registration and make your first deposit, then wait for confirmation in the bot.",
    daily_limit: "Today's limit is reached. Analyses reset after 00:00 UTC.",
    generic_error: "Analysis failed. Please try again.", language_error: "Could not save language.",
  },
};

const el = (id) => document.getElementById(id);
const input = el("image-input");
const uploadArea = el("upload-area");
const analyzeButton = el("analyze-button");
const languagePicker = el("language");
let language = "ru";
let selectedFile = null;
let remaining = 0;
let limit = 3;
let busy = false;

function text(key) { return COPY[language][key] || COPY.ru[key] || key; }

function translate() {
  document.documentElement.lang = language;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    if (key === "remove_image") node.textContent = text(key);
    else node.textContent = text(key);
  });
  languagePicker.value = language;
  updateQuota();
}

function updateQuota() {
  el("quota-copy").textContent = text("quota").replace("{remaining}", remaining).replace("{limit}", limit);
  const dots = el("quota-dots");
  dots.replaceChildren();
  for (let i = 0; i < limit; i += 1) {
    const dot = document.createElement("span");
    dot.className = `quota-dot${i >= remaining ? " used" : ""}`;
    dots.append(dot);
  }
  refreshButton();
}

function refreshButton() {
  analyzeButton.disabled = busy || !selectedFile || !el("sport").value || remaining <= 0;
  analyzeButton.querySelector(".button-spinner").classList.toggle("hidden", !busy);
  analyzeButton.querySelector("[data-i18n]").textContent = busy ? text("analyzing") : text("analyze_button");
}

function setStatus(message = "", isError = false) {
  const status = el("status");
  status.textContent = message;
  status.classList.toggle("error", isError);
}

function apiHeaders() {
  const initData = tg && tg.initData;
  return initData ? { Authorization: `tma ${initData}` } : {};
}

async function readError(response) {
  let data = {};
  try { data = await response.json(); } catch (_) { /* use the localized fallback */ }
  if (data.code === "invalid_telegram_data") return text("invalid_data");
  if (data.code === "deposit_required") return text("deposit_required");
  if (data.code === "daily_limit") return text("daily_limit");
  if (data.code === "image_too_large") return text("too_large");
  if (data.code === "unsupported_image") return text("unsupported");
  return text("generic_error");
}

function setFile(file) {
  if (!file) return;
  if (file.size > MAX_FILE_SIZE) { setStatus(text("too_large"), true); return; }
  if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) { setStatus(text("unsupported"), true); return; }
  selectedFile = file;
  el("preview-image").src = URL.createObjectURL(file);
  el("preview-name").textContent = file.name || text("choose_image");
  el("preview-size").textContent = `${(file.size / 1024 / 1024).toFixed(2)} MB`;
  el("preview").classList.remove("hidden");
  setStatus();
  refreshButton();
}

function clearFile() {
  const oldUrl = el("preview-image").src;
  if (oldUrl.startsWith("blob:")) URL.revokeObjectURL(oldUrl);
  selectedFile = null;
  input.value = "";
  el("preview").classList.add("hidden");
  el("preview-image").removeAttribute("src");
  refreshButton();
}

function showAccessNotice(message) {
  const notice = el("access-notice");
  notice.textContent = message;
  notice.classList.remove("hidden");
  el("analysis-card").classList.add("disabled");
}

async function initialize() {
  if (tg) {
    tg.ready();
    tg.expand();
    try { tg.setHeaderColor("#08090b"); tg.setBackgroundColor("#08090b"); } catch (_) { /* optional Telegram UI methods */ }
  }
  try {
    const response = await fetch("/api/me", { headers: apiHeaders() });
    if (!response.ok) {
      const error = await readError(response);
      showAccessNotice(error);
      setStatus(error, true);
      return;
    }
    const data = await response.json();
    language = data.language === "en" ? "en" : "ru";
    remaining = Number(data.remaining) || 0;
    limit = Number(data.limit) || 3;
    translate();
    if (!data.authorized) showAccessNotice(text("deposit_required"));
  } catch (_) {
    showAccessNotice(text("generic_error"));
  }
}

uploadArea.addEventListener("click", () => input.click());
input.addEventListener("change", (event) => setFile(event.target.files && event.target.files[0]));
el("remove-image").addEventListener("click", clearFile);
languagePicker.addEventListener("change", async () => {
  const previous = language;
  language = languagePicker.value;
  translate();
  try {
    const response = await fetch("/api/language", {
      method: "POST", headers: { ...apiHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({ language }),
    });
    if (!response.ok) throw new Error("language update failed");
    setStatus();
  } catch (_) {
    language = previous;
    translate();
    setStatus(text("language_error"), true);
  }
});

analyzeButton.addEventListener("click", async () => {
  if (!el("sport").value) { setStatus(text("sport_select"), true); return; }
  if (!selectedFile) { setStatus(text("choose_first"), true); return; }
  if (remaining <= 0 || busy) return;
  const form = new FormData();
  form.append("image", selectedFile, selectedFile.name || "screenshot");
  form.append("sport", el("sport").value);
  busy = true;
  setStatus();
  refreshButton();
  try {
    const response = await fetch("/api/analyze", { method: "POST", headers: apiHeaders(), body: form });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (data.code === "daily_limit") { remaining = 0; updateQuota(); }
      setStatus(await readError(new Response(JSON.stringify(data), { status: response.status })), true);
      return;
    }
    remaining = Number(data.remaining) || 0;
    updateQuota();
    el("result-text").textContent = data.result || text("generic_error");
    el("result-card").classList.remove("hidden");
    el("result-card").scrollIntoView({ behavior: "smooth", block: "start" });
    clearFile();
  } catch (_) {
    setStatus(text("generic_error"), true);
  } finally {
    busy = false;
    refreshButton();
  }
});

el("sport").addEventListener("change", refreshButton);

translate();
initialize();

