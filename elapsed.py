import discord
import sqlite3
from discord.ext import commands
import random
import time

conn = sqlite3.connect("swift.db")
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (guild_id, id, nick, lvl, xp, voice_activity, rep, enter_date, clan_id)''')
c.execute('''CREATE TABLE IF NOT EXISTS clans
             (guild_id, owner_id, clan_name, members, clan_id, lvl, xp, create_date)''')
conn.commit()

bot = commands.Bot(command_prefix='sw!', help_command=None)


@bot.event
async def on_ready():
    print("Бот готов играть в Brawl Stars")
    global tdict
    tdict = {}
    for guild in bot.guilds:
        for member in bot.get_all_members():
            print(member.name)
            c.execute(f"SELECT id FROM users where id={member.id}")
            named_tuple = time.localtime()
            time_string = time.strftime("%d.%m.%Y", named_tuple)
            if c.fetchone() == None:
                c.execute(
                    f"INSERT INTO users VALUES ({guild.id}, '{member.id}', '{member.name}', 0, 0, 0, 0, '{time_string}', 'none')")
            else:
                pass
            conn.commit()


@bot.event
async def on_member_join(member):
    named_tuple = time.localtime()
    time_string = time.strftime("%d.%m.%Y", named_tuple)
    c.execute(f"SELECT id FROM users where id={member.id}")
    if c.fetchone() == None:
        c.execute(
            f"INSERT INTO users VALUES ({member.guild.id}, '{member.id}', '{member.name}', 0, 0, 0, 0, '{time_string}', 'none')")
    else:
        pass
    conn.commit()


@bot.event
async def on_message(message):
    if len(message.content) > 10:
        for row in c.execute(f"SELECT xp,lvl FROM users where id={message.author.id}"):
            exp = row[0] + random.randint(5, 15)
            c.execute(f'UPDATE users SET xp={exp} where id={message.author.id}')
            if row[0] >= 1000 and row[0] < 2000:
                lvch = 1
            elif row[1] == 0:
                lvch = 0
            else:
                lvch = exp / 1000
            lv = int(lvch)
            c.execute(f'UPDATE users SET lvl={lv} where id={message.author.id}')
    await bot.process_commands(message)
    conn.commit()


@bot.command(pass_context=True)
async def reg(ctx, user: discord.Member):
    await ctx.message.delete()
    if ctx.author.guild_permissions.administrator:
        print(f"{user.name} Забивается в БД...")
        c.execute(f"SELECT id FROM users where id={user.id}")
        named_tuple = time.localtime()
        time_string = time.strftime("%d.%m.%Y", named_tuple)
        if c.fetchone() is None:
            c.execute(
                f"INSERT INTO users VALUES ({ctx.guild.id}, {user.id}, '{user.name}', 0, 0, 0, 0, '{time_string}', 'none')")
            print(f"{user.name} Был забит в БД")
        else:
            print(f"{user.name} Уже в БД")
            pass


@bot.listen("on_command_error")
async def cooldown_message(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            color=discord.Color.green(),
            title=f":x: Ошибка :x:",
            description=f"У вас перезарядка на команду.\nПодождите {round(error.retry_after)} секунд чтобы использовать эту команду"
        )
        await ctx.send(embed=embed)


@bot.command(pass_context=True)
@commands.cooldown(1, 120, commands.BucketType.user)
async def reputation(ctx, user: discord.Member):
    await ctx.message.delete()
    if user.id != ctx.author.id:
        for row in c.execute(f"SELECT rep FROM users where id={user.id}"):
            embed = discord.Embed(
                color=discord.Color.green(),
                title=f"Успешно",
                description=f"Успешно выдан 1 респект участнику <@{user.id}> :thumbsup: "
            )
            newrep = row[0] + 1
            c.execute(f'UPDATE users SET rep={newrep} where id={user.id}')
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            color=discord.Color.red(),
            title=f"Ошибка :x: ",
            description=f"Вы не можете выдавать респект себе"
        )
        await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def report(ctx, user: discord.Member, *reason):
    await ctx.message.delete()
    if reason != False:
        if user.id != ctx.author.id:
            embed = discord.Embed(
                color=discord.Color.green(),
                title=f"Успешно",
                description=f"Жалоба на участника <@{user.id}> отправлена"
            )
            embed.set_thumbnail(url=user.avatar_url)
            await ctx.send(embed=embed)
            reason = " ".join(reason)
            embed2 = discord.Embed(
                color=discord.Color.green(),
                title=f"Новая жалоба",
                description=f":no_entry: Участник <@{ctx.author.id}> отправил жалобу на <@{user.id}>\nПо причине: {reason} :no_entry:"
            )
            channel = bot.get_channel(845220536326160386)
            embed.set_thumbnail(url=user.avatar_url)
            await channel.send(embed=embed2)
        else:
            await ctx.message.delete()
            embed = discord.Embed(
                color=discord.Color.red(),
                title=f"Ошибка :x: ",
                description=f"Вы не можете писать жалобу на себя"
            )
            await ctx.send(embed=embed)
    else:
        await ctx.message.delete()
        embed = discord.Embed(
            color=discord.Color.red(),
            title=f"Ошибка :x: ",
            description=f"Вы должны написать причину жалобы"
        )
        await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def aboutme(ctx):
    await ctx.message.delete()
    for row in c.execute(f"SELECT nick,lvl,voice_activity,rep,enter_date,clan_id FROM users where id={ctx.author.id}"):
        if row[2] < 60:
            if row[5] == 'none':
                myclan = 'Нету'
            else:
                for row1 in c.execute(
                        f"SELECT clan_name FROM clans where clan_id={row[5]}"):
                    myclan = row1[0]
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"Профиль участника {row[0]}"
            )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name=':arrow_up:Уровень:', value=f"```{row[1]}```", inline=True)
            embed.add_field(name=':clock2:Голосовая Активность:', value=f"```{row[2]} минут```", inline=True)
            embed.add_field(name=':thumbsup:Репутации:', value=f"```{row[3]}```", inline=True)
            embed.add_field(name=':calendar:Дата входа на сервер:', value=f"```{row[4]}```", inline=True)
            embed.add_field(name=':crossed_swords:Клан:', value=f"```{myclan}```", inline=True)
            await ctx.send(embed=embed)
        else:
            vt = round(row[2] / 60, 1)
            if row[5] == 'none':
                myclan = 'Нету'
            else:
                for row1 in c.execute(
                        f"SELECT clan_name FROM clans where clan_id={row[5]}"):
                    myclan = row1[0]
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"Профиль участника {row[0]}"
            )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name=':arrow_up:Уровень:', value=f"```{row[1]}```", inline=True)
            embed.add_field(name=':clock2:Голосовая Активность:', value=f"```{vt} часов```", inline=True)
            embed.add_field(name=':thumbsup:Репутации:', value=f"```{row[3]}```", inline=True)
            embed.add_field(name=':calendar:Дата входа на сервер:', value=f"```{row[4]}```", inline=True)
            embed.add_field(name=':crossed_swords:Клан:', value=f"```{myclan}```", inline=True)
            await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def about(ctx, user: discord.Member):
    await ctx.message.delete()
    for row in c.execute(f"SELECT nick,lvl,voice_activity,rep,enter_date,clan_id FROM users where id={user.id}"):
        if row[2] < 60:
            if row[5] == 'none':
                myclan = 'Нету'
            else:
                for row1 in c.execute(
                        f"SELECT clan_name FROM clans where clan_id={row[5]}"):
                    myclan = row1[0]
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"Профиль участника {row[0]}"
            )
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name=':arrow_up:Уровень:', value=f"```{row[1]}```", inline=True)
            embed.add_field(name=':clock2:Голосовая Активность:', value=f"```{row[2]} минут```", inline=True)
            embed.add_field(name=':thumbsup:Репутации:', value=f"```{row[3]}```", inline=True)
            embed.add_field(name=':calendar:Дата входа на сервер:', value=f"```{row[4]}```", inline=True)
            embed.add_field(name=':crossed_swords:Клан:', value=f"```{myclan}```", inline=True)
            await ctx.send(embed=embed)
        else:
            if row[5] == 'none':
                myclan = 'Нету'
            else:
                for row1 in c.execute(
                        f"SELECT clan_name FROM clans where clan_id={row[5]}"):
                    myclan = row1[0]
            vt = round(row[2] / 60, 1)
            embed = discord.Embed(
                color=discord.Color.blue(),
                title=f"Профиль участника {row[0]}"
            )
            embed.set_thumbnail(url=user.avatar_url)
            embed.add_field(name=':arrow_up:Уровень:', value=f"```{row[1]}```", inline=True)
            embed.add_field(name=':clock2:Голосовая Активность:', value=f"```{vt} часов```", inline=True)
            embed.add_field(name=':thumbsup:Репутации:', value=f"```{row[3]}```", inline=True)
            embed.add_field(name=':calendar:Дата входа на сервер:', value=f"```{row[4]}```", inline=True)
            embed.add_field(name=':crossed_swords:Клан:', value=f"```{myclan}```", inline=True)
            await ctx.send(embed=embed)


@bot.group(invoke_without_command=True)
async def clan(ctx):
    @clan.command()
    async def help(ctx):
        await ctx.message.delete()
        embed = discord.Embed(
            color=discord.Color.blue(),
            title="Информация о кланах"
        )
        embed.add_field(name='sw!clan help', value='`Показывает данное сообщение`',
                        inline=False)
        embed.add_field(name='sw!clan create id название', value='`Создает клан`',
                        inline=False)
        embed.add_field(name='sw!clan join клан', value='`Вступить в клан`',
                        inline=False)
        embed.add_field(name='sw!clan leave', value='`Отправляет жалобу на участника`',
                        inline=False)
        embed.add_field(name='sw!clan info', value='`Отправляет жалобу на участника`',
                        inline=False)
        embed.add_field(name='sw!clan top', value='`Отправляет жалобу на участника`',
                        inline=False)
        embed.add_field(name='sw!clan duel id', value='`Отправляет жалобу на участника`',
                        inline=False)
        embed.set_footer(text="Команда запрошена: @{}".format(ctx.author.display_name))
        await ctx.send(embed=embed)

        @clan.command()
        async def create(ctx, id, name):
            await ctx.message.delete()
            clan_ids = list()
            clan_names = list()
            for row in c.execute(
                    f"SELECT clan_name,clan_id from clans WHERE guild_id={ctx.guild.id}"):
                clan_names.append(row[0])
                clan_ids.append(row[1])
            if id not in clan_ids:
                if name not in clan_names:
                    named_tuple = time.localtime()
                    time_string = time.strftime("%d.%m.%Y", named_tuple)
                    c.execute(
                        f"INSERT INTO clans VALUES ({ctx.guild.id}, {ctx.author.id}, '{name}', 1, {id}, 0, 0, '{time_string}')")
                    c.execute(f'UPDATE users SET clan_id={id} where id={ctx.author.id}')


@bot.command(pass_context=True)
async def help(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="Информация о боте"
    )
    embed.add_field(name='Префикс', value='`Префикс бота является sw!`',
                    inline=False)
    embed.add_field(name='sw!aboutme', value='`Узнать свой уровень и прочее`',
                    inline=False)
    embed.add_field(name='sw!reputation @пользователь', value='`Отправить респект игроку`',
                    inline=False)
    embed.add_field(name='sw!report @пользователь причина', value='`Отправляет жалобу на участника`',
                    inline=False)
    embed.add_field(name='sw!about @пользователь', value='`Узнать уровень и прочее другого участника`',
                    inline=False)
    embed.add_field(name='sw!leaders', value='`Показывает список лидеров`',
                    inline=False)
    embed.add_field(name='sw!help', value='`Показывает это сообщение.`', inline=False)
    embed.set_footer(text="Команда запрошена: @{}".format(ctx.author.display_name))
    await ctx.send(embed=embed)


@bot.event
async def on_voice_state_update(member, before, after):
    for row in c.execute(f"SELECT xp,lvl,voice_activity FROM users where id={member.id}"):
        author = member.id
        if before.channel is None and after.channel is not None:
            t1 = time.time()
            tdict[author] = t1
        elif before.channel is not None and after.channel is None and author in tdict:
            t2 = time.time()
            tiv = t2 - tdict[author]
            vt = round(tiv / 60, 1)
            if vt >= 1:
                exp = row[0] + int(vt) * 2
                c.execute(f'UPDATE users SET xp={exp} where id={member.id}')
                if exp >= 1000 and exp < 2000:
                    lvch = 1
                elif exp == 0:
                    lvch = 0
                else:
                    lvch = exp / 1000
                lv = int(lvch)
                c.execute(f'UPDATE users SET lvl={lv} where id={member.id}')
            vt = row[2] + vt
            c.execute(f'UPDATE users SET voice_activity={vt} where id={member.id}')


@bot.command(pass_context=True)
async def leaders(ctx):
    await ctx.message.delete()
    top = list()
    for row in c.execute(
            f"SELECT nick,lvl,xp from users WHERE guild_id = {ctx.guild.id} ORDER BY xp + 0 DESC LIMIT 6"):
        top.append(row)
    top1 = top[0]
    top2 = top[1]
    top3 = top[2]
    top4 = top[3]
    top5 = top[4]
    embed = discord.Embed(
        color=discord.Color.blue(),
        title="Таблица Лидеров"
    )
    embed.add_field(name='Первое место',
                    value=f"```\nНик:{top1[0]}.\nУровень:{top1[1]}.\nОпыт:{top1[2]}```", inline=False)
    embed.add_field(name='Второе место',
                    value=f"```\nНик:{top2[0]}.\nУровень:{top2[1]}.\nОпыт:{top2[2]}```", inline=False)
    embed.add_field(name='Третье место',
                    value=f"```\nНик:{top3[0]}.\nУровень:{top3[1]}.\nОпыт:{top3[2]}```", inline=False)
    embed.add_field(name='Четвертое место',
                    value=f"```\nНик:{top4[0]}.\nУровень:{top4[1]}.\nОпыт:{top4[2]}```", inline=False)
    embed.add_field(name='Пятое место',
                    value=f"```\nНик:{top5[0]}.\nУровень:{top5[1]}\nОпыт:{top5[2]}```", inline=False)
    await ctx.send(embed=embed)


bot.run('ODM1NTIxNzI4NDgxODUzNDQw.YIQqPw.6f0pj1K4F4NRsLZR2_r4X9teLPI')
