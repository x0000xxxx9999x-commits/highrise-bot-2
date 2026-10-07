import os
import random
import asyncio
from highrise import BaseBot, User, Position, AnchorPosition
from highrise.models import SessionMetadata

# ═══════════════════════════════════════
# إعدادات الموقع (للبعد عن الباب)
# ═══════════════════════════════════════
# غير هذي الأرقام حسب غرفتك
MOVE_X = 8
MOVE_Z = 8
MOVE_FACING = "FrontRight"

# ═══════════════════════════════════════
# بيانات
# ═══════════════════════════════════════
JOKES = [
    'واحد دخل المطعم قال: عندكم دجاج؟ قال: لا. قال: ليش المطعم مفتوح؟ قال: نخبر الناس! 😂',
    'واحد راح للدكتور قال: كل ما أشرب شاي أحس بألم في عيني! قال: شيل الملعقة من الكوب! 😂',
    'سألوا واحد: ليش تمشي ورا البنت؟ قال: من زود الأدب! 😂',
]

RIDDLES = [
    {'q': 'شي يمشي وما عنده رجلين؟', 'a': 'الماء'},
    {'q': 'شي كل ما أخذت منه كبر؟', 'a': 'الحفرة'},
    {'q': 'عنده أسنان وما يعض؟', 'a': 'المشط'},
]

CHALLENGES = [
    'اكتب اسمك بالمقلوب! 🔄',
    'قل شي حلو لأول شخص يدخل! 🌹',
    'سوي رقصة! 💃',
]

COMPLIMENTS = [
    'إنت أسطورة! 🔥',
    'وجودك ينور الغرفة! ✨',
    'إنت الأفضل! 💯',
]

# ═══════════════════════════════════════
# ذاكرة الألعاب
# ═══════════════════════════════════════
rps_games = {}
guess_games = {}
riddle_games = {}


class KhafajiBot2(BaseBot):

    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("✅ Bot 2 Connected!")
        print("📡 جاري الابتعاد عن الباب...")
        await asyncio.sleep(3)
        await self.move_away()

    async def move_away(self):
        """البوت يبتعد 8 خطوات عن الباب"""
        try:
            position = Position(
                x=float(MOVE_X),
                y=0.0,
                z=float(MOVE_Z),
                facing=MOVE_FACING
            )
            await self.highrise.walk_to(position)
            print(f"✅ Moved to ({MOVE_X}, {MOVE_Z})")
        except Exception as e:
            print(f"❌ Move error: {e}")

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        print(f"👤 Join: {user.username}")
        try:
            await asyncio.sleep(0.5)
            await self.highrise.chat(f"مرحباً بك {user.username} في غرفة BLACK MARKET 🕶️")
        except Exception as e:
            print(f"❌ Welcome error: {e}")

    async def on_chat(self, user: User, message: str) -> None:
        try:
            username = user.username
            text = message.strip()
            lower = text.lower()

            print(f"📨 {username}: {text}")

            # ═══ !help ═══
            if lower in ["!help", "!مساعدة"]:
                await self.send("📜 الأوامر:\n!1 نرد | !2 عملة | !3 حجر ورقة مقص | !4 خمن\n!5 لغز | !6 نكتة | !7 تحدي | !8 مدح\n!user [اسم] | !رقص")
                return

            # ═══ !رقص - الرقص ═══
            if lower == "!رقص" or lower == "!dance":
                await self.dance_self()
                return

            # ═══ !1 نرد ═══
            if lower in ["!1", "!نرد"]:
                n = random.randint(1, 6)
                await self.send(f"🎲 {username} رمى النرد: {n}")
                return

            # ═══ !2 عملة ═══
            if lower in ["!2", "!عملة"]:
                r = "صورة 👑" if random.random() < 0.5 else "كتابة 📝"
                await self.send(f"🪙 {username}: {r}")
                return

            # ═══ !3 حجر ورقة مقص ═══
            if lower in ["!3", "!حجر"]:
                rps_games[username] = True
                await self.send(f"✊ {username} اختر:\n1=حجر\n2=ورقة\n3=مقص")
                return

            if username in rps_games and lower in ["1", "2", "3"]:
                choices = {"1": "حجر", "2": "ورقة", "3": "مقص"}
                bot_choice = str(random.randint(1, 3))
                if lower == bot_choice:
                    result = "🤝 تعادل!"
                elif (lower == "1" and bot_choice == "3") or \
                     (lower == "2" and bot_choice == "1") or \
                     (lower == "3" and bot_choice == "2"):
                    result = "🎉 فزت!"
                else:
                    result = "😢 خسرت!"
                await self.send(f"أنت: {choices[lower]} | البوت: {choices[bot_choice]} — {result}")
                del rps_games[username]
                return

            # ═══ !4 خمن ═══
            if lower in ["!4", "!خمن"]:
                target = random.randint(1, 50)
                guess_games[username] = {"target": target, "tries": 0}
                await self.send(f"🎯 {username} خمن رقم بين 1 و 50!")
                return

            if username in guess_games and lower.isdigit():
                guess = int(lower)
                game = guess_games[username]
                game["tries"] += 1
                if guess == game["target"]:
                    await self.send(f"🎉 {username} صح! في {game['tries']} محاولات")
                    del guess_games[username]
                elif guess < game["target"]:
                    await self.send(f"⬆️ أكبر من {guess}")
                else:
                    await self.send(f"⬇️ أصغر من {guess}")
                return

            # ═══ !5 لغز ═══
            if lower in ["!5", "!لغز"]:
                r = random.choice(RIDDLES)
                riddle_games[username] = r["a"]
                await self.send(f"🧩 {username} {r['q']}")
                return

            if username in riddle_games and not lower.startswith("!"):
                answer = riddle_games[username]
                if text == answer:
                    await self.send(f"🎉 {username} صح! الجواب: {answer}")
                else:
                    await self.send(f"❌ خطأ! الجواب: {answer}")
                del riddle_games[username]
                return

            # ═══ !6 نكتة ═══
            if lower in ["!6", "!نكتة"]:
                await self.send(f"😂 {username} {random.choice(JOKES)}")
                return

            # ═══ !7 تحدي ═══
            if lower in ["!7", "!تحدي"]:
                await self.send(f"😈 {username} {random.choice(CHALLENGES)}")
                return

            # ═══ !8 مدح ═══
            if lower in ["!8", "!مدح"]:
                await self.send(f"🌹 {username} {random.choice(COMPLIMENTS)}")
                return

            # ═══ !user ═══
            if lower.startswith("!user") or lower.startswith("!معلومات"):
                target = text.replace("!user", "").replace("!معلومات", "").strip().replace("@", "").strip()
                if not target:
                    target = username
                await self.send(f"🔍 جاري البحث عن {target}...")
                try:
                    profile = await self.highrise.get_user(target)
                    if profile and profile.user:
                        u = profile.user
                        info = [f"👤 {u.username}"]
                        if hasattr(u, 'bio') and u.bio:
                            info.append(f"📝 {u.bio}")
                        info.append(f"⭐ {getattr(u, 'followers', 0)}")
                        await self.send(f"📋 {' | '.join(info)}")
                    else:
                        await self.send(f"❌ ما لقيت {target}")
                except Exception as e:
                    print(f"❌ user error: {e}")
                    await self.send(f"⚠️ خطأ في جلب المعلومات")
                return

            # ═══ ردود تلقائية ═══
            greetings = ["هلا", "مرحبا", "سلام", "اهلا", "hi", "hello"]
            if lower in greetings:
                await self.send(f"👋 أهلاً {username}!")
                return

            if "شكرا" in lower or "تسلم" in lower:
                await self.send(f"🤍 على الرحب {username}!")
                return

        except Exception as e:
            print(f"❌ Chat error: {e}")

    async def send(self, message: str):
        """إرسال رسالة بأمان"""
        try:
            await self.highrise.chat(message)
        except Exception as e:
            print(f"❌ Send error: {e}")

    async def dance_self(self):
        """البوت يرقص"""
        try:
            # رقصة افتراضية - نقدر نغيرها
            dance_id = "emote-dance"
            await self.highrise.send_emote(dance_id)
            await self.highrise.chat("💃 يرقص!")
        except Exception as e:
            print(f"❌ Dance error: {e}")


# ═══════════════════════════════════════
# تشغيل
# ═══════════════════════════════════════
if __name__ == "__main__":
    bot = KhafajiBot2()
    bot.run(
        os.getenv("HIGHRISE_TOKEN", ""),
        os.getenv("HIGHRISE_ROOM_ID", "")
                  )
