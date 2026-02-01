import os
import requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Bot

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- GENERATE EXERCISE TEXT VIA FREE LLM ----------
def generate_exercise_text():
    prompt = (
        "Ты персональный тренер. Сгенерируй одно упражнение для домашней тренировки с названием и короткой инструкцией, "
        "чтобы пользователь понял, как его делать, максимум 200 символов."
    )
    API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}

    try:
        r = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt, "parameters": {"max_new_tokens": 100}},
            timeout=60
        )
        resp = r.json()
        if isinstance(resp, list) and "generated_text" in resp[0]:
            return resp[0]["generated_text"]
        elif isinstance(resp, dict) and "generated_text" in resp:
            return resp["generated_text"]
        else:
            return "Приседания: Встаньте прямо, ноги на ширине плеч. Сгибайте колени и поднимайтесь обратно."
    except Exception as e:
        print("Ошибка генерации:", e)
        return "Приседания: Встаньте прямо, ноги на ширине плеч. Сгибайте колени и поднимайтесь обратно."

# ---------- GENERATE GIF VIA SIMPLE MVP ----------
def generate_exercise_gif(text, frames=5):
    images = []
    for i in range(frames):
        img = Image.new("RGB", (512, 512), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        phase = f"Фаза {i+1}"
        draw.text((20, 20), f"{text}\n{phase}", fill="white", font=font)
        images.append(img)

    gif_path = os.path.join(OUTPUT_DIR, "exercise.gif")
    images[0].save(gif_path, save_all=True, append_images=images[1:], duration=500, loop=0)
    return gif_path

# ---------- SEND TO TELEGRAM ----------
def send_exercise_to_telegram():
    TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
    TG_CHAT_ID = os.getenv("TG_CHAT_ID")  # ID чата для рассылки

    bot = Bot(TG_BOT_TOKEN)

    text = generate_exercise_text()
    gif_path = generate_exercise_gif(text)

    # Отправляем текст
    bot.send_message(chat_id=TG_CHAT_ID, text=text)

    # Отправляем гифку
    with open(gif_path, "rb") as f:
        bot.send_animation(chat_id=TG_CHAT_ID, animation=f)

    print("Упражнение успешно отправлено!")

# ---------- MAIN ----------
if __name__ == "__main__":
    send_exercise_to_telegram()
