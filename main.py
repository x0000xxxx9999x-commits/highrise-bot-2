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
ردودك قصيرة جداً (سطر واحد).
تستخدم إيموجي: 🐉🔥💎👑
لا تذكر أنك AI أو بوت."""


class DragonBot(BaseBot):

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("═══════════════════════════════════")
        print("🐉 DRAGON BOT STARTED")
        print(f"🔑 Key: {GEMINI_API_KEY[:15]}..." if GEMINI_API_KEY else "❌ No API Key!")
        print(f"🌐 Model: {GEMINI_MODEL}")
        print("═══════════════════════════════════")

    async def on_user_join(self, user: User, position) -> None:
        print(f"👤 {user.username} joined")
        try:
            await asyncio.sleep(1)
            await self.highrise.chat(f"🐉 هلا {user.username}! اكتب !test للتجربة")
        except Exception as e:
            print(f"❌ Welcome error: {e}")

    async def on_chat(self, user: User, message: str) -> None:
        try:
            username = user.username
            text = message.strip()

            print(f"📨 {username}: {text}")

            # ═══ !test → يختبر AI ═══
            if text.lower() == "!test":
                print("🧪 Testing AI...")
                await self.highrise.chat("⏳ جاري الاختبار...")

                reply = await self.ask_ai(username, "مرحباً، عرفني عن نفسك")

                if reply:
                    await self.highrise.chat(reply)
                    print(f"✅ AI Works! Reply: {reply}")
                else:
                    await self.highrise.chat("❌ AI فشل - شوف السجلات")
                return

            # ═══ !ping → اختبار البوت ═══
            if text.lower() == "!ping":
                await self.highrise.chat("🏓 Pong!")
                return

            # ═══ أي رسالة ثانية → يختبر AI ═══
            print(f"🤖 Sending to AI: {text}")
            reply = await self.ask_ai(username, text)

            if reply:
                await self.highrise.chat(reply)
                print(f"✅ AI replied: {reply}")
            else:
                await self.highrise.chat("🐉 التنين ما فهم")
                print("❌ AI failed")

        except Exception as e:
            print(f"❌ Chat error: {e}")

    async def ask_ai(self, username: str, message: str):
        """إرسال رسالة لـ Gemini"""
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

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=body, timeout=20) as resp:
                    print(f"📡 Response status: {resp.status}")

                    if resp.status == 200:
                        data = await resp.json()
                        try:
                            reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                            return reply
                        except (KeyError, IndexError) as e:
                            print(f"❌ Parsing error: {e}")
                            print(f"📦 Data: {data}")
                            return None
                    else:
                        err = await resp.text()
                        print(f"❌ Gemini {resp.status}: {err[:300]}")
                        return None

        except asyncio.TimeoutError:
            print("❌ AI Timeout")
            return None
        except Exception as e:
            print(f"❌ AI Exception: {e}")
            return None


# ═══════════════════════════════════════
# 🚀 التشغيل
# ═══════════════════════════════════════
if __name__ == "__main__":
    token = os.getenv("HIGHRISE_TOKEN", "")
    room_id = os.getenv("HIGHRISE_ROOM_ID", "")

    if not token or not room_id:
        print("❌ Missing tokens")
        exit(1)

    print("🐉 Starting Dragon Bot...")
    asyncio.run(main([BotDefinition(DragonBot(), room_id, token)]))
