import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

timers = {}  # Словарь для хранения таймеров

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='защита')
async def defense_timer(ctx):
    await start_timer(ctx, 'defense_timer', 'Таймер защиты включен на 2 часа!', 2)

@bot.command(name='атака')
async def attack_timer(ctx):
    await start_timer(ctx, 'attack_timer', 'Таймер атаки включен на 4 часа!', 4)

@bot.command(name='сколько_осталось', aliases=['сколько', 'взп', 'ближ'])
async def time_left(ctx):
    timer_name, time_left_str = get_time_left(ctx.channel.id)
    await ctx.send(f"До завершения таймера {timer_name} осталось {time_left_str}.")

@bot.command(name='свой_таймер')
async def custom_timer(ctx, hours: int):
    if hours <= 0:
        await ctx.send("Пожалуйста, укажите положительное количество часов.")
        return

    await start_timer(ctx, 'custom_timer', f'Таймер на {hours} часов включен!', hours)

@bot.command(name='стоп')
async def stop_timer(ctx):
    timer_name, _ = get_time_left(ctx.channel.id)
    if timer_name != "нет активных таймеров":
        await ctx.send(f"Таймер {timer_name} остановлен.")
        del timers[timer_name]
        check_timers.stop()
    else:
        await ctx.send("Нет активных таймеров для остановки.")

async def start_timer(ctx, timer_name, message, hours):
    if timer_name in timers:
        await ctx.send(f"Таймер {timer_name} уже запущен.")
        return

    end_time = datetime.utcnow() + timedelta(hours=hours)
    timers[timer_name] = {"end_time": end_time, "channel": ctx.channel.id}
    await ctx.send(message)
    await check_timers.start(ctx=ctx, timer_name=timer_name)

@tasks.loop(minutes=1)
async def check_timers(ctx, timer_name):
    end_time = timers[timer_name]["end_time"]
    channel_id = timers[timer_name]["channel"]
    time_left = end_time - datetime.utcnow()

    if time_left <= timedelta(0):
        await bot.get_channel(channel_id).send(f"Таймер {timer_name} завершен! @everyone")
        del timers[timer_name]
        check_timers.stop()
    elif time_left <= timedelta(minutes=30) and time_left > timedelta(minutes=29):
        await bot.get_channel(channel_id).send(f"Осталось 30 минут до завершения таймера {timer_name}.")
    elif time_left <= timedelta(minutes=15) and time_left > timedelta(minutes=14):
        await bot.get_channel(channel_id).send(f"Осталось 15 минут до завершения таймера {timer_name}.")
    elif time_left <= timedelta(minutes=10) and time_left > timedelta(minutes=9):
        await bot.get_channel(channel_id).send(f"Осталось 10 минут до завершения таймера {timer_name}.")

def get_time_left(channel_id):
    for timer_name, timer_data in timers.items():
        if timer_data["channel"] == channel_id:
            time_left = timer_data["end_time"] - datetime.utcnow()
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            return timer_name, f"{hours} часов {minutes} минут"
    return "нет активных таймеров", ""

bot.run('MTE5OTEwNTM0MDg2NDczNzM1MA.GFPmvq.IpRDPDutemZ3mBxMYC_2S97AuvY9sHYk73w0u8')
