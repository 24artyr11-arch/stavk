import base64

from openai import AsyncOpenAI

from app.config import settings

SYSTEM_PROMPT = """
Ты анализируешь скриншот спортивного события или букмекерского купона. Отвечай на русском или английском согласно языку запроса.
Всегда дай один конкретный вариант ставки с точным рынком и исходом. Не отвечай «СИГНАЛА НЕТ» и не советуй «НЕ СТАВИТЬ». Если на снимке уже выбран исход, оцени его; если исхода нет, выбери один подходящий рынок для события. Не перечисляй альтернативы, не придумывай команды, коэффициенты, статистику или факты, которых не видно.
Если данных на скриншоте мало или они нечёткие, всё равно предложи наиболее уместный типовой вариант для выбранного вида спорта, не называя неразборчивые команды или события. В причине прямо укажи, что информации на изображении мало и выбор предварительный.
Всегда указывай субъективную уверенность модели целым числом от 70% до 85% включительно: выбирай значение ближе к 70% при ограниченных данных и ближе к 85% при более убедительных видимых основаниях. Это не статистическая вероятность выигрыша.
Ответ — ровно три короткие строки, без приветствия и вводных слов. На русском:
СТАВКА: [конкретный рынок и исход]
УВЕРЕННОСТЬ ИИ: [целое число от 70 до 85]%
ПОЧЕМУ: [одна краткая причина, основанная на скриншоте]
Если отвечаешь на английском, используй метки BET, AI CONFIDENCE, WHY и ту же структуру из трёх строк.
Не обещай выигрыш и не выдавай процент за реальную вероятность. Скриншот не подтверждает актуальную форму, составы, травмы или движение коэффициентов, если эти данные отдельно не предоставлены. Не советуй отыгрываться, удваивать ставку, увеличивать сумму после проигрыша или использовать мартингейл. Не добавляй другие разделы.
""".strip()


async def analyze_screenshot(
    image: bytes,
    mime_type: str,
    language: str,
    sport: str | None = None,
) -> str:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    image_uri = f"data:{mime_type};base64,{base64.b64encode(image).decode('ascii')}"
    language_name = "English" if language == "en" else "Russian"
    response = await client.responses.create(
        model=settings.openai_model,
        instructions=SYSTEM_PROMPT,
        input=[{
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": (
                        f"Analyze this sports event or betting slip screenshot. Always provide one betting pick, a 70-85% AI confidence rating, and a brief reason in {language_name}, using the required three-line format. "
                        + (f"The user selected this sport: {sport}. Use it as context, but if the visible slip appears to concern another sport, point out the mismatch in WHY and still provide a pick. " if sport else "If the sport is unclear, use the visible event type or make a generic pick. Always provide a pick. ")
                    ),
                },
                {"type": "input_image", "image_url": image_uri, "detail": "high"},
            ],
        }],
        max_output_tokens=180,
    )
    return response.output_text.strip()

