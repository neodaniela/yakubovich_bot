import random
import typing
from kts_backend.base.base_accessor import BaseAccessor
from kts_backend.quiz.models import Game
from kts_backend.store.bot.poller import Poller
from kts_backend.store.img.yakubovich_photos import STICKER_ON_THE_CALL, STICKER_SILENCE_IN_STUDIO, \
    STICKER_HELLO_MY_FRIEND, IMG_GOODBYE, IMG_YAKUB_IS_COMING, STICKER_HOLD_IT, STICKER_UVY_I_AKH, STICKER_POTRACHENO, \
    STICKER_POZOR, STICKER_SOOBRAJAESH, STICKER_WHOLE_WORD, STICKER_DALADNA, STICKER_VO, STICKER_HOT, STICKER_ULET, \
    STICKER_LIKE, STICKER_WHAT_DO_YOU_SAY, STICKER_SMILE
from kts_backend.store.telegram_api.api import TgClient
from kts_backend.store.telegram_api.dataclasses import UpdateObj
from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
)

if typing.TYPE_CHECKING:
    from kts_backend.web.app import Application


class BotManager(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.token = self.app.config.bot.token
        self.bot_username = self.app.config.bot.username
        self.poller = Poller(self.token, app)
        self.tg_client = TgClient(self.token)

    async def start(self):
        await self.poller.start()
        self.logger.info("Bot start")

    async def stop(self):
        await self.poller.stop()

    async def connect(self, app: "Application"):
        await self.start()

    async def disconnect(self, app: "Application"):
        await self.stop()

    async def handle_update(self, update: UpdateObj):
        print(update)

        if update.my_chat_member:
            chat_id = update.my_chat_member.chat.id
            updated_username = update.my_chat_member.new_chat_member.user.username

            # определяется момент, когда бот назначен администратором в чате
            updated_status = update.my_chat_member.new_chat_member.status
            if (
                    updated_username == self.bot_username
                    and updated_status == "administrator"
            ):
                # выводится командное меню для получения информации
                await self.tg_client.send_photo(
                    chat_id=chat_id,
                    photo=IMG_YAKUB_IS_COMING
                )
                reply_keyboard = [["/start"], ["/stop"], ["/stats"]]
                markup = ReplyKeyboardMarkup(
                    keyboard=reply_keyboard,
                    one_time_keyboard=True,
                    resize_keyboard=True
                )
                text = (
                    f"🤑ДАЛАДНО! Леонид Якубович вошёл в чат!: \n"
                    f"Смотрите, что мы с вами тут можем делать: \n"
                    f"/start - ❤️начать игру с Якубовичем.\n"
                    f"/stop - 💔прервать игру с Якубовичем\n"
                    f"/stats - 💛получить информацию о последних пяти играх в этом чате."
                )

                await self.tg_client.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=markup
                )

        if update.message:
            chat_id = update.message.chat.id
            user_id = update.message.from_.id
            username = update.message.from_.username
            first_name = update.message.from_.first_name
            text_msg = update.message.text
            game = await self.app.store.quizzes.get_active_game_by_chat_id(
                chat_id=chat_id
            )

            if update.message.chat.type == "private":
                # в приватном чате в ответ на любую команду выводится сообщение,
                # о необходимости добавления бота в чат
                text = '🤷Я не могу запустить капитал-шоу "Поле чудес" в приватной беседе, ' \
                       'ведь для игры нужно как минимум два игрока! \n' \
                       'Чтобы покрутить барабан и пообщаться с Якубовичем, добавь меня в чат со своими друзьями, ' \
                       'и, самое главное - дай мне права администратора.' \
                       '\n\nДавай же, я жду!'

                await self.tg_client.send_message(
                    chat_id=chat_id,
                    text=text
                )
                await self.tg_client.send_sticker(
                    chat_id=chat_id,
                    sticker=STICKER_ON_THE_CALL
                )

            else:
                # по команде /start запускается функция предварительной настройки игры
                # её функционал описан ниже
                if update.message.text == "/start" or update.message.text == "/start@leonid_yakubovich_bot":
                    await self.start_session(
                        chat_id=chat_id,
                        user_id=user_id,
                        username=username,
                        first_name=first_name
                    )

                # по команде /stop запускается функция завершения игры
                # её функционал описан ниже
                elif update.message.text == "/stop" or update.message.text == "/stop@leonid_yakubovich_bot":
                    await self.stop_game(
                        chat_id=chat_id
                    )

                # по команде /stats выводится информация о последних пяти играх в чате
                elif update.message.text == "/stats" or update.message.text == "/stats@leonid_yakubovich_bot":
                    games = await self.app.store.quizzes.get_game_stats()
                    result = "⚽️Игр в этом чате ещё не было"

                    if games:
                        result = ""
                        for game in games:
                            winner_name = "Якубович (никто его не победил)"
                            if game.winner:
                                winner = await self.app.store.quizzes.get_player(
                                    tg_id=game.winner
                                )
                                winner_name = winner.first_name
                            text = (
                                f"⭐️⭐️⭐️Информация об игре {game.id}: \n"
                                f"⏰Старт игры: {game.created_at.strftime('%Y-%m-%d %H:%M:%S')} "
                                f"(часовой пояс не учтен)\n"
                                f"🥇Победитель: {winner_name}\n"
                                f"⚽️Игроки: \n"
                            )
                            for player in game.players:
                                text += f"@{player.username} \n"

                            result += f"{text} \n"

                    await self.tg_client.send_message(
                        chat_id=chat_id,
                        text=result
                    )
                    await self.tg_client.send_sticker(
                        chat_id=chat_id,
                        sticker=STICKER_HOLD_IT
                    )

                # если не пройдена игровая подготовка и игра не запущена, бот слушает только команды
                # и только если началась игра и игрок может начать отправлять ответы, бот начинает случать всё
                elif game and game.move:
                    # это сделано для того, чтобы бот не отвечал на свои же сообщения
                    if username == self.bot_username:
                        pass
                    else:
                        # ниже написана реализация метода, который проверяет, какой игрок ходит в данный момент
                        # и ругает игроков, если они пытаются отправлять что-то не в свой ход.
                        # эта ветка запускается для игрока, который ходит в свой ход
                        if await self.check_user_turn(
                                game=game,
                                chat_id=chat_id,
                                username=username
                        ):
                            question = await self.app.store.quizzes.get_question_by_id(
                                question_id=game.question_id
                            )

                            # проверяется флаг is_whole_word, который говорит о том,
                            # собирается ли игрок угадать всё слово сразу
                            if game.is_whole_word:
                                # для простоты ответ в базе всегда записан в верхнем регистре,
                                # и сообщение игрока тоже приводится к верхнему регистру
                                if question.answer == text_msg.upper():
                                    await self.set_winner(
                                        chat_id=chat_id,
                                        game_id=game.id,
                                        user_id=user_id,
                                        username=username,
                                        first_name=first_name
                                    )

                                else:
                                    await self.app.store.quizzes.is_whole_word_state(
                                        game_id=game.id,
                                        state=False
                                    )
                                    await self.tg_client.send_sticker(
                                        chat_id=chat_id,
                                        sticker=STICKER_UVY_I_AKH
                                    )
                                    text = f"🙈НЕПРАВИЛЬНО! @{username}, {first_name}, выбывает из игры!"
                                    await self.tg_client.send_message(
                                        chat_id=chat_id,
                                        text=text
                                    )
                                    await self.app.store.quizzes.remove_player_game_link(game.id, user_id)
                                    await self.next_move(chat_id, True)

                            # ветка, где игрок гадает по буквам
                            else:
                                letter = text_msg.upper()

                                # ветка, если игрок прислал больше одной буквы
                                if len(letter) != 1:
                                    await self.tg_client.send_sticker(
                                        chat_id=chat_id,
                                        sticker=STICKER_POTRACHENO
                                    )
                                    text = f"🙈Это не буква!🙈"
                                    await self.tg_client.send_message(
                                        chat_id=chat_id,
                                        text=text
                                    )
                                    await self.next_move(
                                        chat_id=chat_id,
                                        is_next_player=True
                                    )

                                # ветка, если игрок прислал букву, которую уже называли
                                elif letter in game.played_letters:
                                    await self.tg_client.send_sticker(
                                        chat_id=chat_id,
                                        sticker=STICKER_POZOR
                                    )
                                    text = f"🙈Такую букву уже называли!🙈"
                                    await self.tg_client.send_message(
                                        chat_id=chat_id,
                                        text=text
                                    )
                                    await self.next_move(
                                        chat_id=chat_id,
                                        is_next_player=True
                                    )

                                # ветка, где игрок прислал один неназванный символ
                                # TODO: проверять, что это именно буква, а не цифра, символ и так далее
                                else:
                                    # названая буква (символ) записывается в модель игры в базе как использованная
                                    letters_array = game.played_letters
                                    letters_array.append(letter)
                                    await self.app.store.quizzes.add_letter(
                                        game_id=game.id,
                                        letters_array=letters_array
                                    )

                                    # ветка, если буква правильная
                                    if letter in question.answer:
                                        text = f"Что вы говорите, {first_name}!\n" \
                                               f"Откройте нам букву \"{text_msg.upper()}\"!"
                                        await self.tg_client.send_message(
                                            chat_id=chat_id,
                                            text=text
                                        )
                                        stickers = [
                                            STICKER_SOOBRAJAESH,
                                            STICKER_VO,
                                            STICKER_HOT,
                                            STICKER_ULET,
                                            STICKER_LIKE,
                                            STICKER_WHAT_DO_YOU_SAY,
                                            STICKER_SMILE
                                        ]
                                        rand = random.randint(0, len(stickers) - 1)
                                        await self.tg_client.send_sticker(
                                            chat_id=chat_id,
                                            sticker=stickers[rand]
                                        )

                                        # перерисовывается маска в запиненном сообщении
                                        mask = ''
                                        for i in range(len(question.answer)):
                                            if question.answer[i] in letters_array:
                                                mask += question.answer[i]
                                            else:
                                                mask += '✳️'

                                        # ветка, если это была последняя буква в слове, победа, завершение игры
                                        if mask == question.answer:
                                            await self.tg_client.send_sticker(
                                                chat_id=chat_id,
                                                sticker=STICKER_DALADNA
                                            )
                                            text = f"Да ладна, {first_name}!\n" \
                                                   f"Вы же собрали слово полностью!"
                                            await self.tg_client.send_message(
                                                chat_id=chat_id,
                                                text=text
                                            )
                                            await self.set_winner(
                                                chat_id=chat_id,
                                                game_id=game.id,
                                                user_id=user_id,
                                                username=username,
                                                first_name=first_name
                                            )
                                        else:
                                            text = f"{mask}\n{question.title} "
                                            await self.tg_client.edit_message_text(
                                                chat_id=chat_id,
                                                message_id=game.pinned_message_id,
                                                text=text
                                            )
                                            await self.next_move(
                                                chat_id=chat_id,
                                                is_next_player=False
                                            )
                                    else:
                                        text = f"Такой буквы нет"
                                        await self.tg_client.send_message(
                                            chat_id, text=text
                                        )
                                        await self.next_move(
                                            chat_id=chat_id,
                                            is_next_player=True
                                        )

        # обработка кликов по кнопкам
        if update.callback_query:
            chat_id = update.callback_query.message.chat.id
            user_id = update.callback_query.from_.id
            username = update.callback_query.from_.username
            first_name = update.callback_query.from_.first_name
            text_msg = update.callback_query.message.text
            data = update.callback_query.data
            message_id = update.callback_query.message.message_id
            game = await self.app.store.quizzes.get_active_game_by_chat_id(
                chat_id=chat_id
            )
            question = await self.app.store.quizzes.get_question_by_id(
                question_id=game.question_id
            )
            mask = "✳️" * len(question.answer)

            # обрабатывается клик на кнопку "Присоединиться к игре"
            if data == "/add_to_game":
                # предупреждение, если игрок уже добавлен
                if await self.app.store.quizzes.is_player_added(
                        game_id=game.id,
                        player_id=user_id
                ):
                    text = f"{first_name}, вы уже в игре!"
                    await self.tg_client.send_message(
                        chat_id=chat_id,
                        text=text
                    )
                else:
                    # проверяется, впервые ли игрок играет с Якубовичем, если да - он записывается в базу
                    if not await self.app.store.quizzes.get_player(user_id):
                        await self.app.store.quizzes.add_player(
                            player_id=user_id,
                            player_username=username,
                            player_firstname=first_name
                        )

                    # добавление связи между игроком и конкретной игрой
                    await self.app.store.quizzes.add_player_game_link(
                        game_id=game.id,
                        player_id=user_id
                    )

                    # редактируется сообщение, где агрегируется список участников
                    text = text_msg + f"\n➡️@{username}, {first_name}!"
                    inline_kb = self.add_players_keyboard()
                    await self.tg_client.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=text,
                        reply_markup=inline_kb,
                    )

            # обрабатывается клик на кнопку "Выйти из игры"
            if data == "/exit_from_game":
                # проверяется, действительно ли игрок уже имеет связь с игрой
                if await self.app.store.quizzes.is_player_added(
                        game_id=game.id,
                        player_id=user_id
                ):
                    await self.app.store.quizzes.remove_player_game_link(
                        game_id=game.id,
                        player_id=user_id
                    )
                    text = (
                            text_msg
                            + f"\n⬅️{first_name} таки с нами играть не будет!"
                    )
                    inline_kb = self.add_players_keyboard()
                    await self.tg_client.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=text,
                        reply_markup=inline_kb,
                    )
                else:
                    text = f"{first_name}, чтобы удалиться из игры, в неё нужно сначала добавиться!"
                    await self.tg_client.send_message(
                        chat_id=chat_id,
                        text=text
                    )

            # обрабатывается клик на кнопку "Начать игру"
            if data == "/start_game":
                players_count = await self.app.store.quizzes.get_player_amount(
                    game_id=game.id
                )
                if players_count <= 1:
                    text = "Ну нет, когда так мало игроков, я не играю"
                    await self.tg_client.send_message(
                        chat_id=chat_id,
                        text=text
                    )
                else:
                    text = text_msg + "\n\n🚨🚨🚨И мы начинаем! Поехали!🚨🚨🚨"
                    await self.tg_client.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=text
                    )

                    await self.tg_client.send_sticker(
                        chat_id=chat_id,
                        sticker=STICKER_SILENCE_IN_STUDIO
                    )

                    text = f"🚨Внимание, вопрос!🚨"
                    await self.tg_client.send_message(
                        chat_id=chat_id,
                        text=text
                    )

                    text = f"{mask}\n{question.title}"
                    sent_message = await self.tg_client.send_message(
                        chat_id=chat_id,
                        text=text
                    )

                    # бот пинит сообщение с вопросом и маской ответа
                    await self.tg_client.pin_chat_message(
                        chat_id=chat_id,
                        message_id=sent_message.result.message_id
                    )

                    # id запиненного сообщения записывается в базу в модель игры,
                    # чтобы можно было быстро получить его в любой момент
                    await self.app.store.quizzes.add_pinned_message_id(
                        game_id=game.id,
                        message_id=sent_message.result.message_id
                    )

                    # дефолтный ход в базе (0) перезаписывается и становится 1
                    await self.next_move(
                        chat_id=chat_id,
                        is_next_player=True
                    )

            # обрабатывается клик на кнопку "Назвать слово сразу"
            if data == "/word":
                # проверяется пермиссия игрока на выполнение данного действия
                if await self.check_user_turn(
                        game=game,
                        chat_id=chat_id,
                        username=username
                ):
                    await self.app.store.quizzes.is_whole_word_state(
                        game_id=game.id,
                        state=True
                    )
                    text = text_msg + f"\n\n@{username} назовёт слово сразу!"
                    await self.tg_client.edit_message_text(
                        chat_id=chat_id,
                        message_id=message_id,
                        text=text
                    )
                    await self.tg_client.send_sticker(
                        chat_id=chat_id,
                        sticker=STICKER_WHOLE_WORD
                    )

    # функция предварительной подготовки к игре, которая запускается при клике на кнопку /start.
    # проверяет, есть ли в чате активная игра.
    # если игры нет - приветствует игроков, создаёт игру в базе
    # добавляет в игру юзера, который нажал кнопку, собирает других игроков
    async def start_session(
            self, chat_id: int, user_id: int, username: str, first_name: str
    ):
        active_game = await self.app.store.quizzes.get_active_game_by_chat_id(
            chat_id=chat_id
        )
        if active_game:
            text = "В этом чате уже есть активная игра"
            await self.tg_client.send_message(
                chat_id=chat_id,
                text=text
            )
        else:
            await self.tg_client.send_sticker(
                chat_id=chat_id,
                sticker=STICKER_HELLO_MY_FRIEND
            )

            question = await self.app.store.quizzes.get_random_question()
            game = await self.app.store.quizzes.create_game(
                chat_id=chat_id,
                question_id=question.id
            )
            player = await self.app.store.quizzes.get_player(
                tg_id=user_id
            )

            if not player:
                await self.app.store.quizzes.add_player(
                    player_id=user_id,
                    player_username=username,
                    player_firstname=first_name
                )

            await self.app.store.quizzes.add_player_game_link(
                game_id=game.id,
                player_id=user_id
            )

            text1 = (
                "🎇Добрый вечер! Здравствуйте, уважаемые дамы и господа! В эфире капитал-шоу «Поле чудес»!\n"
                "🎆И как обычно, под аплодисменты зрительного зала я приглашаю в студию игроков:\n"
                "\n"
                f"➡️@{username}, {first_name}!"
            )

            inline_kb = self.add_players_keyboard()

            await self.tg_client.send_message(
                chat_id=chat_id,
                text=text1,
                reply_markup=inline_kb,
            )

    # функция, которая останавливает игру, либо уведомляет, что активной игры нет
    # убирает все запинненные сообщения, переводит статус игры в базе в неактивный
    async def stop_game(self, chat_id: int):
        game = (
            await self.app.store.quizzes.get_active_game_by_chat_id(
                chat_id=chat_id
            )
        )
        if game:
            await self.tg_client.unpin_all_chat_messages(chat_id=chat_id)
            await self.app.store.quizzes.stop_game(game_id=game.id)
            text = "С вами мы прощаемся ровно на одну неделю. \n" \
                   "Желаем удачи хотя бы на эти коротенькие семь дней. \n" \
                   "Дай вам Бог."
            await self.tg_client.send_message(chat_id=chat_id, text=text)
            await self.tg_client.send_photo(chat_id=chat_id, photo=IMG_GOODBYE)
        else:
            text = "В этом чате нет активной игры"
            await self.tg_client.send_message(chat_id=chat_id, text=text)

    # функция перехода хода
    async def next_move(self, chat_id: int, is_next_player: bool):
        game_state = await self.app.store.quizzes.get_active_game_by_chat_id(chat_id=chat_id)

        # когда тот же самый игрок делает ещё попытку, ход не переводится
        if is_next_player:
            await self.app.store.quizzes.next_move(game_id=game_state.id, move=game_state.move)
            game_state = await self.app.store.quizzes.get_active_game_by_chat_id(chat_id=chat_id)

        # для простоты реализации ход игрока определяется исходя из количества игроков и номера хода делением нацело
        # игроки ходят в той последовательности, в какой добавлялись в игру
        players_count = await self.app.store.quizzes.get_player_amount(
            game_id=game_state.id
        )

        # единица отнимается потому что ход начинается с 1, а индексация игроков - с 0
        active_player_num = game_state.move % players_count - 1
        active_player = game_state.players[active_player_num]

        text = f"Ход игрока @{active_player.username}\n" \
               f"Напишите букву или нажмите на кнопку ниже, если хотите назвать слово сразу."
        append_btn = [
            InlineKeyboardButton(
                "Назвать слово сразу",
                callback_data="/word",
            )
        ]
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[append_btn])
        await self.tg_client.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=inline_kb
        )

    # функция проверяет обновление, чтобы понять, что его написал игрок, который сейчас ходит
    # если нет - то ничего не делает и просто выводит сообщение о недопустимости такого поведения
    async def check_user_turn(self, game: Game, chat_id: int, username: str) -> bool:
        players_count = await self.app.store.quizzes.get_player_amount(
            game.id
        )
        active_player_num = game.move % players_count - 1
        active_player = game.players[active_player_num]

        if username != active_player.username:
            text = f"@{username}, тишина в студии! Не подсказываем! " \
                   f"Сейчас ходит @{active_player.username}."
            await self.tg_client.send_message(chat_id=chat_id, text=text)
            return False

        return True

    async def set_winner(self, chat_id: int, game_id: int, user_id: int, username: str, first_name: str):
        text = f"🔥🔥🔥@{username}, {first_name}, Вы абсолютно в этом правы, " \
               f"вы победитель!\n" \
               f"🔥🔥🔥Приз в студию!"
        await self.tg_client.send_message(
            chat_id=chat_id,
            text=text
        )

        prize = await self.app.store.quizzes.get_random_prize()
        text1 = f"Ваш приз - {prize.title}"
        await self.tg_client.send_message(
            chat_id=chat_id,
            text=text1
        )
        await self.tg_client.send_photo(
            chat_id=chat_id,
            photo=prize.img
        )
        await self.app.store.quizzes.add_winner(
            game_id=game_id,
            user_id=user_id
        )
        await self.stop_game(chat_id=chat_id)

    # разметка клавиатуры из подготовительного шага
    @staticmethod
    def add_players_keyboard():
        append_btn = [
            InlineKeyboardButton(
                "Присоединиться",
                callback_data="/add_to_game",
            ),
            InlineKeyboardButton(
                "Выйти из игры",
                callback_data="/exit_from_game",
            ),
            InlineKeyboardButton(
                "Запустить игру",
                callback_data="/start_game",
            ),
        ]
        inline_kb = InlineKeyboardMarkup(inline_keyboard=[append_btn])

        return inline_kb
