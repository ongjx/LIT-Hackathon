from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
import requests
import json
from SearchObject import *
from cachetools import cached, TTLCache
import logging
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def getLawyersInCategory(bot,update,category,urls):

    ''' get source code for specified category '''
    categorySourceCode = getTermDocumentCode(category, urls)
    
    ''' split lawyers into A and R'''
    lawyers_split_dict = appealVsRespond(categorySourceCode)
    cleaned_data = cleaner(lawyers_split_dict)
    appeal = getLawyersInRespectiveCase(cleaned_data)[0]
    respond = getLawyersInRespectiveCase(cleaned_data)[1]
    
    a_string = "Lawyers that represented Appellants:\n"
    r_string = "Lawyers that represented Respondents:\n"
    
    appeal_list = []
    respond_list = []
    for lawyer in appeal:
        if len(lawyer) > 5 and not ('second' in lawyer and 'for' in lawyer) :
            try:
                rating = str(getRecommendation(lawyer))  
                a_string += rating + '\t\t\t\t' + lawyer + "\n"
                appeal_list.append((rating,lawyer))
            except:
                pass
    appeal_list = sorted(appeal_list, key=lambda x: x[0],reverse=True)
    ap_string = "*Lawyers that represented Appellants:*\n"
    for i in appeal_list[:20]:
        ap_string += i[0] + '\t\t\t\t' + i[1] + '\n'
    # update.message.reply_text(a_string) 
    update.message.reply_text(ap_string,parse_mode='Markdown')
    for lawyer in sorted(respond):
        if len(lawyer) > 5 and 'second' not in lawyer and 'for' not in lawyer and 'second' not in lawyer and 'forth' not in lawyer:
            try:
                rating = str(getRecommendation(lawyer))
                r_string += rating + '\t\t\t\t' + lawyer + "\n"
                respond_list.append((rating,lawyer))
            except:
                pass
    respond_list = sorted(respond_list, key=lambda x: x[0],reverse=True)
    rs_string = "*Lawyers that represented Respondents*:\n"
    for i in respond_list[:20]:
        rs_string += i[0] + '\t\t\t\t' + i[1] + '\n'
    # update.message.reply_text(r_string)
    update.message.reply_text(rs_string,parse_mode='Markdown')


def getCategory(bot,update):
    # update.message.reply_text("Enter topic to search")
    response = update.message.text.replace('/getcategory ', '').lower()
    print('after')
    user_response = response
    if user_response == 'abuses':
        user_response = 'abuse'
    if user_response == 'accident':
        user_response = 'accidents'
    if user_response == 'claim':
        user_response = 'claims'
    if user_response == 'torts':
        user_response = 'tort'
    print('finding all lawyers in', user_response, 'field')
    update.message.reply_text('finding all lawyers in ' + user_response + ' field')
    urlLists = getUrlOfTerm(user_response)
    getLawyersInCategory(bot,update,user_response,urlLists)


def getLawyerInformation(bot,update):
    lawyerName = update.message.text.replace('/getinfo ', '')
    # update.message.reply_text(lawyerName)
    # history = getLawyerHistory(lawyerName)
    expertise = getExpertise(lawyerName)[0]
    side = getExpertise(lawyerName)[1]
    try:
        update.message.reply_text("{} specializes in {} cases and tends to do better when on the {} side.\n\n {}'s current ratings is {}.\n\nThe approximated contract value range should you choose to contract {}'s services is {}".format(lawyerName.title(), expertise.upper(), side.upper(), lawyerName.title(), getRecommendation(lawyerName.title()),lawyerName.title(), getSalary(lawyerName.title())))
    except:
        update.message.reply_text("No user found. Please try again!")

def getHelp(bot,update):
    
    definitions = {
        'Appellant': 'the party who wants to change the current decision of their case',
        'Respondent': 'the party responding to an Appellant',
        'Tort': 'a wrongful act eg. Personal injury',
        'Contract': 'a written or spoken agreement',
        'Accident': 'eg. Motor vehicle accidents',
        'Abuse': 'eg. physical abuse, mental abuse, verbal abuse'
    }

    string = '*Some helpful definitions on legal terms:*\n\n'
    for k,v in definitions.items():
        string += k + ": " + v + '\n\n'
    update.message.reply_text(string, parse_mode='Markdown')

    
def start(bot, update):
    update.message.reply_text(
        "Hello! Welcome to LAWL BOT!\n\nTo search for lawyers from a category: \n/getcategory <category name>\n\nTo get a specific lawyer's info: \n/getinfo <lawyer's name>\n\nThe categories available for search are:\nAbuse\nAccidents\nClaims\nDivorce\nTort\n"
        )

updater = Updater('739214507:AAFDrPsC2dkRSnC8MiWJeZ8cfdp2tkNChTc')

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('category', getLawyersInCategory))
updater.dispatcher.add_handler(CommandHandler('getcategory', getCategory))
updater.dispatcher.add_handler(CommandHandler('getinfo', getLawyerInformation))
updater.dispatcher.add_handler(CommandHandler('help', getHelp))
updater.start_polling()

    