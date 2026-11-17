import base64

from openai import AsyncOpenAI

from app.config import settings

SYSTEM_PROMPT = """
Ты анализируешь изображение букмекерского купона и отвечаешь на русском или английском языке, в зависимости от указанного языка.
Сначала проверь, читается ли купон: событие, рынок, выбранный исход и коэффициент. Не додумывай отсутствующие данные.
Объясни, что изображение само по себе не подтверждает текущую форму команд, составы, травмы или движение коэффициентов. Не утверждай, что проверил актуальную статистику, если она не передана.
Дай осторожную оценку видимого выбора с краткими аргументами и ключевыми неопределённостями. Если данных недостаточно, скажи это прямо и не выдавай категоричный прогноз.
Не обещай выигрыш или доходность. Не советуй отыгрываться, увеличивать сумму после проигрыша, удваивать ставку или использовать мартингейл.
Заверши коротким напоминанием, что ставки несут риск потери денег и решение остаётся за пользователем.
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
                        f"Analyze this betting slip screenshot. Reply in {language_name}. "
                        + (f"The user selected this sport: {sport}. Use it as context, but if the visible slip appears to concern another sport, point out the mismatch. " if sport else "If the sport is unclear, do not guess. ")
                    ),
                },
                {"type": "input_image", "image_url": image_uri, "detail": "high"},
            ],
        }],
        max_output_tokens=700,
    )
    return response.output_text.strip()

