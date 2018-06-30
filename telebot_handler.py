import json
import logging
import re
from telegram import Message, Chat, Update, Bot, User
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler, MessageHandler, Filters
from collections import deque
import uuid
import boto3
import random
import os
import sys


import requests

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))
dynamodb = boto3.resource('dynamodb')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

#Declare all global lists collecting information: project results, token stakes, and responses to Non-TWR questions

index = 0
players = list()
all_stake = list()
project_results = list()
project_name = ['Cindcator', 'Ripple', 'Gnosis']
email_list = list()
twr_game_questions= ['Q1: Which Project has better Team-Dream fit?',
    'Q2: Which Project has better Team-Dream fit?',
    'Q3: Which Project has better Team-Dream fit?',
    'Q4: Which Project has better Team-Dream fit?',
    'Q5: Which Project has better Team-Dream fit?',
    'Q6: Which Project has better Team-Machine fit?',
    'Q7: Which Project has better Team-Machine fit?',
    'Q8: Which Project has better Team-Machine fit?',
    'Q9: Which Project has better Team-Machine fit?',
    'Q10: Which Project has better Team-Machine fit?']

twr_game_photos = ['https://docs.google.com/drawings/d/e/2PACX-1vQ-4jIixGN5iVqdjWg2fft8Er2bYq-yg9QO3-5w7KN5veLoS8gmqqsqFcxYxSKukKAnLKoCLyvlmaFG/pub?w=1335&h=919',
    'https://docs.google.com/drawings/d/e/2PACX-1vRo5cv6s0YhYX4E7FGElWCyOXIXR1aSu_egtaj0RsMzPygUSKOqV_VvHqVejs80Ah5Fi2R9Wu7XhNZo/pub?w=1335&h=919',
    'https://docs.google.com/drawings/d/e/2PACX-1vQVRWZURf5XWnNYNfKVBhdBvn2MHrqKgHMxJcBUGkizHuJrRhf7CF6YSBfyk6-ny531sWxUQFThMNZq/pub?w=1335&h=919',
    'https://docs.google.com/drawings/d/e/2PACX-1vRZt5f8H_zLFAxKcaKEqu03NjXECGi8y2ikF0SInZzb2e6m9GJOizHs6Vmzz0w20LQ2zsbtrRCRsPG6/pub?w=1335&h=919',
    'https://docs.google.com/drawings/d/e/2PACX-1vTzDUI_n3Lx7sVcXJ7Bi_GrU0jcMCdsxOcJQ4RR3OSwTM8qkTg-kgbz2jyndqtrNbrVSqotkYv7sYqI/pub?w=1335&h=919',
    'https://docs.google.com/drawings/d/e/2PACX-1vQU1b_JrmQu_xBsbbSJLhhYCAwbtiGPwMp_UZAU6YueWDhluqj4uLlc3hwRnYTBEoZhtYECsWAvS6EN/pub?w=1335&h=919',
    'https://docs.google.com/drawings/d/e/2PACX-1vQd1q688OyshWfJmpLIyqFU26G4Dm2ava_I1IeFrC1x-P8I5_PTZAOeBU0Db8r02icByXIn-2L_EDvW/pub?w=1335&h=919',
    'https://docs.google.com/drawings/d/e/2PACX-1vSbYG0HsKg2qeWZiP2ed7pyrxyoPit_0mDPtKQD_Y1jFr23s6E5Na4COuA4xB3UaewsavuvcPyuYsQf/pub?w=1335&h=919',
    'https://docs.google.com/drawings/d/e/2PACX-1vSfw_SKZbw2oXSN0a6S8MuaA1uOXId4_yYq0lH20Q_dBnjF1-uKqCXxVEBUQAx9LLMsPk1LeRjMQAbu/pub?w=1335&h=919',
    'https://docs.google.com/drawings/d/e/2PACX-1vTzDUI_n3Lx7sVcXJ7Bi_GrU0jcMCdsxOcJQ4RR3OSwTM8qkTg-kgbz2jyndqtrNbrVSqotkYv7sYqI/pub?w=1335&h=919']

airdrop = 150
#non_answers = []
#all_clicks = []
reply_markup_twr = InlineKeyboardMarkup([
[InlineKeyboardButton("Project A", callback_data='Project A'),
InlineKeyboardButton("Project B", callback_data='Project B')]])

def log(event, context):
    table = dynamodb.Table(os.environ['MESSAGES_TABLE'])
    table.put_item(Item=_get_data(event))
    return {"statusCode": 200}

def authorize(event, context):

    message = "Authorization is successful"

    table = dynamodb.Table(os.environ['USERS_TABLE'])
    chat_id = event["message"]["chat"]["id"]
    user_id = event['results']['receive']['user_id']
    data = {"chat_id": chat_id, 'user_id': user_id}
    # send data to your website to auth
    all_data = _get_data(event)
    item = {k: all_data.get(k) for k in ['id', 'first_name', 'last_name', 'username', 'language_code']}

    item.update(data)
    table.put_item(Item=item)

    return {"statusCode": 200, "message": message}


def start(bot, update):
    global players
    name = update.effective_user.first_name
    text = 'Hola Cypherpunk!\nWelcome back, ' + name +'!'+ '\nPlease authenticate using your email id to receive your playing balance:'
    update.message.reply_text(text=text)
    players.append(name)
    #bot.sendMessage(update.message.chat_id, str(update.message.from_user.username))

def email(bot,update):
    global email_list
    email = update.message.text

    text = "Confirm Email and hit sumbit: {}".format(email)
    email_list.append(email)
    update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text="Submit Email", callback_data="startit")]]))
    print (email)


    #update.message.reply_text(update.callback_query.id, text="You have 100 tokens left", show_alert=True, url=None, cache_time=None, timeout=None)
#def project_answers():
    #global project_results


def startit(bot, update):
    chat_id = update.effective_message.chat_id
    query = update.callback_query
    text = "Okay, you have 100 tokens for this game.\n If you have already been allocated startereums in the past, these will be credited to your account after a delay..".format(update.effective_user.first_name)
    update.callback_query.message.reply_text(text=text,reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text="How to Play", callback_data="play")],
                                         [InlineKeyboardButton(text="Start the Game", callback_data="twr_games")]]))



def how_play(bot,update):
    chat_id = update.effective_message.chat_id
    text = "{}, it is quite easy to play (See below) If you understand basic concepts of blockchain and can make smart investment decisions lets start.".format(update.effective_user.first_name)


    update.callback_query.message.reply_text(text=text,reply_markup=InlineKeyboardMarkup(
                                             [[InlineKeyboardButton(text="Start the Game", callback_data="twr_games")]]))
    bot.sendDocument(chat_id=chat_id, document='https://media.giphy.com/media/2Yc0g11QsZ7vqxmzTn/giphy.gif')

def token_stake(bot, update):
    global all_stake
    global airdrop
    global project_results
    reply_markup = ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)])
    total_spent = sum(all_stake)

    token_left = airdrop - total_spent


    text = "Token Left: " + str(token_left) + "\n Please stake tokens for {}".format(update.callback_query.data)

    update.callback_query.message.reply_text(text=text, reply_markup=reply_markup)
    project_results.append(update.callback_query.data)
    print (project_results)
    #bot.answer_callback_query(update.callback_query.id, text="Great pick, {}!".format(update.effective_user.first_name), show_alert=True, url=None, cache_time=None, timeout=None)

def stake_submit(bot, update):
    global all_stake
    token = update.message
    token_value = int(token.text)
    total_spent = sum(all_stake)
    token_left = airdrop - total_spent
    if token_value > token_left:
        update.message.reply_text(text="You don't have enough tokens.\nPlease stake tokens accurately.", reply_markup=InlineKeyboardMarkup(
                                             [[InlineKeyboardButton(text="Stake Again", callback_data="Project")]]))


    #stake = re.findall(r'\d+',token)
    #stake_value = int(stake.group(1))
    else:
        text = "Token Staked {}".format(token_value)

        all_stake.append(token_value)
        update.message.reply_text(text=text,reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text="Next Question", callback_data="twr_games")]]))

    print(all_stake)
 #Insert hide keyboard feature
#def game_list(bot, update):
    #update.message.reply_text("Please pick your next unplayed game from this list- Investment Games: [/game_one], [/game_two], [/game_three], [/game_four], [/game_five], [/game_six], [/game_seven], [/game_eight],[/game_nine], [/game_ten] Optional Verification Games: [/verify_1], [/verify_2], [/verify_3]. Press /submit ONLY after all Investment games are over")


#def button(bot, update):
    #query = update.callback_query
    #bot.edit_message_text(text="For each of the 10 Investment Games it is mandatory to stake tokens between 3-20. Please PRESS /token_stake to stake tokens for your selection: {}".format(query.data),
                      #chat_id=query.message.chat_id,
                      #message_id=query.message.message_id)


#def token_button (bot, update) :

    #bot.answer_callback_query(update.callback_query.id, text="You have 100 tokens left", show_alert=True, url=None, cache_time=None, timeout=None)

def twr_games(bot, update):

    chat_id = update.effective_message.chat_id
    global twr_game_questions
    global twr_game_photos
    global reply_markup_twr
    global index
    text = twr_game_questions[index]
    photo = twr_game_photos[index]
    index = index + 1
    if index == 10:
        update.callback_query.message.reply_text(text='All TWR games are done', reply_markup=InlineKeyboardMarkup(
                                             [[InlineKeyboardButton(text="Submit Final", callback_data="submit_final")]]))
    else:
        bot.send_photo(chat_id, photo=photo)
        update.callback_query.message.reply_text(text=text, reply_markup=reply_markup_twr)


    #print (text)#s, photo)

#def gk1(bot, update):

    #keyboard = [[InlineKeyboardButton("Investors", callback_data='verify_2'),
              #InlineKeyboardButton("Buyers", callback_data='Correct Answer: Accountants')],
              #[InlineKeyboardButton("Accountants", callback_data='Correct Answer: Accountants'),
              #InlineKeyboardButton("Promoters", callback_data='Correct Answer: Accountants')]]

    #reply_markup = InlineKeyboardMarkup(keyboard)


    #update.message.reply_text('First Question: Miners are the __ of the Bitcoin ecosystem', reply_markup=reply_markup)


def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration


def submit_final (bot, update):
    global project_results
    global email_list
    global all_stake
    text= "{} Your entry has been logged into our records".format(update.effective_user.first_name)
    #total spent =
    #total earned =
    #total winnings = TBD
    #Projects Selected:" + str(project_results) +"\nToken Staked:" + str(all_stake)

    update.callback_query.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text="See Top Bets", callback_data="bets")]]))


    print (project_results,all_stake)

def bets(bot, update):
    global project_name
    update.callback_query.message.reply_text(text= 'These are your top 3 bets:\n' + str(project_name))

def hide(bot, update):
    update.message.reply_text("\U0001F44D", reply_markup=ReplyKeyboardRemove())

def help(bot, update):
    update.message.reply_text("tbd")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def unknown(bot, update):
    player = update.effective_user.first_name

    bot.send_message(chat_id=update.message.chat_id, text="Hi {}.".format(player) + "\nPlease enter the correct value, or use /help for more")

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("TELEGRAM_TOKEN")

    updater.dispatcher.add_handler(RegexHandler('\d+', stake_submit))
    updater.dispatcher.add_handler(RegexHandler('(\w+[.|\w])*@(\w+[.])*\w+', email))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(startit, pattern=r"startit"))
    #updater.dispatcher.add_handler(CallbackQueryHandler(email, pattern=r"email_me"))
    updater.dispatcher.add_handler(CallbackQueryHandler(submit_final, pattern=r"submit_final"))
    updater.dispatcher.add_handler(CallbackQueryHandler(bets, pattern=r"bets"))
    updater.dispatcher.add_handler(CallbackQueryHandler(token_stake, pattern=r"Project"))
    updater.dispatcher.add_handler(CallbackQueryHandler(how_play, pattern=r"play"))
    #updater.dispatcher.add_handler(CallbackQueryHandler(stake_submit, pattern=r"st_3"))
    #updater.dispatcher.add_handler(CallbackQueryHandler('gk1', gk1))

    updater.dispatcher.add_handler(CallbackQueryHandler(twr_games, pattern=r"twr_games"))

    #updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    updater.dispatcher.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()



if __name__ == '__main__':
    main()



    """
    END- AAYUSH SRIVASTAVA 
    """
