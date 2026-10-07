import os
import random
import asyncio
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata
from highrise.__main__ import BotDefinition, main

# ═══════════════════════════════════════
# 🐉 إعدادات الغرفة
# ═══════════════════════════════════════
ROOM_NAME = "نرد التنين"

# مساحة الحركة العشوائية (18 × 30 → نستخدم حدود آمنة)
ROOM_X_MIN = -6
ROOM_X_MAX = 6
ROOM_Z_MIN = -10
ROOM_Z_MAX = 10

# وقت بين كل حركة
MOVE_MIN_DELAY = 8
MOVE_MAX_DELAY = 15

# ═══════════════════════════════════════
# 🐉 رسائل حسب العلاقة
# ═══════════════════════════════════════
NEW_USER_MESSAGES = [
    "🐉 زئير! من هذا الغريب؟ 👁️\nمرحباً {user}! أول مرة أشوفك هنا 🌟",
    "🐲 أوه! وجه جديد!\nأهلاً بك {user} في عرين التنين 💎",
    "🔥 التنين شمّ رائحة جديدة!\nمنور {user}! شنو اسمك؟ 🌟",
    "🐉 عين التنين رصدتك {user}...\nمرحباً بك في مملكتي 👑",
]

FRIEND_MESSAGES = [
    "🐉 يا هلا! {user} رجع!\nنورتني مرة ثانية 💎",
    "🔥 {user}! التنين كان ينتظرك! 👑",
    "🐲 أهلاً {user}!\nكل مرة تجي فيها = صديق أفضل 🌟",
    "💎 {user} وصل! التنين يحب شوفتك 🐉",
]

CLOSE_FRIEND_MESSAGES = [
    "🐉 {user}!! التنين اشتاقلك!\nإنت من أعز الأصدقاء 💎",
    "👑 يا هلا {user}!\nإنت من أفراد المملكة المقربين 🔥",
    "🐲 {user} الوحش رجع!\nغرفة التنين تنور بوجودك ✨",
]

BEST_FRIEND_MESSAGES = [
    "🐉 {user}!! أخيراً!\nإنت أخو التنين الحقيقي! 👑🔥",
    "💎 {user}!\nالتنين يضع تاجك اليوم! 👑",
    "🔥 {user}!\nإنت كنز المملكة! 💎🐉",
]

# ═══════════════════════════════════════
# 🐉 أسئلة للمتابعة
# ═══════════════════════════════════════
QUESTIONS = [
    "🐉 شنو أخبارك اليوم؟",
    "💎 كيف كان يومك؟",
    "🔥 شنو سويت اليوم؟",
    "👑 شنو تحب تسوي باللعبة؟",
    "🐲 وين تحب تلعب عادة؟",
    "🌟 تعرف أحد ثاني في الغرفة؟",
    "💎 شنو نوع الألعاب المفضلة عندك؟",
    "🔥 هل تلعب Highrise من مدة طويلة؟",
]

# ═══════════════════════════════════════
# 🐉 بيانات الألعاب
# ═══════════════════════════════════════
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
    "🐲 قلد صوت التنين",
]

COMPLIMENTS = [
    "🐉 إنت مقاتل حقيقي! 🔥",
    "💎 إنت كنز نادر! 👑",
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
]

# ═══════════════════════════════════════
# ذاكرة الألعاب (لا تُحفظ)
# ═══════════════════════════════════════
rps_games = {}
guess_games = {}
riddle_games = {}

# ذاكرة العلاقات (تُفقد عند Restart)
user_visits = {}     # {username: عدد الزيارات}


def rand(arr):
    return random.choice(arr)


# ═══════════════════════════════════════
# 🐉 كلاس البوت
# ═══════════════════════════════════════
class DragonBot(BaseBot):

    def __init__(self):
        super().__init__()
        self.movement_task = None
        self.is_greeting = False
        self.current_target = None

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print(f"🐉 Dragon Bot Awakened in {ROOM_NAME}!")
        await asyncio.sleep(3)
        # ابدأ حلقة الحركة العشوائية
        self.movement_task = asyncio.create_task(self.random_movement_loop())

    # ═══════════════════════════════════════
    # 🚶 الحركة العشوائية
    # ═══════════════════════════════════════
    async def random_movement_loop(self):
        while True:
            try:
                if not self.is_greeting:
                    x = random.uniform(ROOM_X_MIN, ROOM_X_MAX)
                    z = random.uniform(ROOM_Z_MIN, ROOM_Z_MAX)
                    pos = Position(
                        x=float(x),
                        y=0.0,
                        z=float(z),
                        facing="FrontRight"
                    )
                    await self.highrise.walk_to(pos)
                    print(f"🚶 Random move → ({x:.1f}, {z:.1f})")
                
                delay = random.uniform(MOVE_MIN_DELAY, MOVE_MAX_DELAY)
                await asyncio.sleep(delay)
            except Exception as e:
                print(f"❌ Move error: {e}")
                await asyncio.sleep(5)

    # ═══════════════════════════════════════
    # 👤 عندما يدخل مستخدم
    # ═══════════════════════════════════════
    async def on_user_join(self, user: User, position) -> None:
        try:
            username = user.username
            print(f"👤 {username} entered the lair")

            # إيقاف الحركة العشوائية
            self.is_greeting = True
            await asyncio.sleep(0.5)

            # التحرك نحو المستخدم
            try:
                if position and hasattr(position, 'x') and hasattr(position, 'z'):
                    target_x = position.x + random.uniform(-1.5, 1.5)
                    target_z = position.z + random.uniform(-1.5, 1.5)
                    pos = Position(
                        x=float(target_x),
                        y=0.0,
                        z=float(target_z),
                        facing="FrontRight"
                    )
                    await self.highrise.walk_to(pos)
                    print(f"🚶 Moving toward {username} → ({target_x:.1f}, {target_z:.1f})")
                    await asyncio.sleep(2)
            except Exception as e:
                print(f"⚠️ Walk to user error: {e}")

            # عدد الزيارات
            visits = user_visits.get(username, 0)
            user_visits[username] = visits + 1

            # اختيار الرسالة حسب العلاقة
            if visits == 0:
                greeting = rand(NEW_USER_MESSAGES).replace("{user}", username)
                print(f"🌟 New user: {username}")
            elif visits < 5:
                greeting = rand(FRIEND_MESSAGES).replace("{user}", username)
                print(f"💎 Friend: {username} ({visits+1} visits)")
            elif visits < 15:
                greeting = rand(CLOSE_FRIEND_MESSAGES).replace("{user}", username)
                print(f"👑 Close friend: {username} ({visits+1} visits)")
            else:
                greeting = rand(BEST_FRIEND_MESSAGES).replace("{user}", username)
                print(f"🔥 Best friend: {username} ({visits+1} visits)")

            await self.highrise.chat(greeting)

            # سؤال متابعة بعد 3 ثواني
            await asyncio.sleep(3)
            question = rand(QUESTIONS)
            await self.highrise.chat(question)

        except Exception as e:
            print(f"❌ Join error: {e}")
        finally:
            # انتظار قبل استئناف الحركة
            await asyncio.sleep(5)
            self.is_greeting = False

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
                    "✊ !3 حجر ورقة مقص\n"
                    "🎯 !4 خمن الكنز\n"
                    "🧩 !5 لغز التنين\n"
                    "😂 !6 نكتة\n"
                    "😈 !7 تحدي\n"
                    "🌹 !8 مدح\n"
                    "👑 !9 حكمة التنين"
                )
                return

            # !1 نرد
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

            # !4 خمن
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
                await self.highrise.chat(f"🐉 التنين بخير! شنو أخبارك {username}؟")
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
    asyncio.run(main([BotDefinition(DragonBot(), room_id, token)]))
