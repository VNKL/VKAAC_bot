from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
from models import VkApi
import settings


vk = VkApi(settings.VK_TOKEN)


def _is_user_known(context, update):
    username = update.effective_user.username

    with open('permissions.txt') as file:
        users = file.read().rstrip().split('\n')

    if username not in users:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Я тебя не знаю. Напиши @vnkl_iam. '
                                      'Может быть, он нас познакомит.')
        print(f'!!! @{username} not in permissions')
        return False
    else:
        return True


def start(update, context):
    if _is_user_known(context, update):
        chat_id = update.effective_message.chat_id
        context.bot.send_message(chat_id=chat_id,
                                 text='Привет!\n\n'
                                      'Я могу прислать тебе актуальный на момент запроса размер аудитории слушателей '
                                      'артиста в ВК. Слушатели - это те люди, которые регулярно слушают треки данного '
                                      'артиста. Более конкретно алгоритм сбора такой аудитории ВК не раскрывает, но '
                                      'я заметил, что ее обновление близко к реальному времени.\n\n'
                                      'Округления в размерах аудиторий - так ВК отдает эту информацию\n\n'
                                      'Просто пришли мне имя артиста так, как оно лицензируется в ВК, без ошибок, '
                                      'иначе ничего не найдем.')


def help(update, context):
    if _is_user_known(context, update):
        chat_id = update.effective_message.chat_id
        context.bot.send_message(chat_id=chat_id,
                                 text='Привет!\n\n'
                                      'Я могу прислать тебе актуальный на момент запроса размер аудитории слушателей '
                                      'артиста в ВК. Слушатели - это те люди, которые регулярно слушают треки данного '
                                      'артиста. Более конкретно алгоритм сбора такой аудитории ВК не раскрывает, но '
                                      'я заметил, что ее обновление близко к реальному времени.\n\n'
                                      'Округления в размерах аудиторий - так ВК отдает эту информацию\n\n'
                                      'Просто пришли мне имя артиста так, как оно лицензируется в ВК, без ошибок, '
                                      'иначе ничего не найдем.')


def get_audience_count(update, context):
    if _is_user_known(context, update):
        chat_id = update.effective_message.chat_id
        username = update.effective_user.username
        text = update.message.text

        context.bot.send_message(chat_id=chat_id,
                                 text='Иду за инфой в ВК, это может занять некоторое время. '
                                      'Много нулевых размеров аудиторий означают лаги на стороне ВК')

        audience_count = vk.get_audience_count_by_artist_name_per_socdem(text)

        if audience_count:
            answer_text = _api_response_to_text(audience_count)
            context.bot.send_message(chat_id=chat_id,
                                     text=answer_text,
                                     parse_mode=ParseMode.HTML)
            print(f"@{username} get audience count for '{text}'")
        else:
            context.bot.send_message(chat_id=chat_id,
                                     text=f'В ВК не нашлось артиста с именем "{text}". '
                                          f'Проверь правильность написания его имени')
            print(f"@{username} failed with get audience count for '{text}'")


def _api_response_to_text(response_dict):

    artist_name = list(response_dict.keys())[0]

    text = f'<b>{artist_name}</b>\n\n'

    for socdem, count in response_dict[artist_name].items():
        text += f'<b>{socdem}:</b> {count}\n'

    return text


def main():

    bot = Updater(token=settings.TELEGRAM_TOKEN, request_kwargs=settings.PROXY, use_context=True)
    dp = bot.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(MessageHandler(Filters.text, get_audience_count))

    bot.start_polling()     # Собсно начинаем обращаться к телеге за апдейтами
    bot.idle()              # Означает, что бот работает до принудительной остановки


if __name__ == '__main__':
    main()
