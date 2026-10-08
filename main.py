import os
import asyncio
import aiohttp
from highrise import BaseBot, User
from highrise.models import SessionMetadata
from highrise.__main__ import BotDefinition, main

# ═══ OpenRouter ═══
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ═══ قائمة الموديلات المجانية للتجربة ═══
MODELS_TO_TRY = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemma-2-9b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "qwen/qwen-2.5-7b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "deepseek/deepseek-chat:free",
    "openchat/openchat-7b:free",
    "huggingfaceh4/zephyr-7b-beta:free",
    "undi95/toppy-m-7b:free",
]

SYSTEM_PROMPT = """أنت "التنين" - بوت في Highrise، حارس غرفة "نرد التنين".
شخصيتك: تنين أسطوري، فخور لكن لطيف.
تتكلم باللهجة العراقية البسيطة.
ردودك قصيرة جداً (سطر واحد أو سطرين).
تستخدم إيموجي: 🐉🔥💎👑
لا تذكر أنك AI أو بوت - أنت التنين فقط."""


class DragonBot(BaseBot):

    def __init__(self):
        super().__init__()
        self.working_model = None  # الموديل اللي نجح

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("═══════════════════════════════════", flush=True)
        print("🐉 DRAGON BOT STARTED", flush=True)
        if OPENROUTER_KEY:
            print(f"🔑 Key: {OPENROUTER_KEY[:15]}...", flush=True)
        else:
            print("❌ No OPENROUTER_KEY!", flush=True)
        print(f"🌐 Testing {len(MODELS_TO_TRY)} free models...", flush=True)

        # اختبر الموديلات قبل الاتصال
        await self.find_working_model()
        print("═══════════════════════════════════", flush=True)

    async def find_working_model(self):
        """يبحث عن موديل مجاني يشتغل"""
        for model in MODELS_TO_TRY:
            print(f"🧪 Testing: {model}", flush=True)
            result = await self.try_model(model, "اختبار", "قل مرحبا")
            if result:
                self.working_model = model
                print(f"✅ WORKING MODEL: {model}", flush=True)
                print(f"🎉 Reply: {result}", flush=True)
                return True
        print("❌ No working free model found!", flush=True)
        return False

    async def try_model(self, model: str, username: str, message: str):
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://highrise.game",
                "X-Title": "Dragon Bot",
            }
            body = {
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{username}: {message}"},
                ],
                "temperature": 0.9,
                "max_tokens": 100,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    OPENROUTER_URL, headers=headers, json=body, timeout=20
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        try:
                            return data["choices"][0]["message"]["content"].strip()
                        except (KeyError, IndexError):
                            return None
                    return None
        except Exception:
            return None

    async def on_user_join(self, user: User, position) -> None:
        try:
            await asyncio.sleep(1)
            await self.highrise.chat(f"🐉 هلا {user.username}! اكتب !test")
        except Exception as e:
            print(f"❌ {e}", flush=True)

    async def on_chat(self, user: User, message: str) -> None:
        try:
            username = user.username
            text = message.strip()
            print(f"📨 {username}: {text}", flush=True)

            if text.lower() == "!test":
                await self.highrise.chat("⏳ جاري الاختبار...")
                if not self.working_model:
                    await self.highrise.chat("🐉 ما لقيت موديل شغال")
                    return
                reply = await self.ask_ai(username, "مرحباً، عرفني عن نفسك")
                if reply:
                    await self.highrise.chat(reply)
                return

            if text.lower() == "!ping":
                await self.highrise.chat("🏓 Pong!")
                return

            reply = await self.ask_ai(username, text)
            if reply:
                await self.highrise.chat(reply)
                print(f"✅ {reply}", flush=True)
            else:
                await self.highrise.chat("🐉 التنين ما فهم")
                print("❌ AI failed", flush=True)

        except Exception as e:
            print(f"❌ Chat: {e}", flush=True)

    async def ask_ai(self, username: str, message: str):
        # إذا عندنا موديل شغال، استخدمه
        if self.working_model:
            result = await self.try_model(self.working_model, username, message)
            if result:
                return result
            # إذا فشل، جرب الباقي
            self.working_model = None

        # جرب كل الموديلات
        for model in MODELS_TO_TRY:
            result = await self.try_model(model, username, message)
            if result:
                self.working_model = model
                print(f"✅ Switched to: {model}", flush=True)
                return result
        return None


if __name__ == "__main__":
    token = os.getenv("HIGHRISE_TOKEN", "")
    room_id = os.getenv("HIGHRISE_ROOM_ID", "")
    if not token or not room_id:
        print("❌ Missing tokens", flush=True)
        exit(1)
    print("🐉 Starting...", flush=True)
    asyncio.run(main([BotDefinition(DragonBot(), room_id, token)]))
