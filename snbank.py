import distutils
import commands
from distutils import get
import sqlite3
import os


TOKEN = 'NTYyNDQ3ODExNjAyNDE1NjE5.XUm2GA.qZ2PRD1YYiN-vywnYse0EmF0wZ0'
BOT_PREFIX = '/'

bot = commands.Bot(command_prefix=BOT_PREFIX)

DIR = os.path.dirname(__file__)
db = sqlite3.connect(os.path.join(DIR, "BankAccounts.db"))
SQL = db.cursor()
START_BALANCE = 100.00
C_NAME = "Coins"


@bot.event
async def on_ready():
    print("Logged in as: " + bot.user.name + "\n")


@bot.command(pass_context=True, brief="Shows users balance", aliases=["bal"])
async def balance(ctx):
    USER_ID = ctx.message.author.id
    USER_NAME = str(ctx.message.author)
    SQL.execute('create table if not exists Accounts("Num" integer primary key autoincrement,"user_name" text, "user_id" integer not null, "balance" real)')
    SQL.execute(f'select user_id from Accounts where user_id="{USER_ID}"')
    result_userID = SQL.fetchone()

    if result_userID is None:
        SQL.execute('insert into Accounts(user_name, user_id, balance) values(?,?,?)', (USER_NAME, USER_ID, START_BALANCE))
        db.commit()

    SQL.execute(f'select balance from Accounts where user_id="{USER_ID}"')
    result_userbal = SQL.fetchone()
    await ctx.send(f"{ctx.message.author.mention} has a balance of {result_userbal[0]} {C_NAME}")


@bot.command(pass_context=True, brief="Pay Someone", aliases=["pay", "give"])
async def transfer(ctx, other: discord.Member, amount: int):
    USER_ID = ctx.message.author.id
    USER_NAME = str(ctx.message.author)
    OTHER_ID = other.id
    OTHER_NAME = str(other)

    SQL.execute('create table if not exists Accounts("Num" integer primary key autoincrement,"user_name" text, "user_id" integer not null, "balance" real)')
    SQL.execute(f'select user_id from Accounts where user_id="{USER_ID}"')
    result_userID = SQL.fetchone()
    SQL.execute(f'select user_id from Accounts where user_id="{OTHER_ID}"')
    result_otherID = SQL.fetchone()

    if result_userID is None:
        SQL.execute('insert into Accounts(user_name, user_id, balance) values(?,?,?)', (USER_NAME, USER_ID, START_BALANCE))
        db.commit()
    if result_otherID is None:
        SQL.execute('insert into Accounts(user_name, user_id, balance) values(?,?,?)', (OTHER_NAME, OTHER_ID, START_BALANCE))
        db.commit()

    SQL.execute(f'select balance from Accounts where user_id="{USER_ID}"')
    result_userbal = SQL.fetchone()
    if amount > int(result_userbal[0]):
        await ctx.send(f"{ctx.message.author.mention} does not have that many {C_NAME}")
        return

    SQL.execute('update Accounts set balance = balance - ? where user_id = ?', (amount, USER_ID))
    db.commit()
    SQL.execute('update Accounts set balance = balance + ? where user_id = ?', (amount, OTHER_ID))
    db.commit()

    await ctx.send(f"{ctx.message.author.mention} sent {other.mention} {amount} {C_NAME}")


@bot.command(pass_context=True, brief="list top 10 bank accounts", aliases=["top"])
async def top10(ctx):
    SQL.execute(f"select user_name, balance from Accounts order by balance desc")
    result_top10 = SQL.fetchmany(2)

    embed = discord.Embed(
        colour=discord.Colour.orange()
    )

    embed.set_author(name="Top 10 bank accounts")
    embed.add_field(name="#1", value=f"User: {result_top10[0][0]} Bal: {result_top10[0][1]}", inline=False)
    embed.add_field(name="#2", value=f"User: {result_top10[1][0]} Bal: {result_top10[1][1]}", inline=False)

    await ctx.send(embed=embed)

bot.run(TOKEN)