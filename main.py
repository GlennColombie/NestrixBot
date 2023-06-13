# This is a sample Python script.
import asyncio
import json
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import jwt
import time
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
secret_key = os.getenv('SECRET_KEY')
jwt_algorithm = os.getenv('JWT_ALGORITHM')

# Dictionary to store the JWT tokens associated with Discord IDs
user_tokens = {}


def validate_jwt_token(token):
    try:
        payload = jwt.decode(token, secret_key, algorithms=jwt_algorithm)
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, "Token is expired. Please log in again."
    except jwt.InvalidTokenError:
        return False, "Invalid token. Please log in again."


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Please try again.")


# @bot.command(
#     brief='Command to login to the Nestrix backend.',
#     help="To use this command, type: !login and provide info when asked."
# )
# async def loginid(ctx):
#     if not isinstance(ctx.channel, discord.DMChannel):
#         await ctx.send("This command can only be used in DMs.")
#         return
#
#     existing_token = user_tokens.get(ctx.author.id)
#     if existing_token:
#         is_valid, token_status = validate_jwt_token(existing_token["token"])
#         if is_valid:
#             await ctx.send("You are already logged in.")
#             return
#         else:
#             if token_status == "Token is expired. Please log in again.":
#                 # remove the expired token
#                 del user_tokens[ctx.author.id]
#             else:
#                 await ctx.send("There was an issue with your session. Please log in again.")
#                 return
#
#     url = f'{api_base_url}/Gebruiker/Login'
#     await ctx.send("Please enter your ID (or type 'STOP' to cancel):")
#     id = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
#     if id.content.upper() == "STOP":
#         await ctx.send("Login cancelled.")
#         return
#
#     await ctx.send("Please enter your code (or type 'STOP' to cancel):")
#     code = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
#     if code.content.upper() == "STOP":
#         await ctx.send("Login cancelled.")
#         return
#
#     data = {"gebruikerId": id.content, "code": code.content}
#     response = requests.post(url, json=data, verify=True)
#     if response.ok:
#         try:
#             result = response.json()
#             user_tokens[ctx.author.id] = {"token": result['token'], "gebruiker": result['gebruiker']}
#             await ctx.send(result['message'])
#         except json.JSONDecodeError as e:
#             await ctx.send(f'Error decoding JSON response: {str(e)}')
#     else:
#         await ctx.send(f'Error {response.status_code}')
#
#
# @bot.command(
#     brief='Command to login to the Nestrix Backend via e-mail.',
#     help="To use this command, type: !loginEmail and provide info when asked"
# )
# async def loginemail(ctx):
#     if not isinstance(ctx.channel, discord.DMChannel):
#         await ctx.send("This can only be used in DMs.")
#         await ctx.author.send("You can only use my commands in direct messages.")
#         return
#
#     existing_token = user_tokens.get(ctx.author.id)
#     if existing_token:
#         is_valid, token_status = validate_jwt_token(existing_token["token"])
#         if is_valid:
#             await ctx.send("You are already logged in.")
#             return
#         else:
#             if token_status == "Token is expired. Please log in again.":
#                 # remove the expired token
#                 del user_tokens[ctx.author.id]
#             else:
#                 await ctx.send("There was an issue with your session. Please log in again.")
#                 return
#
#     url = f'{api_base_url}/Gebruiker/loginEmail'
#     await ctx.send("Please enter your e-mail (or type 'STOP' to cancel):")
#     email = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
#     if email.content.upper() == "STOP":
#         await ctx.send("Login cancelled.")
#         return
#
#     await ctx.send("Please enter your password (or type 'STOP' to cancel):")
#     password = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
#     if password.content.upper() == "STOP":
#         await ctx.send("Login cancelled.")
#         return
#
#     data = {"email": email.content, "password": password.content}
#     response = requests.post(url, json=data, verify=True)
#
#     if response.ok:
#         try:
#             result = response.json()
#             user_tokens[ctx.author.id] = {"token": result['token'], "gebruiker": result['gebruiker']}
#             await ctx.send(result['message'])
#         except json.JSONDecodeError as e:
#             await ctx.send(f'Error decoding JSON response: {str(e)}')
#     else:
#         await ctx.send(f'Error {response.status_code}')


@bot.command(
    brief='Command to login to the Nestrix Backend.',
    help="To use this command, type: !login and provide info when asked."
)
async def login(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return

    existing_token = user_tokens.get(ctx.author.id)
    if existing_token:
        is_valid, token_status = validate_jwt_token(existing_token["token"])
        if is_valid:
            await ctx.send("You are already logged in.")
            return
        else:
            if token_status == "Token is expired. Please log in again.":
                # remove the expired token
                del user_tokens[ctx.author.id]
            else:
                await ctx.send("There was an issue with your session. Please log in again.")
                return

    await ctx.send("Select login method: Type 'ID' for ID login or 'EMAIL' for Email login (or type 'STOP' to cancel):")
    method = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if method.content.upper() == "STOP":
        await ctx.send("Login cancelled.")
        return

    if method.content.upper() == "ID":
        url = f'{api_base_url}/Gebruiker/Login'
        await ctx.send("Please enter your ID (or type 'STOP' to cancel):")
        id = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if id.content.upper() == "STOP":
            await ctx.send("Login cancelled.")
            return

        await ctx.send("Please enter your code (or type 'STOP' to cancel):")
        code = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if code.content.upper() == "STOP":
            await ctx.send("Login cancelled.")
            return

        data = {"gebruikerId": id.content, "code": code.content}

    elif method.content.upper() == "EMAIL":
        url = f'{api_base_url}/Gebruiker/loginEmail'
        await ctx.send("Please enter your e-mail (or type 'STOP' to cancel):")
        email = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if email.content.upper() == "STOP":
            await ctx.send("Login cancelled.")
            return

        await ctx.send("Please enter your password (or type 'STOP' to cancel):")
        password = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if password.content.upper() == "STOP":
            await ctx.send("Login cancelled.")
            return

        data = {"email": email.content, "password": password.content}

    else:
        await ctx.send("Invalid method.")
        return

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


async def get_rekening(ctx, rekening_iban, depth=0):
    url = f'{api_base_url}/Rekening/{rekening_iban}?depth={depth}'
    response = requests.get(url)

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
    brief="Get information about a Rekening by ID and an optional depth for transactions.",
    help="To use this command, type: !get <ID> <depth: optional> "
)
async def get(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("This command can only be used in DMs.")
        return

    token = user_tokens.get(ctx.author.id)
    if not token:
        await ctx.send("You need to log in first.")
        return None

    # Validate the JWT token
    is_valid, message = validate_jwt_token(token["token"])
    if not is_valid:
        await ctx.send(message)
        return None

    await ctx.send("Please enter the IBAN (or type 'STOP' to cancel):")
    iban = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if iban.content.upper() == "STOP":
        await ctx.send("request cancelled.")
        return

    await ctx.send("Please enter the depth of transactions or enter 0 if none (or type 'STOP' to cancel):")
    depth = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if depth.content.upper() == "STOP":
        await ctx.send("Request cancelled.")
        return

    rekening = await get_rekening(ctx, iban.content, depth.content)
    if rekening:
        # Customize the output message based on the received Rekening data.
        rekening_info = rekening["gebruiker"]
        if rekening_info['id'] != token['gebruiker']['id']:
            await ctx.send("Unauthorized.")
            return None
        else:
            transaction_types = {0: "Inkomend", 1: "Uitgaand"}
            adres_info = rekening_info["adres"]
            embed = discord.Embed(title="Rekening Information", color=0x00ff00)
            embed.add_field(name="Rekening ID", value=rekening['rekeningnummer'], inline=False)
            embed.add_field(name="Rekening Type", value=rekening['rekeningType'], inline=False)
            embed.add_field(name="Kredietlimiet", value=rekening['kredietLimiet'], inline=False)
            embed.add_field(name="Saldo", value=rekening['saldo'], inline=False)
            embed.add_field(name="Currency", value=rekening['currency'], inline=False)

            embed.add_field(name="Gebruiker ID", value=rekening_info['id'], inline=False)
            embed.add_field(name="Naam", value=f"{rekening_info['voornaam']} {rekening_info['familienaam']}",
                            inline=False)
            embed.add_field(name="Email", value=rekening_info['email'], inline=False)
            embed.add_field(name="Telefoonnummer", value=rekening_info['telefoonnummer'], inline=False)
            embed.add_field(name="Geboortedatum", value=rekening_info['geboortedatum'], inline=False)

            embed.add_field(name="Adres",
                            value=f"{adres_info['straat']} {adres_info['huisnummer']}, {adres_info['postcode']}, {adres_info['gemeente']}, {adres_info['land']}",
                            inline=False)

            if depth.content.isdigit() and int(depth.content) > 0:
                transacties = rekening["transacties"]
                if transacties:
                    for i, transactie in enumerate(transacties[:int(depth.content)]):
                        transactie_type = transaction_types.get(transactie['transactieType'], 'Unknown')
                        embed.add_field(name=f"Transactie {i + 1}", value=f"ID: {transactie['transactieId']}\n"
                                                                          f"Bedrag: {transactie['bedrag']}\n"
                                                                          f"Datum: {transactie['datum']}\n"
                                                                          f"Omschrijving: {transactie['omschrijving']}\n"
                                                                          f"Type: {transactie_type}", inline=False)

            await ctx.send(embed=embed)
            # response = (
            #     f"Rekening Information:\n"
            #     f"Rekening ID: {rekening['rekeningnummer']}\n"
            #     f"Rekening Type: {rekening['rekeningType']}\n"
            #     f"Kredietlimiet: {rekening['kredietLimiet']}\n"
            #     f"Saldo: {rekening['saldo']}\n"
            #     f"Currency: {rekening['currency']}\n\n"
            #     f"Gebruiker Information:\n"
            #     f"ID: {rekening_info['id']}\n"
            #     f"Naam: {rekening_info['voornaam']} {rekening_info['familienaam']}\n"
            #     f"Email: {rekening_info['email']}\n"
            #     f"Telefoonnummer: {rekening_info['telefoonnummer']}\n"
            #     f"Geboortedatum: {rekening_info['geboortedatum']}\n\n"
            #     f"Adres Information:\n"
            #     f"Straat: {adres_info['straat']} {adres_info['huisnummer']}\n"
            #     f"Postcode: {adres_info['postcode']}\n"
            #     f"Gemeente: {adres_info['gemeente']}\n"
            #     f"Land: {adres_info['land']}"
            # )
            #
            # if depth.content.isdigit() and int(depth.content) > 0:
            #     transacties = rekening["transacties"]
            #     if transacties:
            #         response += "\n\nTransacties:\n"
            #         for transactie in transacties[:int(depth.content)]:
            #             transactie_type = transaction_types.get(transactie['transactieType'], 'Unknown')
            #             response += (
            #                 f"\nTransactie ID: {transactie['transactieId']}\n"
            #                 f"Bedrag: {transactie['bedrag']}\n"
            #                 f"Datum: {transactie['datum']}\n"
            #                 f"Omschrijving: {transactie['omschrijving']}\n"
            #                 f"Transactie Type: {transactie_type}\n"
            #             )
            #
            # await ctx.send(response)


@bot.command(
    brief="Transfer money between two Rekening accounts.",
    help="To use this command, type: !transfer <sender> <recipient> <amount> <currency> <description: optional>"
)
async def transfer(ctx):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.author.send("You can only use my commands in direct messages.")
        return

    token = user_tokens.get(ctx.author.id)
    if not token:
        await ctx.send("You need to log in first.")
        return

    # Validate the JWT token
    is_valid, validation_message = validate_jwt_token(token["token"])
    if not is_valid:
        await ctx.send(validation_message)
        return None

    await ctx.send("Please enter the sender Rekening IBAN (or type 'STOP' to cancel):")
    from_iban = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if from_iban.content.upper() == "STOP":
        await ctx.send("Transfer cancelled.")
        return

    await ctx.send("Please enter the recipient Rekening IBAN (or type 'STOP' to cancel):")
    to_iban = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if to_iban.content.upper() == "STOP":
        await ctx.send("Transfer cancelled.")
        return

    await ctx.send("Please enter the amount to transfer (or type 'STOP' to cancel):")
    amount_message = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if amount_message.content.upper() == "STOP":
        await ctx.send("Transfer cancelled.")
        return

    amount = float(amount_message.content)
    if amount <= 0:
        await ctx.send("Amount must be greater than 0.")
        return

    await ctx.send("Please enter the currency as <XXX>(or type 'STOP' to cancel):")
    currency = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if currency.content.upper() == "STOP":
        await ctx.send("Transfer cancelled.")
        return

    await ctx.send("Please enter the transfer description (or type 'SKIP' to skip):")
    description_message = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    description = None
    if description_message.content.upper() != "SKIP":
        description = description_message.content

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    url = f'{api_base_url}/Rekening/transactie'
    data = {
        "from": from_iban.content,
        "to": to_iban.content,
        "amount": amount,
        "currency": currency.content,
        "description": description
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

    token = user_tokens.get(ctx.author.id)
    if not token:
        await ctx.send("You need to log in first.")
        return

    # Validate the JWT token
    is_valid, validation_message = validate_jwt_token(token["token"])
    if not is_valid:
        await ctx.send(validation_message)
        return None

    gebruiker = token["gebruiker"]

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

    token = user_tokens.get(ctx.author.id)
    if not token:
        await ctx.send("You need to log in first.")
        return

    # Validate the JWT token
    is_valid, validation_message = validate_jwt_token(token["token"])
    if not is_valid:
        await ctx.send(validation_message)
        return None

    gebruiker = token["gebruiker"]

    # Function to ask the user for input and check for "STOP"
    async def ask_for_input(prompt):
        while True:
            await ctx.send(prompt)
            inputresponse = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
            if inputresponse.content.upper() == 'STOP':
                return None
            if inputresponse.content:  # Here you can add more conditions to check the validity of the response
                return inputresponse.content
            await ctx.send("Invalid input. Please try again or type 'STOP' to cancel.")

    accounttype = await ask_for_input("Please enter the account type you'd like to make:")
    if accounttype is None:
        return

    iban = await ask_for_input("Please enter a valid IBAN:")
    if iban is None:
        return

    credit = await ask_for_input("Please enter the credit you'd like:")
    if credit is None:
        return

    currency = await ask_for_input("Please enter the desired currency, in capitalized <XXX> format:")
    if currency is None:
        return

    url = f'{api_base_url}/Rekening'
    data = {
        "gebruikerId": gebruiker['id'],
        "rekeningType": int(accounttype),
        "iban": iban,
        "kredietLimiet": credit,
        "currency": currency
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.post(url, json=data, headers=headers)
    print(response.content)
    if response.ok:
        response_data = response.json()
        account_info = response_data['rekeningnummer']
        account_type = response_data['rekeningType']
        account_credit = response_data['kredietLimiet']
        account_currency = response_data['currency']
        account_iban = response_data['iban']

        user_firstname = response_data['gebruiker']['voornaam']
        user_lastname = response_data['gebruiker']['familienaam']
        user_email = response_data['gebruiker']['email']

        await ctx.send(
            f"Account creation successful! 🎉\n"
            f"\nDetails:\n"
            f"Account Number: {account_info}\n"
            f"IBAN: {account_iban}\n"
            f"Account Type: {account_type}\n"
            f"Credit Limit: {account_credit} {account_currency}\n"
            f"\nUser Details:\n"
            f"Name: {user_firstname} {user_lastname}\n"
            f"Email: {user_email}\n"
            f"\nHappy banking!"
        )
    else:
        await ctx.send("Sorry, something went wrong with creating your account. Please try again.")


bot.run(discord_token)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
