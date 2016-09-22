#!/usr/bin/python2.7

import webuntis
import datetime
import telebot
from telebot import types

bot = telebot.TeleBot("TOKEN")

s = webuntis.Session(
	server='url',
	username='',
	password='',
	school='',
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
	bot.send_message(message.chat.id, "Fuer Stundenplan von Heute: /today\nFuer Stundenplan von Morgen: #/tomorrow\nFuer eine Liste aller Klassen: /list_klass")

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

def room_to_string(rom):
	return '' + rom.name + ''

def rooms_to_string(roml):
	st = ''
	f = 0
	for rom in roml:
		if not f==0:
			st += ', '
		else:
			f=1
		st += room_to_string(rom)
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
	

