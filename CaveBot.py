import telegram.botapi.botbuilder as botbuilder
import pexpect
import signal
import sys

from GameProcess import GameProcess
from ProcessList import ProcessList
#
# Global variables
#
global games

#
# Helper functions
#

# Display an help text
def help_text(update):
	return "@maioadventuretest_bot - Play Colossal Cave Adventure!\n" \
		"This is the list of commands:\n\n" \
		"/restart - Starts a new game\n" \
		"/help - Display this help text.\n" \
		"command - send a command ingame (Eg. look)\n\n"

# Cleanup and save game before quitting
def exitGracefully(signal, frame):
	global games
	
	for proc in games.getAll().values():
		proc.save()
		proc.quit()
		
	games.stopGC()
	
	print("GOODBYE.")
	sys.exit(0)

# Start a new game
def start(update):
	global games
	
	game = games.getGame(update.chat.id)
	if game == None:
		return "Sorry, the server is busy. Try again later."
	
	return game.getOutput()

# process user input
def process_input(update):
	global games

	game = games.getGame(update.chat.id)
	if game == None:
		return "Sorry, the server is busy. Try again later."

	return game.execCmd(update.text)
	#if len(update.text) >= 7:
	#	return game.execCmd(update.text[6:])
	#else:
	#	return game.getOutput()

# Start a new game
def restart(update):
	game = games.getGame(update.chat.id)
	game.restart()
	return game.getOutput()

def catchall(update):
	if update.text.lower() == "/start":
		return help_text(update) # start(update)
	elif update.text.lower() == "/help":
		return help_text(update)
	elif update.text.lower() == "/restart":
		return restart(update)
	return process_input(update)

def catchalltrigger(update):
	return True

# Log received messages
def logger(update):
	print("%i > %s" % (update.chat.id, update.text))

#
# MAIN:
#
if __name__ == "__main__":
	# create games list
	global games
	games = ProcessList()
	# intercept SIGINT (Ctrl+C) and SIGTERM
	signal.signal(signal.SIGINT, exitGracefully)
	signal.signal(signal.SIGTERM, exitGracefully)
	# create bot
	bot = botbuilder.BotBuilder(apikey_file="apikey.txt")
	# bot actions
	bot.do_when(lambda update: (True), logger, botbuilder.DO_NOT_CONSUME)
	#bot.send_message_when("start", start)
	#bot.send_message_when("cave", process_input)
	#bot.send_message_when("help", help_text)
	#bot.send_message_when("restart", restart)
	bot.send_message_when(catchalltrigger, catchall)

	# create bot and launch it
	bot.build().start()
