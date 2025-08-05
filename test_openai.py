import os
from openai import OpenAI

# Проверяем, установлен ли API-ключ в переменных окружения
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("Ошибка: Переменная окружения OPENAI_API_KEY не установлена.")
else:
    print("Успех: Ключ OPENAI_API_KEY найден.")
    try:
        # Пытаемся создать клиент OpenAI
        client = OpenAI(api_key=api_key)
        print("Успех: Клиент OpenAI инициализирован.")

        # Пытаемся выполнить простой вызов API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Скажи привет пользователю."}]
        )
        print("Успех: Вызов API был успешным.")
        print("Ответ API:", response.choices[0].message.content)
    except Exception as e:
        print("Ошибка: Произошло исключение во время инициализации клиента или вызова API.")
        print(f"Полный текст ошибки: {e}")