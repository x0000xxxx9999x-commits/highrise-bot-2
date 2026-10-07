import os
import asyncio
import aiohttp
from highrise import BaseBot, User
from highrise.models import SessionMetadata
from highrise.__main__ import BotDefinition, main

# ═══════════════════════════════════════
# 🤖 Gemini API
# ═══════════════════════════════════════
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

SYSTEM_PROMPT = """أنت "التنين" - بوت في Highrise.
شخصيتك: تنين أسطوري، تتكلم باللهجة العراقية البسيطة.
ردودك قصيرة جداً (سطر واحد أو سطرين).
تستخدم إيموجي: 🐉🔥💎👑
لا تذكر أنك AI أو بوت."""


class DragonBot(BaseBot):

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("═══════════════════════════════════", flush=True)
        print("🐉 DRAGON BOT STARTED", flush=True)
        if GEMINI_API_KEY:
            print(f"🔑 Key: {GEMINI_API_KEY[:20]}...", flush=True)
            print(f"🔑 Key Length: {len(GEMINI_API_KEY)}", flush=True)
        else:
            print("❌ No API Key!", flush=True)
        print(f"🌐 Model: {GEMINI_MODEL}", flush=True)
        print("═══════════════════════════════════", flush=True)

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

            # ═══ !test → يختبر AI ═══
            if text.lower() == "!test":
                print("🧪 Testing AI...", flush=True)
                await self.highrise.chat("⏳ جاري الاختبار...")

                # ═══ اختبار 1: هل المفتاح موجود؟ ═══
                if not GEMINI_API_KEY:
                    await self.highrise.chat("🔴 GEMINI_API_KEY مفقود في Railway!")
                    return

                # ═══ اختبار 2: هل المفتاح صالح؟ ═══
                await self.highrise.chat(f"🔑 طول المفتاح: {len(GEMINI_API_KEY)}")
                await self.highrise.chat(f"🔑 يبدأ بـ: {GEMINI_API_KEY[:10]}...")

                # ═══ اختبار 3: إرسال للـ AI ═══
                reply = await self.ask_ai(username, "مرحباً، عرفني عن نفسك")

                if reply:
                    await self.highrise.chat(reply)
                    print(f"✅ AI Works! Reply: {reply}", flush=True)
                else:
                    print("❌ AI failed - see errors above", flush=True)
                return

            # ═══ !ping → اختبار البوت ═══
            if text.lower() == "!ping":
                await self.highrise.chat("🏓 Pong!")
                return

            # ═══ أي رسالة ثانية → AI ═══
            print(f"🤖 Sending to AI: {text}", flush=True)
            reply = await self.ask_ai(username, text)

            if reply:
                await self.highrise.chat(reply)
                print(f"✅ AI replied: {reply}", flush=True)
            else:
                await self.highrise.chat("🐉 التنين ما فهم")
                print("❌ AI failed", flush=True)

        except Exception as e:
            print(f"❌ Chat error: {e}", flush=True)

    async def ask_ai(self, username: str, message: str):
        """إرسال رسالة لـ Gemini مع تشخيص كامل"""
        try:
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

            url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"

            print(f"📡 Sending to: {GEMINI_MODEL}", flush=True)
            print(f"📡 URL: {url[:80]}...", flush=True)

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=body, timeout=20) as resp:
                    print(f"📡 Response status: {resp.status}", flush=True)

                    if resp.status == 200:
                        data = await resp.json()
                        try:
                            reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                            return reply
                        except (KeyError, IndexError) as e:
                            print(f"❌ Parsing error: {e}", flush=True)
                            print(f"📦 Data: {data}", flush=True)
                            await self.highrise.chat(f"🔴 تحليل الرد فشل")
                            return None
                    else:
                        err = await resp.text()
                        print(f"❌ Gemini {resp.status}: {err[:500]}", flush=True)
                        # إرسال الخطأ للغرفة
                        try:
                            await self.highrise.chat(f"🔴 Gemini Error: {resp.status}")
                            # استخراج رسالة الخطأ الأساسية
                            short_err = err[:150].replace("\n", " ")
                            await self.highrise.chat(f"📋 {short_err}")
                        except Exception:
                            pass
                        return None

        except asyncio.TimeoutError:
            print("❌ AI Timeout", flush=True)
            await self.highrise.chat("🔴 AI Timeout")
            return None
        except Exception as e:
            print(f"❌ AI Exception: {e}", flush=True)
            await self.highrise.chat(f"🔴 {str(e)[:150]}")
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
