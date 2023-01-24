import telebot;
bot = telebot.TeleBot('5626444694:AAHkkLQ0MqR1jACt_M4eVcv55jIUhnQPiN4');


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	print(message.text)
	if message.text == "Привет":
		bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
	elif message.text == "/help":
		bot.send_message(message.from_user.id, "Напиши привет")
	else:
		bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

bot.polling(none_stop=True, interval=0)