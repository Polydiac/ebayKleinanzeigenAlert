#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to send timed Telegram messages.

This Bot uses the Application class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

Note:
To use the JobQueue, you must install PTB via
`pip install "python-telegram-bot[job-queue]"`
"""

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import sys
from random import randint
from time import sleep

from sqlalchemy.orm import Session

from ebAlert import create_logger
from ebAlert.crud.base import crud_link, get_session
from ebAlert.crud.post import crud_post
from ebAlert.ebayscrapping import ebayclass
from ebAlert.telegram.telegramclass import telegram


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# Define a few command handlers. These usually take the two arguments update and
# context.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")

async def checkPosts(context: ContextTypes.DEFAULT_TYPE) -> None:
	"""Send the alarm message."""
	job = context.job
	with get_session() as db:
    	links = crud_link.get_all(db=db)
    	if links:
    	    for link_model in links:
    	        # print("Processing link - id: {} - link: {} ".format(link_model.id, link_model.link))
            	post_factory = ebayclass.EbayItemFactory(link_model.link)
            	items = crud_post.add_items_to_db(db=db, items=post_factory.item_list)
            	for item in items:
                    
        			message = f"{item.title}\n\n{item.price} ({item.city})\n\n"
        			url = f'<a href="{item.link}">{item.link}</a>'
                    await context.bot.send_message(job.chat_id, text= message + url)
            	sleep(randint(0, 40)/10)
                		


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)


async def show(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_session() as db:
        text = ""
		links = crud_link.get_all(db) 
        text = ">> List of URLs\n"
        if links:
            for link_model in links:
                text += "{0:<{1}}{2}".format(link_model.id, 8 - len(str(link_model.id)), link_model.link)
		await update.message.reply_text(text)


async def remove(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_session() as db:
        text = ""
        text += ">> Removing link\n"
        if crud_link.remove(db=db, id=context.args[0]):
            text += "<< Link removed"
        else:
            text += "<< No link found"
		await update.message.reply_text(text)
            

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_session() as db:
        text = ""
        text += ">> Clearing database\n"
        crud_post.clear_database(db=db)
		await update.message.reply_text(text)
        

async def url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_session() as db:
        text = ""
        text += ">> Adding url"
        if crud_link.get_by_key(key_mapping={"link": url}, db=db):
            text += "<< Link already exists"
        else:
            crud_link.create({"link": url}, db)
            ebay_items = ebayclass.EbayItemFactory(url)
            crud_post.add_items_to_db(db, ebay_items.item_list)
            text += "<< Link and post added to the database"
		await update.message.reply_text(text)
            
async def go()



def main() -> None:
    """Run bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("TOKEN").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()