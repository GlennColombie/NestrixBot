# This is a sample Python script.
import json
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import discord
import requests
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

discord_token = os.getenv('DISCORD_TOKEN')
api_base_url = os.getenv('API_BASE_URL')

# Dictionary to store the JWT tokens associated with Discord IDs
user_tokens = {}


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Please try again.")


@bot.command(
    brief='Command to login to the Nestrix backend.',
    help="To use this command, type: !login and provide info when asked."
)
async def loginid(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return

    url = f'{api_base_url}/Gebruiker/Login'
    await ctx.send("Please enter your ID:")
    id = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    await ctx.send("Please enter your code:")
    code = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    data = {"gebruikerId": id.content, "code": code.content}
    response = requests.post(url, json=data, verify=True)
    if response.ok:
        try:
            result = response.json()
            user_tokens[ctx.author.id] = {"token": result['token'], "gebruiker": result['gebruiker']}
            await ctx.send(result['message'])
        except json.JSONDecodeError as e:
            await ctx.send(f'Error decoding JSON response: {str(e)}')
    else:
        await ctx.send(f'Error {response.status_code}')


@bot.command(
    brief='Command to login to the Nestrix Backend via e-mail.',
    help="To use this command, type: !loginEmail and provide info when asked"
)
async def loginemail(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return

    url = f'{api_base_url}/Gebruiker/loginEmail'
    await ctx.send("Please enter your e-mail:")
    email = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    await ctx.send("Please enter your password:")
    password = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    data = {"email": email.content, "password": password.content}
    response = requests.post(url, json=data, verify=True)
    if response.ok:
        try:
            result = response.json()
            user_tokens[ctx.author.id] = {"token": result['token'], "gebruiker": result['gebruiker']}
            await ctx.send(result['message'])
        except json.JSONDecodeError as e:
            await ctx.send(f'Error decoding JSON response: {str(e)}')
    else:
        await ctx.send(f'Error {response.status_code}')


async def get_rekening(ctx, rekening_id, discord_id):
    token = user_tokens.get(discord_id)
    if not token:
        await ctx.send("You need to log in first.")
        return None

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    url = f'{api_base_url}/Rekening/{rekening_id}'
    response = requests.get(url, headers=headers)

    if response.ok:
        try:
            rekening = response.json()
            return rekening
        except json.JSONDecodeError as e:
            await ctx.send(f'Error decoding JSON response: {str(e)}')
            return None
    else:
        await ctx.send(f'Error {response.status_code}: {response.text}')
        return None


@bot.command(
    brief="Get information about a Rekening by ID.",
    help="To use this command, type: !get <ID>"
)
async def get(ctx, rekening_id: str):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return

    if not rekening_id:
        await ctx.send("Please provide a Rekening ID.")
        return

    rekening = await get_rekening(ctx, rekening_id, ctx.author.id)
    if rekening:
        # Customize the output message based on the received Rekening data.
        rekening_info = rekening["gebruiker"]
        adres_info = rekening_info["adres"]

        response = (
            f"Rekening Information:\n"
            f"Rekening ID: {rekening['rekeningnummer']}\n"
            f"Rekening Type: {rekening['rekeningType']}\n"
            f"Kredietlimiet: {rekening['kredietLimiet']}\n"
            f"Saldo: {rekening['saldo']}\n"
            f"Currency: {rekening['currency']}\n\n"
            f"Gebruiker Information:\n"
            f"ID: {rekening_info['id']}\n"
            f"Naam: {rekening_info['voornaam']} {rekening_info['familienaam']}\n"
            f"Email: {rekening_info['email']}\n"
            f"Telefoonnummer: {rekening_info['telefoonnummer']}\n"
            f"Geboortedatum: {rekening_info['geboortedatum']}\n\n"
            f"Adres Information:\n"
            f"Straat: {adres_info['straat']} {adres_info['huisnummer']}\n"
            f"Postcode: {adres_info['postcode']}\n"
            f"Gemeente: {adres_info['gemeente']}\n"
            f"Land: {adres_info['land']}"
        )

        await ctx.send(response)


@bot.command(
    brief="Transfer money between two Rekening accounts.",
    help="To use this command, type: !transfer <sender> <recipient> <amount> <currency> <description: optional>"
)
async def transfer(ctx, from_id: str, to_id: str, amount: float, currency: str, description: str = None):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return

    if not (from_id and to_id and amount and currency):
        await ctx.send("Please provide From Rekening ID, To Rekening ID, Amount and Currency(EUR,USD,...)")
        return

    if amount <= 0:
        await ctx.send("Amount must be greater than 0.")
        return

    token = user_tokens.get(ctx.author.id)
    if not token:
        await ctx.send("You need to log in first.")
        return

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    url = f'{api_base_url}/Rekening/transactie'
    data = {
        "From": from_id,
        "To": to_id,
        "Amount": amount,
        "Currency": currency,
        "Description": description
    }
    response = requests.post(url, json=data, headers=headers)

    if response.ok:
        await ctx.send("Transfer successful.")
    else:
        await ctx.send(f'Error {response.status_code}: {response.text}')


@bot.command(
    brief='Command to get the current logged-in user information.',
    help="To use this command, type: !info."
)
async def info(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return

    user_info = user_tokens.get(ctx.author.id)
    if not user_info:
        await ctx.send("You need to log in first.")
        return

    gebruiker = user_info["gebruiker"]

    response_message = "User Information:\n"
    response_message += f"ID: {gebruiker['id']}\n"

    if gebruiker['voornaam'] is not None and gebruiker['familienaam'] is not None:
        response_message += f"Naam: {gebruiker['voornaam']} {gebruiker['familienaam']}\n"

    if gebruiker['email'] is not None:
        response_message += f"Email: {gebruiker['email']}\n"

    if gebruiker['telefoonnummer'] is not None:
        response_message += f"Telefoonnummer: {gebruiker['telefoonnummer']}\n"

    if gebruiker['geboortedatum'] is not None and gebruiker['geboortedatum'] != '0001-01-01T00:00:00':
        response_message += f"Geboortedatum: {gebruiker['geboortedatum']}\n"

    if gebruiker['adres'] is not None:
        response_message += "\nAdres Information:\n"

        if 'straat' in gebruiker['adres'] and 'huisnummer' in gebruiker['adres']:
            response_message += f"Straat: {gebruiker['adres']['straat']} {gebruiker['adres']['huisnummer']}\n"

        if 'postcode' in gebruiker['adres']:
            response_message += f"Postcode: {gebruiker['adres']['postcode']}\n"

        if 'gemeente' in gebruiker['adres']:
            response_message += f"Gemeente: {gebruiker['adres']['gemeente']}\n"

        if 'land' in gebruiker['adres']:
            response_message += f"Land: {gebruiker['adres']['land']}"

    await ctx.send(response_message)


@bot.command(
    brief='Command to add an account',
    help="To use this command, type: !add <accounttype: 0/1 (zichtrekening/spaarrekening)> <IBAN> <credit> <currency>"
)
async def add(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return

    user_info = user_tokens.get(ctx.author.id)
    if not user_info:
        await ctx.send("You need to log in first.")
        return

    data={
        "RekeningType":
    }

bot.run(discord_token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
