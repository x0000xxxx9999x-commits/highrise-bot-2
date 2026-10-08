import os
import asyncio
import aiohttp
from highrise import BaseBot, User
from highrise.models import SessionMetadata
from highrise.__main__ import BotDefinition, main

# ═══════════════════════════════════════
# 🤖 Gemini AI
# ═══════════════════════════════════════
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
LIST_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"

SYSTEM_PROMPT = """أنت "التنين" - بوت في Highrise، حارس غرفة "نرد التنين".
شخصيتك: تنين أسطوري، فخور لكن لطيف.
تتكلم باللهجة العراقية البسيطة.
ردودك قصيرة جداً (سطر واحد أو سطرين).
تستخدم إيموجي: 🐉🔥💎👑
لا تذكر أنك AI أو بوت - أنت التنين فقط."""


class DragonBot(BaseBot):

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("═══════════════════════════════════", flush=True)
        print("🐉 DRAGON BOT STARTED", flush=True)
        if GEMINI_API_KEY:
            print(f"🔑 Key: {GEMINI_API_KEY[:15]}...", flush=True)
        else:
            print("❌ No GEMINI_API_KEY!", flush=True)

        # فحص الموديلات المتاحة
        await self.check_available_models()
        print("═══════════════════════════════════", flush=True)

    async def check_available_models(self):
        """فحص الموديلات المتاحة من Google"""
        try:
            url = f"{LIST_MODELS_URL}?key={GEMINI_API_KEY}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = data.get("models", [])
                        print(f"✅ Found {len(models)} models:", flush=True)
                        for m in models:
                            name = m.get("name", "").replace("models/", "")
                            methods = m.get("supportedGenerationMethods", [])
                            if "generateContent" in methods and "flash" in name:
                                print(f"   🎯 {name}", flush=True)
                    else:
                        print(f"❌ List models failed: {resp.status}", flush=True)
        except Exception as e:
            print(f"❌ Check models error: {e}", flush=True)

    async def on_user_join(self, user: User, position) -> None:
        print(f"👤 {user.username} joined", flush=True)
        try:
            await asyncio.sleep(1)
            await self.highrise.chat(f"🐉 هلا {user.username}! اكتب !test للتجربة")
        except Exception as e:
            print(f"❌ Welcome error: {e}", flush=True)

    async def on_chat(self, user: User, message: str) -> None:
        try:
            username = user.username
            text = message.strip()

            print(f"📨 {username}: {text}", flush=True)

            # ═══ !test → اختبار AI ═══
            if text.lower() == "!test":
                print("🧪 Testing AI...", flush=True)
                await self.highrise.chat("⏳ جاري الاختبار...")

                if not GEMINI_API_KEY:
                    await self.highrise.chat("🔴 GEMINI_API_KEY مفقود!")
                    return

                reply = await self.ask_ai(username, "مرحباً، عرفني عن نفسك")

                if reply:
                    await self.highrise.chat(reply)
                    print(f"✅ AI Works! Reply: {reply}", flush=True)
                else:
                    print("❌ AI failed", flush=True)
                return

            # ═══ !ping ═══
            if text.lower() == "!ping":
                await self.highrise.chat("🏓 Pong!")
                return

            # ═══ أي رسالة → AI ═══
            reply = await self.ask_ai(username, text)

            if reply:
                await self.highrise.chat(reply)
                print(f"✅ AI replied: {reply}", flush=True)
            else:
                await self.highrise.chat("🐉 التنين ما فهم، جرب مرة ثانية")
                print("❌ AI failed", flush=True)

        except Exception as e:
            print(f"❌ Chat error: {e}", flush=True)

    async def ask_ai(self, username: str, message: str):
        """مع إعادة المحاولة على موديلات مختلفة"""
        # قائمة الموديلات للتجربة
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-2.0-flash-exp",
            "gemini-flash-latest",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
        ]

        # للمرة الأولى، نستخدم الموديل الافتراضي
        # إذا فشل، نجرب الباقي
        for model in models_to_try:
            result = await self.try_model(model, username, message)
            if result:
                if model != GEMINI_MODEL:
                    print(f"✅ Worked with fallback model: {model}", flush=True)
                return result

        return None

    async def try_model(self, model: str, username: str, message: str):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

            body = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": f"{username}: {message}"}]
                    }
                ],
                "systemInstruction": {
                    "parts": [{"text": SYSTEM_PROMPT}]
                },
                "generationConfig": {
                    "temperature": 0.9,
                    "maxOutputTokens": 100,
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=body, timeout=20) as resp:
                    print(f"📡 {model}: {resp.status}", flush=True)

                    if resp.status == 200:
                        data = await resp.json()
                        try:
                            reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                            return reply
                        except (KeyError, IndexError) as e:
                            print(f"❌ Parse error on {model}: {e}", flush=True)
                            return None
                    elif resp.status == 404:
                        # الموديل غير موجود، جرب غيره
                        return None
                    else:
                        err = await resp.text()
                        print(f"❌ {model} {resp.status}: {err[:200]}", flush=True)
                        return None

        except asyncio.TimeoutError:
            print(f"❌ Timeout: {model}", flush=True)
            return None
        except Exception as e:
            print(f"❌ {model} error: {e}", flush=True)
            return None


# ═══════════════════════════════════════
# 🚀 التشغيل
# ═══════════════════════════════════════
if __name__ == "__main__":
    token = os.getenv("HIGHRISE_TOKEN", "")
    room_id = os.getenv("HIGHRISE_ROOM_ID", "")

    if not token or not room_id:
        print("❌ Missing tokens", flush=True)
        exit(1)

    print("🐉 Starting Dragon Bot...", flush=True)
    asyncio.run(main([BotDefinition(DragonBot(), room_id, token)]))
