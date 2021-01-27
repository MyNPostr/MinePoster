import discord
import sqlite3
from discord.ext import commands

conn = sqlite3.connect("discord.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (id, nick, rating, looses, wins)''')
conn.commit()


bot = commands.Bot(command_prefix='?', help_command=None)


@bot.event
async def on_ready():
    print("Бот запущен")
    guilds = len(bot.guilds)
    await bot.change_presence(activity=discord.Game(name=f"В хадилку брадилку с {guilds} серверами."))
    for guild in bot.guilds:
        print(guild.name, 'Успешно загружен')
        nol = 0
        for member in guild.members:
            c.execute(f"SELECT id FROM users where id={member.id}")
            if c.fetchone() is None:
                c.execute(
                    f"INSERT INTO users VALUES ({member.id}, '{member.name}', {nol}, {nol}, {nol})")
            else:
                pass
            conn.commit()


@bot.event
async def on_member_join(member):
    c.execute(f"SELECT id FROM users where id={member.id}")
    if c.fetchone() is not None:
        pass
    else:
        c.execute(f"INSERT INTO users VALUES ({member.id}, '{member.name}', 0)")
    conn.commit()


@bot.command(pass_context=True)
async def win(ctx, user: discord.Member):
    role = discord.utils.find(lambda r: r.name == 'Programmer', ctx.message.server.roles)
    if role in user.roles:
        await ctx.message.delete()
        embed = discord.Embed(
            color=discord.Color.red(),
            title="Победа"
        )
    for row in c.execute(f"SELECT rating FROM users where id={user.id}"):
        rating = row[0] + 2
        c.execute(f'UPDATE users SET rating = {rating} where id={user.id}')
    for row1 in c.execute(f"SELECT wins FROM users where id={user.id}"):
        wins = row1[0] + 1
        c.execute(f'UPDATE users SET wins = {wins} where id={user.id}')
        embed.add_field(name='Молодец!', value=f"{user.mention} Выйграл в этом раунде!!")
        embed.set_footer(text="Команда выполнена: @{}".format(ctx.author.display_name))
        await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def loose(ctx, user: discord.Member):
    await ctx.message.delete()
    embed = discord.Embed(
        color=discord.Color.red(),
        title="Поражение"
    )
    embed.add_field(name='Эхххх...', value=f"{user.mention} Проиграл в этом раунде:(")
    embed.set_footer(text="Команда выполнена: @{}".format(ctx.author.display_name))
    for row in c.execute(f"SELECT rating FROM users where id={user.id}"):
        rating = row[0] - 1
        c.execute(f'UPDATE users SET rating = {rating} where id={user.id}')
    for row1 in c.execute(f"SELECT looses FROM users where id={user.id}"):
        looses = row1[0] + 1
        c.execute(f'UPDATE users SET looses = {looses} where id={user.id}')
        await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def profile(ctx, user: discord.Member):
    await ctx.message.delete()
    embed = discord.Embed(
        color=discord.Color.red(),
        title="Профиль"
    )
    for row in c.execute(f"SELECT rating FROM users where id={user.id}"):
        rating = row[0]
        if user.id != 276627019822006274:
            if rating >= 100:
                rank = "Мастер"
            else:
                if rating >= 50:
                    rank = "Профессионал"
                else:
                    if rating >= 25:
                        rank = "Любитель"
                    else:
                        rank = "Новичок"
        else:
            rank = "Developer"
        for row1 in c.execute(f"SELECT looses FROM users where id={user.id}"):
            for row2 in c.execute(f"SELECT wins FROM users where id={user.id}"):
                wins = row1[0]
                looses = row2[0]
                if looses > 0:
                    kdr = round(wins / looses, 2)
                else:
                    kdr = wins
                embed.add_field(name='Участник', value=f"{user.mention}", inline=True)
                embed.add_field(name='Рейтинг', value=f"{rating}", inline=True)
                embed.add_field(name='Ранг', value=f"{rank}", inline=True)
                embed.add_field(name='ОПП', value=f"{kdr}", inline=True)
                embed.set_footer(text="Команда запрошена: @{}".format(ctx.author.display_name))
                await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def info(ctx):
    await ctx.message.delete()
    dev = "276627019822006274"
    embed = discord.Embed(
        color=discord.Color.red(),
        title="Информация о боте"
    )
    embed.add_field(name='Автор', value=f"Автор бота MinePoster это <@{dev}>", inline=True)
    embed.add_field(name='Версия бота', value='Бот находится в бета тесте. Версия:  0.1.2', inline=True)
    embed.add_field(name='GitHub', value='https://github.com/MemePhoenix/MinePoster', inline=True)
    embed.add_field(name='Top.gg', value="Вы можете проголосовать по Ссылке: https://top.gg/bot/776444400683188234",
                    inline=True)
    embed.add_field(name='!win @упоминание', value='Выдает очки упомянутому человеку за победу.', inline=False)
    embed.add_field(name='!loose @упоминание', value='Отнимает очки у упомянутого человека за поражение.', inline=False)
    embed.add_field(name='!profile @упоминание', value='Показывает профиль участника.', inline=False)
    embed.add_field(name='!info', value='Показывает это сообщение.', inline=False)
    embed.set_footer(text="Команда запрошена: @{}".format(ctx.author.display_name))
    await ctx.send(embed=embed)


bot.run('Ваш токен | Your token')

