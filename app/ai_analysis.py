import base64

from openai import AsyncOpenAI

from app.config import settings

SYSTEM_PROMPT = """
Ты анализируешь скриншот спортивного события или букмекерского купона. Отвечай на русском или английском согласно языку запроса.
Дай один краткий и конкретный вариант: укажи рынок и точный исход, опираясь только на читаемые данные изображения. Если на снимке уже выбран исход, оцени именно его. Не перечисляй альтернативы и не выдумывай рынок, команду, коэффициент, статистику или факты, которых не видно.
Если сигнал обоснован видимыми данными, ответь ровно тремя короткими строками, без приветствия и вводных слов. На русском:
СТАВКА: [конкретный рынок и исход]
УВЕРЕННОСТЬ ИИ: [целое число от 70 до 85]%
ПОЧЕМУ: [одна краткая причина, основанная на скриншоте]
Процент — субъективная оценка уверенности модели в выборе, а не статистическая вероятность выигрыша. Не подгоняй оценку под желаемое число: если по видимым данным нельзя обосновать уверенность хотя бы 70%, сигнала нет.
Если сигнала нет:
СИГНАЛА НЕТ: [чего не хватает]
СТАВКА: НЕ СТАВИТЬ
ПОЧЕМУ: [коротко объясни, почему по снимку нельзя выбрать исход]
Для английского используй метки BET, AI CONFIDENCE, WHY; если сигнала нет — NO SIGNAL, BET: DO NOT BET, WHY.
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
                        f"Analyze this sports event or betting slip screenshot. Reply in {language_name} using the required three-line concise format. "
                        + (f"The user selected this sport: {sport}. Use it as context, but if the visible slip appears to concern another sport, point out the mismatch. " if sport else "If the sport is unclear, do not guess. ")
                    ),
                },
                {"type": "input_image", "image_url": image_uri, "detail": "high"},
            ],
        }],
        max_output_tokens=180,
    )
    return response.output_text.strip()

