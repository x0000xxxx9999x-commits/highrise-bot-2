import os
import asyncio
import aiohttp
from highrise import BaseBot, User
from highrise.models import SessionMetadata
from highrise.__main__ import BotDefinition, main

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ═══ OpenAI-compatible endpoint (يعمل مع Gemini) ═══
GEMINI_OPENAI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

SYSTEM_PROMPT = """أنت "التنين" - بوت في Highrise، حارس غرفة "نرد التنين".
شخصيتك: تنين أسطوري، فخور لكن لطيف.
تتكلم باللهجة العراقية البسيطة.
ردودك قصيرة جداً (سطر واحد أو سطرين).
تستخدم إيموجي: 🐉🔥💎👑
لا تذكر أنك AI أو بوت - أنت التنين فقط."""

# الموديلات للتجربة
MODELS = [
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-flash-latest",
]


class DragonBot(BaseBot):

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("═══════════════════════════════════", flush=True)
        print("🐉 DRAGON BOT STARTED", flush=True)
        print(f"🔑 Key: {GEMINI_API_KEY[:15]}..." if GEMINI_API_KEY else "❌ No Key", flush=True)
        print("🌐 Using OpenAI-compatible endpoint", flush=True)
        print("═══════════════════════════════════", flush=True)

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
                reply = await self.ask_ai(username, "مرحباً، عرفني عن نفسك")
                if reply:
                    await self.highrise.chat(reply)
                    print(f"✅ Works: {reply}", flush=True)
                else:
                    print("❌ AI failed", flush=True)
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
        for model in MODELS:
            result = await self.try_openai(model, username, message)
            if result:
                print(f"✅ Model works: {model}", flush=True)
                return result
        return None

    async def try_openai(self, model: str, username: str, message: str):
        try:
            headers = {
                "Authorization": f"Bearer {GEMINI_API_KEY}",
                "Content-Type": "application/json",
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
                    GEMINI_OPENAI_URL, headers=headers, json=body, timeout=20
                ) as resp:
                    print(f"📡 {model}: {resp.status}", flush=True)
                    if resp.status == 200:
                        data = await resp.json()
                        try:
                            return data["choices"][0]["message"]["content"].strip()
                        except (KeyError, IndexError):
                            return None
                    else:
                        err = await resp.text()
                        print(f"❌ {model} {resp.status}: {err[:150]}", flush=True)
                        return None
        except asyncio.TimeoutError:
            print(f"❌ {model} timeout", flush=True)
            return None
        except Exception as e:
            print(f"❌ {model}: {e}", flush=True)
            return None


if __name__ == "__main__":
    token = os.getenv("HIGHRISE_TOKEN", "")
    room_id = os.getenv("HIGHRISE_ROOM_ID", "")
    if not token or not room_id:
        print("❌ Missing tokens", flush=True)
        exit(1)
    print("🐉 Starting...", flush=True)
    asyncio.run(main([BotDefinition(DragonBot(), room_id, token)]))
