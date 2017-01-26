#!/usr/bin/python3.5

import argparse
import datetime

import telebot
import webuntis
from telebot import types

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--url', type=str, help='server to connect to', dest='url')
parser.add_argument('-n', '--user-name', type=str, help='user name', dest='user')
parser.add_argument('-p', '--password', type=str, help='password', dest='pw')
parser.add_argument('-s', '--school', type=str, help='schoolname', dest='school')
parser.add_argument('-t', '--token', type=str, help='telegram token', dest='token')
args = parser.parse_args()

bot = telebot.TeleBot(args.token)

print(args.url)

s = webuntis.Session(
	server=args.url,
	username=args.user,
	password=args.pw,
	school=args.school,
	useragent='Pyton Stundenplan pull Script'
)

@bot.message_handler(commands=['list_klass'])
def send_klass(message):
	print(message.from_user.username)
	reply = bot.reply_to(message, list_klass())

@bot.message_handler(commands=['today'])
def send_tday(message):
	print(message.from_user.username)
	markup = types.ForceReply(selective=False)
	reply = bot.reply_to(message, "Klasse?", reply_markup=markup)
	bot.register_next_step_handler(reply, send_stpl_tday)

@bot.message_handler(commands=['tomorrow'])
def send_tmorrow(message):
	print(message.from_user.username)
	markup = types.ForceReply(selective=False)
	reply = bot.reply_to(message, "Klasse?", reply_markup=markup)
	bot.register_next_step_handler(reply, send_stpl_tmorrow)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	print(message.from_user.username)
	bot.send_message(message.chat.id, "Fuer Stundenplan von Heute: /today\nFuer Stundenplan von Morgen: /tomorrow\n"
									  "Fuer eine Liste aller Klassen: /list_klass")

def list_klass():
	try:
		s.login()
		str = ''
		for klasse in s.klassen():
			str += klasse.name + "\n"
		s.logout()
	except Exception as e:
		str = e
	return str

def send_stpl_tday(reply):
	try:
		s.login()
		bot.reply_to(reply, tday(reply.text.upper()))
		s.logout()
	except Exception as e:
		bot.reply_to(reply, e)

def send_stpl_tmorrow(reply):
	try:
		s.login()
		bot.reply_to(reply, tmorrow(reply.text.upper()))
		s.logout()
	except Exception as e:
		bot.reply_to(reply, e)

def period_to_string(per):
	return '' + subjects_to_string(per.subjects) + ', [' + per.start.strftime("%H:%M:%S") + ' - ' + per.end.strftime("%H:%M:%S") + '], [' + teachers_to_string(per.teachers) + '], [' + rooms_to_string(per.rooms) + ']'

def periods_to_string(pers):
	st = ''
	pers = sorted(pers, key=lambda p:p.start)
	per_end = datetime.datetime.now()
	for per in pers:
		if per.code != 'cancelled':
			if per_end < per.start:
				diff = (per.start - per_end)/60
				st += "--- FREI: " + str(int(round(diff.total_seconds()))) + "min ---\n"
			st += period_to_string(per) + "\n"
			per_end = per.end
	st += ''
	return st


def room_to_string(room):
	return '' + room.name + ''


def rooms_to_string(rooml):
	st = ''
	f = 0
	for room in rooml:
		if not f==0:
			st += ', '
		else:
			f=1
		st += room_to_string(room)
	st += ''
	return st

def teacher_to_string(tch):
	return '' + tch.name + ''

def teachers_to_string(tchl):
	st = ''
	f = 0
	for tch in tchl:
		if not f==0:
			st += ', '
		else:
			f=1
		st += teacher_to_string(tch)
	st += ''
	return st

def subject_to_string(sub):
	return '' + sub.name + ''

def subjects_to_string(subl):
	st = '['
	f = 0
	for sub in subl:
		if not f==0:
			st += ', '
		else:
			f=1
		st += subject_to_string(sub)
	st += ']'
	return st

def tmorrow(cname):
	tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
	klasse = s.klassen().filter(name=cname)[0]
	tt = s.timetable(klasse=klasse, start=tomorrow, end=tomorrow)
	tt = [elem for elem in tt if elem.end > datetime.datetime.now()]
	tt = sorted(tt, key=lambda p:p.start)
	return periods_to_string(tt)

def tday(cname):
	today = datetime.date.today()
	klasse = s.klassen().filter(name=cname)[0]
	tt = s.timetable(klasse=klasse, start=today, end=today)
	tt = [elem for elem in tt if elem.end > datetime.datetime.now()]
	tt = sorted(tt, key=lambda p:p.start)
	return periods_to_string(tt)

def pol():
	try:
		bot.polling()
	except Exception as e:
		print(e)
		pol()
pol()
#def klassen_to_string(kla)
	

