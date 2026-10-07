import os
import random
import asyncio
import aiohttp
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata
from highrise.__main__ import BotDefinition, main

# ═══════════════════════════════════════
# 🐉 إعدادات
# ═══════════════════════════════════════
ROOM_NAME = "نرد التنين"

# حدود الحركة العشوائية
ROOM_X_MIN = -6
ROOM_X_MAX = 6
ROOM_Z_MIN = -10
ROOM_Z_MAX = 10

# 🤖 Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

# شخصية التنين
SYSTEM_PROMPT = """أنت "التنين" - بوت حارس غرفة "نرد التنين" في Highrise.
شخصيتك: تنين أسطوري فخم، حارس كنوز، فخور قليلاً لكن لطيف.
تتكلم باللهجة العراقية العربية البسيطة، قريب من الشباب.
ردودك قصيرة جداً (سطر واحد أو سطرين كحد أقصى).
تستخدم إيموجي: 🐉🔥💎👑⭐
لا تذكر أنك AI أو بوت أو برنامج. أنت التنين فقط.
لا تكرر نفس العبارات.
كن مرن مع المواضيع - إذا سألك أحد عن يومه، جاوب باهتمام.
تذكر أن الغرفة اسمها "نرد التنين" وأنك حارسها."""

# ═══════════════════════════════════════
# 🐉 رسائل الترحيب
# ═══════════════════════════════════════
WELCOME_MESSAGES = [
    "🐉 زئير! من هذا الغريب؟ 👁️\nمرحباً {user}! أول مرة أشوفك 🌟",
    "🐲 أوه! وجه جديد!\nأهلاً بك {user} في عرين التنين 💎",
    "🔥 التنين شمّ رائحة جديدة!\nمنور {user}! شنو اسمك؟ 🌟",
    "🐉 عين التنين رصدتك {user}...\nمرحباً بك في مملكتي 👑",
]

# ═══════════════════════════════════════
# بيانات
# ═══════════════════════════════════════
JOKES = [
    "واحد دخل المطعم قال: عندكم دجاج؟ قال: لا. قال: ليش المطعم مفتوح؟ قال: نخبر الناس! 😂",
    "واحد راح للدكتور قال: كل ما أشرب شاي أحس بألم في عيني! قال: شيل الملعقة من الكوب! 😂",
]

RIDDLES = [
    {"q": "شي يمشي وما عنده رجلين؟", "a": "الماء"},
    {"q": "شي كل ما أخذت منه كبر؟", "a": "الحفرة"},
]

# ═══════════════════════════════════════
# ذاكرة
# ═══════════════════════════════════════
rps_games = {}
guess_games = {}
riddle_games = {}


def rand(arr):
    return random.choice(arr)


# ═══════════════════════════════════════
# 🐉 كلاس التنين
# ═══════════════════════════════════════
class DragonBot(BaseBot):

    def __init__(self):
        super().__init__()
        self.state = "IDLE"
        self.target_user = None
        self.user_positions = {}
        self.chat_history = {}
        self.last_known_position = None
        self.cooldown_until = 0
        self.behavior_task = None
        self.last_user_msg_time = {}

    # ═══════════════════════════════════════
    # التشغيل
    # ═══════════════════════════════════════
    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print(f"🐉 Dragon Bot Awakened in {ROOM_NAME}!")
        print(f"🤖 AI: {'مفعّل ✅' if GEMINI_API_KEY else 'معطّل ❌ (أضف GEMINI_API_KEY)'}")
        await asyncio.sleep(3)
        self.behavior_task = asyncio.create_task(self.behavior_loop())

    # ═══════════════════════════════════════
    # 🧠 حلقة السلوك
    # ═══════════════════════════════════════
    async def behavior_loop(self):
        while True:
            try:
                await asyncio.sleep(3)
                current_users = list(self.user_positions.keys())

                # ═══ IDLE: غرفة فارغة ═══
                if self.state == "IDLE":
                    if len(current_users) == 0:
                        x = random.uniform(ROOM_X_MIN, ROOM_X_MAX)
                        z = random.uniform(ROOM_Z_MIN, ROOM_Z_MAX)
                        try:
                            await self.highrise.walk_to(
                                Position(x=float(x), y=0.0, z=float(z), facing="FrontRight")
                            )
                            print(f"🚶 Random move → ({x:.1f}, {z:.1f})")
                        except Exception as e:
                            print(f"❌ Move: {e}")
                    else:
                        self.target_user = random.choice(current_users)
                        self.state = "APPROACHING"
                        print(f"🎯 New target: {self.target_user}")
                        await self.approach_target()

                # ═══ APPROACHING: يقترب من الهدف ═══
                elif self.state == "APPROACHING":
                    if self.target_user not in current_users:
                        self.state = "IDLE"
                        self.target_user = None
                        continue
                    await self.approach_target()
                    self.state = "FOLLOWING"
                    print(f"✅ Now following {self.target_user}")

                # ═══ FOLLOWING: يتبع الهدف ═══
                elif self.state == "FOLLOWING":
                    if self.target_user not in current_users:
                        print(f"👋 {self.target_user} left. Cooldown 60s...")
                        self.target_user = None
                        self.state = "COOLDOWN"
                        self.cooldown_until = asyncio.get_event_loop().time() + 60
                        continue
                    await self.follow_target()

                # ═══ COOLDOWN ═══
                elif self.state == "COOLDOWN":
                    if asyncio.get_event_loop().time() > self.cooldown_until:
                        print("⏰ Cooldown over")
                        self.state = "IDLE"
                        continue
                    x = random.uniform(ROOM_X_MIN, ROOM_X_MAX)
                    z = random.uniform(ROOM_Z_MIN, ROOM_Z_MAX)
                    try:
                        await self.highrise.walk_to(
                            Position(x=float(x), y=0.0, z=float(z), facing="FrontRight")
                        )
                        print(f"🚶 Cooldown walk → ({x:.1f}, {z:.1f})")
                    except Exception:
                        pass

            except Exception as e:
                print(f"❌ Behavior error: {e}")
                await asyncio.sleep(5)

    # ═══════════════════════════════════════
    # 🚶 الاقتراب
    # ═══════════════════════════════════════
    async def approach_target(self):
        pos = self.user_positions.get(self.target_user)
        if not pos or not hasattr(pos, 'x') or not hasattr(pos, 'z'):
            return
        try:
            target_x = pos.x + random.uniform(-1.5, 1.5)
            target_z = pos.z + random.uniform(-1.5, 1.5)
            await self.highrise.walk_to(
                Position(x=float(target_x), y=0.0, z=float(target_z), facing="FrontRight")
            )
            print(f"🚶 Approaching {self.target_user}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ Approach error: {e}")

    # ═══════════════════════════════════════
    # 👣 التتبع
    # ═══════════════════════════════════════
    async def follow_target(self):
        pos = self.user_positions.get(self.target_user)
        if not pos or not hasattr(pos, 'x') or not hasattr(pos, 'z'):
            return
        try:
            if self.last_known_position:
                dx = pos.x - self.last_known_position.x
                dz = pos.z - self.last_known_position.z
                distance = (dx * dx + dz * dz) ** 0.5
                if distance < 1.5:
                    return

            target_x = pos.x + random.uniform(-1.5, 1.5)
            target_z = pos.z + random.uniform(-1.5, 1.5)
            await self.highrise.walk_to(
                Position(x=float(target_x), y=0.0, z=float(target_z), facing="FrontRight")
            )
            print(f"👣 Following {self.target_user}")
        except Exception as e:
            print(f"❌ Follow error: {e}")

    # ═══════════════════════════════════════
    # 👤 عند دخول مستخدم
    # ═══════════════════════════════════════
    async def on_user_join(self, user: User, position) -> None:
        try:
            username = user.username
            print(f"👤 {username} joined")

            if position and hasattr(position, 'x'):
                self.user_positions[username] = position

            await asyncio.sleep(0.5)

            welcome = rand(WELCOME_MESSAGES).replace("{user}", username)
            await self.highrise.chat(welcome)

            if self.target_user is None and self.state == "IDLE":
                self.target_user = username
                self.state = "APPROACHING"
                print(f"🎯 Target from join: {username}")

        except Exception as e:
            print(f"❌ Join error: {e}")

    # ═══════════════════════════════════════
    # 🚪 عند خروج مستخدم
    # ═══════════════════════════════════════
    async def on_user_leave(self, user: User) -> None:
        try:
            username = user.username
            print(f"🚪 {username} left")
            if username in self.user_positions:
                del self.user_positions[username]
            if username in self.chat_history:
                del self.chat_history[username]
        except Exception as e:
            print(f"❌ Leave error: {e}")

    # ═══════════════════════════════════════
    # 📍 عند حركة مستخدم
    # ═══════════════════════════════════════
    async def on_user_move(self, user: User, position) -> None:
        try:
            if position and hasattr(position, 'x'):
                self.user_positions[user.username] = position
        except Exception:
            pass

    # ═══════════════════════════════════════
    # 💬 استقبال الرسائل
    # ═══════════════════════════════════════
    async def on_chat(self, user: User, message: str) -> None:
        try:
            username = user.username
            text = message.strip()
            lower = text.lower()

            print(f"📨 {username}: {text}")

            # !help
            if lower in ["!help", "!مساعدة"]:
                await self.highrise.chat(
                    "🐉 أوامر التنين:\n"
                    "🎲 !1 نرد التنين\n"
                    "🪙 !2 عملة الحظ\n"
                    "😂 !6 نكتة\n"
                    "🌹 !8 مدح\n"
                    "👑 !9 حكمة التنين"
                )
                return

            if lower in ["!1", "!نرد"]:
                n = random.randint(1, 6)
                faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
                await self.highrise.chat(f"🐉 {username} رمى النرد: {faces[n-1]} {n}")
                return

            if lower in ["!2", "!عملة"]:
                r = "👑 رأس" if random.random() < 0.5 else "💎 ذيل"
                await self.highrise.chat(f"🐲 {username}: {r}")
                return

            if lower in ["!6", "!نكتة"]:
                await self.highrise.chat(f"😂 {rand(JOKES)}")
                return

            if lower in ["!8", "!مدح"]:
                await self.highrise.chat(f"🌹 {username} إنت أسطورة! 🔥")
                return

            if lower in ["!9", "!حكمة"]:
                wisdoms = ["🐉 الحظ يعشق الجريء", "💎 الوقت أغلى من الذهب", "🔥 من يخاف لا يفوز"]
                await self.highrise.chat(rand(wisdoms))
                return

            # ═══════════════════════════════════════
            # 🤖 Gemini AI
            # ═══════════════════════════════════════
            if GEMINI_API_KEY:
                now = asyncio.get_event_loop().time()
                last = self.last_user_msg_time.get(username, 0)
                if now - last < 2:
                    return
                self.last_user_msg_time[username] = now

                print(f"🤖 Asking Gemini for {username}...")
                reply = await self.get_ai_response(username, text)
                if reply:
                    await self.highrise.chat(reply)
                    print(f"🤖 AI replied: {reply}")
                else:
                    await self.highrise.chat(f"🐉 {username} التنين ما فهم... جرب مرة ثانية")
            else:
                simple = rand([
                    f"🐉 {username}، التنين ما فهم قصدك",
                    f"🔥 {username}، جرب تكتب شي ثاني",
                    f"💎 {username}، التنين مشغول يحرس الكنوز",
                ])
                await self.highrise.chat(simple)

        except Exception as e:
            print(f"❌ Chat error: {e}")

    # ═══════════════════════════════════════
    # 🤖 استدعاء Gemini
    # ═══════════════════════════════════════
    async def get_ai_response(self, username: str, message: str) -> str:
        try:
            history = self.chat_history.get(username, [])

            # بناء المحتوى
            contents = []
            for h in history[-6:]:
                role = "user" if h["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": h["content"]}]
                })
            contents.append({
                "role": "user",
                "parts": [{"text": f"{username}: {message}"}]
            })

            body = {
                "contents": contents,
                "systemInstruction": {
                    "parts": [{"text": SYSTEM_PROMPT}]
                },
                "generationConfig": {
                    "temperature": 0.9,
                    "topP": 0.95,
                    "maxOutputTokens": 120,
                }
            }

            url = f"{GEMINI_URL}?key={GEMINI_API_KEY}"

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=body, timeout=20) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        try:
                            reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        except (KeyError, IndexError):
                            print(f"❌ Parsing error: {data}")
                            return None

                        if username not in self.chat_history:
                            self.chat_history[username] = []
                        self.chat_history[username].append({"role": "user", "content": message})
                        self.chat_history[username].append({"role": "assistant", "content": reply})
                        self.chat_history[username] = self.chat_history[username][-10:]
                        return reply
                    else:
                        err = await resp.text()
                        print(f"❌ Gemini error {resp.status}: {err}")
                        return None
        except Exception as e:
            print(f"❌ AI error: {e}")
            return None


# ═══════════════════════════════════════
# 🚀 التشغيل
# ═══════════════════════════════════════
if __name__ == "__main__":
    token = os.getenv("HIGHRISE_TOKEN", "")
    room_id = os.getenv("HIGHRISE_ROOM_ID", "")

    if not token or not room_id:
        print("❌ Missing HIGHRISE_TOKEN or HIGHRISE_ROOM_ID")
        exit(1)

    print("🐉 Dragon Bot Rising...")
    asyncio.run(main([BotDefinition(DragonBot(), room_id, token)]))
