import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types
import datetime

# قراءة التوكن والمفتاح من إعدادات السيرفر بأمان
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# إعداد الذكاء الاصطناعي
ai_client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

SYSTEM_INSTRUCTION = """
أنت مساعد أدمن لـ Discord متخصص في تحليل مشاعر الشات.
مهمتك هي اكتشاف المشاحنات والنزاعات التصاعدية، والتهكم العدائي، والمشاجرات بين المستخدمين (حتى لو لم تحتوي على شتائم صريحة).

قم بتقييم النص أو السياق ورد فقط بكلمة واحدة من الكلمتين التاليين:
1. "TOXIC" : إذا كان الكلام يحتوي على جدال حاد جداً، هجوم شخصي، استفزاز، أو بداية خناقة وعداء.
2. "OK" : إذا كان المحادثة طبيعية، نقاش عادي، مزاح صديق، أو كلام لا يستدعي التدخل.

رد بـ TOXIC أو OK فقط دون أي شرح إضافي.
"""

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت بنجاح باسم: {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.strip()
    if not content or len(content) < 4:
        await bot.process_commands(message)
        return

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"اسم المستخدم: {message.author.display_name}\nالرسالة: {content}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.1
            )
        )

        result = response.text.strip().upper()

        if "TOXIC" in result:
            duration = datetime.timedelta(minutes=5)
            await message.author.timeout(duration, reason="اكتشاف جدال حاد أو خناقة بواسطة الذكاء الاصطناعي")
            await message.channel.send(
                f"⚠️ تم تطبيق تايم أوت لمدة 5 دقائق على {message.author.mention} بسبب إثارة الجدل أو المشاحنات."
            )

    except Exception as e:
        print(f"حدث خطأ: {e}")

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)