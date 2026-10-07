import os
import random
import asyncio
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata
from highrise.__main__ import BotDefinition, main

# ═══════════════════════════════════════
# 🐉 هوية التنين
# ═══════════════════════════════════════
ROOM_NAME = "نرد التنين"
DRAGON = "🐉"

# إعدادات الموقع - البوت يبتعد عن الباب
MOVE_X = 8
MOVE_Z = 8
MOVE_FACING = "FrontRight"

# ═══════════════════════════════════════
# 🎲 البيانات
# ═══════════════════════════════════════
WELCOME_MESSAGES = [
    "🐉 استيقظ التنين! مرحباً {user} في نرد التنين 🎲\n🔥 اقترب من الكنز! 💎",
    "🐲 زئير التنين! {user} وصل! 👑\n🎲 تفضل بالمقامرة",
    "🔥 من الأنقاض يخرج التنين! {user} نورت! 🐉\n💎 الكنوز في انتظارك",
    "🐉 عين التنين تراقبك {user}... 👁️\n🎲 اقترب إن كنت تجرؤ!",
    "👑 {user} دخل مملكة التنين! 🐲\n💎 الحظ معك اليوم"
]

JOKES = [
    "واحد دخل المطعم قال: عندكم دجاج؟ قال: لا. قال: ليش المطعم مفتوح؟ قال: نخبر الناس! 😂",
    "واحد راح للدكتور قال: كل ما أشرب شاي أحس بألم في عيني! قال: شيل الملعقة من الكوب! 😂",
    "سألوا واحد: ليش تمشي ورا البنت؟ قال: من زود الأدب! 😂",
    "واحد قال لصاحبه: أمس حلمت إني شربت بحر! قال: شلون؟ قال: بسرعة! 😂",
]

RIDDLES = [
    {"q": "شي يمشي وما عنده رجلين؟", "a": "الماء"},
    {"q": "شي كل ما أخذت منه كبر؟", "a": "الحفرة"},
    {"q": "عنده أسنان وما يعض؟", "a": "المشط"},
    {"q": "يدخل الماء ولا يبتل؟", "a": "الضوء"},
    {"q": "كلما زاد نقص؟", "a": "العمر"},
]

CHALLENGES = [
    "🐉 ازأر كالتنين أمام الغرفة!",
    "🔥 اكتب اسمك مع إيموجي النار",
    "💎 قل شيئاً ثميناً لأول شخص يدخل",
    "👑 تحدى التنين في التخمين!",
    "🐲 قلد صوت التنين في الدردشة",
]

COMPLIMENTS = [
    "🐉 إنت مقاتل حقيقي! 🔥",
    "💎 إنت كنز نادر في مملكة التنين! 👑",
    "🔥 أنت أسطورة! 🐲",
    "👑 التنين معجب بشجاعتك!",
    "🐲 نورت عرين التنين! 💎",
]

DRAGON_WISDOM = [
    "🐉 حكمة التنين: الحظ يعشق الجريء",
    "🔥 التنين يقول: من يخاف لا يفوز",
    "💎 كنز التنين: الوقت أغلى من الذهب",
    "👑 التنين يهدر: القوة بلا عقل هلاك",
    "🐲 من عرين التنين: الوفاء لا يُشترى",
]

GREETINGS_RESPONSES = [
    "🐉 زئير! من يجرؤ على التحدي؟",
    "🔥 هلا بالبطل! اقترب",
    "💎 نورت المملكة!",
    "👑 أهلاً بك في عرين التنين",
    "🐲 مرحباً بك، تفضل بجولة في الكنوز",
]

# ═══════════════════════════════════════
# ذاكرة الألعاب
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

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print(f"🐉 Dragon Bot Awakened in {ROOM_NAME}!")
        await asyncio.sleep(3)
        await self.move_away()

    async def move_away(self):
        try:
            position = Position(
                x=float(MOVE_X),
                y=0.0,
                z=float(MOVE_Z),
                facing=MOVE_FACING
            )
            await self.highrise.walk_to(position)
            print(f"✅ Dragon moved to ({MOVE_X}, {MOVE_Z})")
        except Exception as e:
            print(f"❌ Move error: {e}")

    async def on_user_join(self, user: User, position) -> None:
        print(f"👤 {user.username} entered the dragon's lair")
        try:
            await asyncio.sleep(0.8)
            welcome = rand(WELCOME_MESSAGES).replace("{user}", user.username)
            await self.highrise.chat(welcome)
            await asyncio.sleep(2.5)
            await self.highrise.chat("📜 اكتب !help لعرض أوامر التنين 🐉")
        except Exception as e:
            print(f"❌ Welcome error: {e}")

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
                    "✊ !3 حجر ورقة مقص\n"
                    "🎯 !4 خمن الكنز\n"
                    "🧩 !5 لغز التنين\n"
                    "😂 !6 نكتة\n"
                    "😈 !7 تحدي\n"
                    "🌹 !8 مدح\n"
                    "👑 !9 حكمة التنين"
                )
                return

            # !1 نرد التنين
            if lower in ["!1", "!نرد"]:
                n = random.randint(1, 6)
                faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
                comments = ["🔥 التنين راضٍ!", "💎 حظ سعيد!", "🐉 النرد ساخن!", "👑 رمية ملكية!"]
                await self.highrise.chat(f"🐉 {username} رمى نرد التنين: {faces[n-1]} {n}\n{rand(comments)}")
                return

            # !2 عملة
            if lower in ["!2", "!عملة"]:
                r = "👑 رأس التنين" if random.random() < 0.5 else "💎 ذيل التنين"
                await self.highrise.chat(f"🐲 {username} رما عملة التنين: {r}")
                return

            # !3 حجر ورقة مقص
            if lower in ["!3", "!حجر"]:
                rps_games[username] = True
                await self.highrise.chat(f"✊ {username} اختر:\n1 = حجر 🪨\n2 = ورقة 📄\n3 = مقص ✂️")
                return

            if username in rps_games and lower in ["1", "2", "3"]:
                choices = {"1": "حجر 🪨", "2": "ورقة 📄", "3": "مقص ✂️"}
                bot_choice = str(random.randint(1, 3))
                if lower == bot_choice:
                    result = "🤝 تعادل!"
                elif (lower == "1" and bot_choice == "3") or \
                     (lower == "2" and bot_choice == "1") or \
                     (lower == "3" and bot_choice == "2"):
                    result = "🎉 فزت على التنين! 🔥"
                else:
                    result = "😈 التنين فاز! 🐉"
                await self.highrise.chat(f"أنت: {choices[lower]} | التنين: {choices[bot_choice]}\n{result}")
                del rps_games[username]
                return

            # !4 خمن الكنز
            if lower in ["!4", "!خمن"]:
                target = random.randint(1, 50)
                guess_games[username] = {"target": target, "tries": 0}
                await self.highrise.chat(f"🐉 {username} خمن رقم بين 1 و 50!\n💎 كنز التنين مخبأ!")
                return

            if username in guess_games and lower.isdigit():
                guess = int(lower)
                game = guess_games[username]
                game["tries"] += 1
                if guess == game["target"]:
                    await self.highrise.chat(f"🎉 {username} لقى الكنز! 💎\nالرقم {game['target']} في {game['tries']} محاولات!")
                    del guess_games[username]
                elif guess < game["target"]:
                    await self.highrise.chat(f"⬆️ الكنز أعلى من {guess}")
                else:
                    await self.highrise.chat(f"⬇️ الكنز أقل من {guess}")
                return

            # !5 لغز
            if lower in ["!5", "!لغز"]:
                r = rand(RIDDLES)
                riddle_games[username] = r["a"]
                await self.highrise.chat(f"🐲 لغز التنين:\n🧩 {r['q']}")
                return

            if username in riddle_games and not lower.startswith("!"):
                answer = riddle_games[username]
                if text == answer:
                    await self.highrise.chat(f"🎉 {username} ذكي كالتنين! الجواب {answer}")
                else:
                    await self.highrise.chat(f"❌ خطأ! الجواب {answer}")
                del riddle_games[username]
                return

            # !6 نكتة
            if lower in ["!6", "!نكتة"]:
                await self.highrise.chat(f"😂 التنين يضحك:\n{rand(JOKES)}")
                return

            # !7 تحدي
            if lower in ["!7", "!تحدي"]:
                await self.highrise.chat(f"🐉 التنين يتحدى {username}:\n{rand(CHALLENGES)}")
                return

            # !8 مدح
            if lower in ["!8", "!مدح"]:
                await self.highrise.chat(rand(COMPLIMENTS))
                return

            # !9 حكمة
            if lower in ["!9", "!حكمة"]:
                await self.highrise.chat(rand(DRAGON_WISDOM))
                return

            # ردود تلقائية
            greetings = ["هلا", "مرحبا", "سلام", "اهلا", "hi", "hello"]
            if lower in greetings:
                await self.highrise.chat(rand(GREETINGS_RESPONSES))
                return

            if "شكرا" in lower or "تسلم" in lower:
                await self.highrise.chat(f"👑 التنين يشكرك {username}! 💎")
                return

            if "شلونك" in lower or "كيفك" in lower:
                await self.highrise.chat("🐉 التنين بخير، يحرس الكنوز! 💎")
                return

        except Exception as e:
            print(f"❌ Chat error: {e}")


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
    
    # ← الأهم: نستدعي main() مع asyncio.run()
    asyncio.run(main([BotDefinition(DragonBot(), room_id, token)]))
