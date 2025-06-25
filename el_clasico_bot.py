from aiogram.fsm.state import State, StatesGroup
import gspread
from aiogram.utils.markdown import hbold
from oauth2client.service_account import ServiceAccountCredentials
from aiogram.types import Message
from aiogram.filters import StateFilter
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext


TOKEN = ""
bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)
dp["fsm_storage"] = {}




scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_NAME = "расписание EL CLASICO"
sheet = client.open(SHEET_NAME).worksheet("общие группы")
sheet_clients = client.open(SHEET_NAME).worksheet("Заявки")
sheet_help = client.open(SHEET_NAME).worksheet("Обращение")

class RegisterState(StatesGroup):
    branch = State()
    name = State()
    birth_year = State()
    phone = State()

class ScheduleState(StatesGroup):  
    branch = State()

class HelpState(StatesGroup):
        issue = State()
        phone = State()
        name = State()

main_menu = [
        "ℹ️ Ақпарат/Информация",
        "📅 Кесте/Расписание",
        "📝 Запись/Тіркелу",
        "❓ Көмек/Помощь"
    ]

# Филиалы
branches_list = {
    "70 мектеп/школа, Майкайын 1": "70_school",
    "74 мектеп/школа, Жургенова 29": "74_school",
    "10 мектеп/школа, Габдуллина 7": "10_school",
    "71 мектеп/школа, Омарова 4": "71_school",
    "84 мектеп/школа, Ұлы дала 41/1": "84_school",
    "95 мектеп/школа, Ұлы дала 73/1": "95_school",
    "Бином мектебі/школа, Байтұрсынова 49А": "Binom",
    "2 мектеп/школа, Сейфуллина 19": "2_school",
    "44 мектеп/школа, Нұрлы жол 8": "44_school",
}

lang_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇰🇿 Қазақша"), KeyboardButton(text="🇷🇺 Русский")]
    ],
    resize_keyboard=True
)
main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=cmd)] for cmd in [
        "ℹ️ Ақпарат/Информация",
        "📅 Кесте/Расписание",
        "📝 Запись/Тіркелу",
        "❓ Көмек/Помощь"
    ]],
    resize_keyboard=True
)

def get_branches_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=branch)] for branch in branches_list.keys()],
        resize_keyboard=True
    )


user_lang = {}

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Тілді таңдаңыз / Выберите язык:", reply_markup=lang_keyboard)

@dp.message(lambda message: message.text in ["🇰🇿 Қазақша", "🇷🇺 Русский"])
async def set_language(message: types.Message):
    user_lang[message.from_user.id] = "kk" if message.text == "🇰🇿 Қазақша" else "ru"
    await message.answer(
        "🌟 Командаларды пайдалану үшін батырманы басыңыз." if user_lang[message.from_user.id] == "kk"
        else "🌟 Выберите команду в меню.",
        reply_markup=main_menu_keyboard
    )


@dp.message(lambda message: message.text == "ℹ️ Ақпарат/Информация")
async def choose_branch_info(message: types.Message):
    lang = user_lang.get(message.from_user.id, "ru")
    text = (
        "⚽ *El Clasico* футбол мектебі – бұл балалар футбол шеберлігін дамытатын орын!"
        "📍 Біз қаланың орталығында орналасқанбыз, жаттығулар жабық және ашық алаңдарда өтеді."
        "👨‍🏫 Тәжірибелі жаттықтырушылар мен кәсіби көзқарас."
        "🏟️ Филиалдар:\n"
        "📍 70 мектеп, Майқайын 1\n"
        "📍 74 мектеп, Жүргенова 29\n"
        "📍 10 мектеп, Габдуллина 7\n"
        "📍 71 мектеп, Омарова 4\n"
        "📍 Өзен Арена, Қордай 8а\n"
        "📍 Фаворит Арена, Алтыбақан 14\n"
        "📍 84 мектеп, Ұлы дала 41/1\n"
        "📍 95 мектеп, Ұлы дала 73/1"
        if lang == "kk" else
        "⚽ *El Clasico* – это футбольная школа для детей!"
        "📍 Мы находимся в центре города, тренировки проходят в закрытых и открытых площадках."
        "👨‍🏫 Опытные тренеры и профессиональный подход."
           "Филиалы: школа №70, №74, №10, №71, Озен Арена, Фаворит Арена, школа №84, №95, Бином, школа №2, школа №44."
        )
    await message.answer(text, parse_mode="Markdown")
    await message.answer("ℹ️ Выберите команду:", reply_markup=main_menu_keyboard)


@dp.message(lambda message: message.text == "📅 Кесте/Расписание")
async def choose_branch_schedule(message: types.Message, state: FSMContext):
    lang = user_lang.get(message.from_user.id, "ru")
    await message.answer(
        "📍 Филиалды таңдаңыз:" if lang == "kk" else "📍 Выберите филиал:",
        reply_markup=get_branches_keyboard()
    )
    await state.set_state(ScheduleState.branch)


@dp.message(ScheduleState.branch)
async def send_schedule(message: types.Message, state: FSMContext):
    branch_name = message.text
    if branch_name not in branches_list:
        await message.answer(
            "⚠️ Тізімнен таңдаңыз." if user_lang.get(message.from_user.id, "ru") == "kk"
            else "⚠️ Выберите филиал из списка."
        )
        return

    branch_id = branches_list[branch_name]
    data = sheet.get_all_records()
    lang = user_lang.get(message.from_user.id, "ru")

    schedule_text = f"{hbold(f'📅 {branch_name} кестесі:')}\n\n" if lang == "kk" else f"{hbold(f'📅 Расписание для {branch_name}:')}\n\n"

    for row in data:
        if row.get('Филиал (Адрес)') == branch_id:
            schedule_text += (
                f"🕒 Уақыты/Время: {row.get('Время', 'Не указано')}\n"
                f"📅 Өткізілу күні/День занятий: {row.get('Дни занятий', 'Не указано')}\n"
                f"👨‍👦 Жас аралығы/Возрастная группа: {row.get('Возрастная группа', 'Не указано')}\n"
                f"👨‍🏫 Жаттықтырушы/ Тренер: {row.get('Тренер', 'Не указано')}\n\n"
            )

    await message.answer(schedule_text if schedule_text.strip() else "❌ Расписание не найдено.", parse_mode="HTML")
    await message.answer("ℹ️ Выберите команду:", reply_markup=main_menu_keyboard)
    await state.clear()

@dp.message(lambda message: message.text == "📝 Запись/Тіркелу")
async def start_registration(message: Message, state: FSMContext):
    await state.clear()
    lang = user_lang.get(message.from_user.id, "ru")
    await message.answer(
        "📍 Филиалды таңдаңыз:" if lang == "kk" else "📍 Выберите филиал:",
        reply_markup=get_branches_keyboard()
    )
    await state.set_state(RegisterState.branch)

@dp.message(RegisterState.branch)
async def enter_branch(message: Message, state: FSMContext):
    lang = user_lang.get(message.from_user.id, "ru")
    if message.text not in branches_list:
        await message.answer("⚠️ Тізімнен таңдаңыз." if lang == "kk" else "⚠️ Выберите филиал из списка.")
        return
    await state.update_data(branch=message.text)
    await message.answer(
        "👤 Баланың аты-жөнін енгізіңіз:" if lang == "kk" else "👤 Введите имя и фамилию ребенка."
    )
    await state.set_state(RegisterState.name)

@dp.message(StateFilter(RegisterState.name))
async def enter_name(message: Message, state: FSMContext):
    lang = user_lang.get(message.from_user.id, "ru")
    await state.update_data(name=message.text)
    await message.answer("📅 Туған жылын енгізіңіз:" if lang == "kk" else "📅 Введите год рождения:")
    await state.set_state(RegisterState.birth_year)

@dp.message(StateFilter(RegisterState.birth_year))
async def enter_birth_year(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (2009 <= int(message.text) <= 2020):
        await message.answer("⚠️ Жасыңызды дұрыс енгізіңіз (мысалы, 2015)." if user_lang.get(message.from_user.id, "ru") == "kk" else "⚠️ Введите корректный год рождения (например, 2015).")
        return
    await state.update_data(birth_year=message.text)
    await message.answer("📞 Телефон нөміріңізді енгізіңіз (WhatsApp):" if user_lang.get(message.from_user.id, "ru") == "kk" else "📞 Введите номер телефона (WhatsApp):")
    await state.set_state(RegisterState.phone)


import re  


@dp.message(StateFilter(RegisterState.phone))
async def enter_phone(message: Message, state: FSMContext):
    lang = user_lang.get(message.from_user.id, "ru")

    phone = message.text.strip()  # Убираем пробелы по краям
    phone = phone.replace(" ", "")  # Убираем пробелы внутри номера

    # Если номер начинается с 8, меняем его на +7
    if phone.startswith("8") and len(phone) == 11:
        phone = "+7" + phone[1:]

    # Проверяем, что номер соответствует формату +7XXXXXXXXXX
    if not re.match(r"^\+7\d{10}$", phone):
        await message.answer(
            "⚠️ Телефон нөміріңізді дұрыс енгізіңіз (+7XXXXXXXXXX немесе 8XXXXXXXXXX)."
            if lang == "kk" else
            "⚠️ Введите корректный номер телефона (+7XXXXXXXXXX или 8XXXXXXXXXX)."
        )
        return

    user_data = await state.get_data()
    sheet_clients.append_row([
        user_data.get('branch', 'Не указан'),
        user_data.get('name', 'Не указан'),
        user_data.get('birth_year', 'Не указан'),
        phone  # Записываем уже исправленный номер
    ])

    await message.answer("✅ Сіз сәтті тіркелдіңіз! Whatsapp желісінде менеджерден хабарлама күтіңіз!" if user_lang.get(message.from_user.id, "ru") == "kk" else "✅ Вы успешно записаны! В whatsapp ожидайте от менеджера сообщения!")
    await state.clear()
    await message.answer("ℹ️ Выберите команду:", reply_markup=main_menu_keyboard)
@dp.message(Command("cancel"))
async def cancel_registration(message: Message, state: FSMContext):
    await state.clear()
    lang = user_lang.get(message.from_user.id, "ru")
    await message.answer("🚫 Регистрация отменена." if lang == "kk" else "🚫 Регистрация отменена.\n\nЧтобы начать заново, введите /register")


@dp.message(lambda message: message.text == "❓ Көмек/Помощь")
async def help_request(message: Message, state: FSMContext):
    await state.clear()
    lang = user_lang.get(message.from_user.id, "ru")

    await message.answer(
        "👋 Қайырлы күн! Сізге қалай көмектесе аламыз? \n\n"
        "Өтініш, мәселеңізді қысқаша сипаттаңыз." if lang == "kk" else
        "👋 Добрый день! Чем можем помочь? \n\n"
        "Пожалуйста, кратко опишите вашу проблему."
    )

    await state.set_state(HelpState.issue)


@dp.message(StateFilter(HelpState.issue))
async def enter_issue(message: Message, state: FSMContext):
    lang = user_lang.get(message.from_user.id, "ru")

    await state.update_data(issue=message.text)
    await message.answer(
        "📞 Байланысу үшін телефон нөміріңізді енгізіңіз:" if lang == "kk" else
        "📞 Введите ваш номер телефона для связи:"
    )

    await state.set_state(HelpState.phone)


@dp.message(StateFilter(HelpState.phone))
async def enter_help_phone(message: Message, state: FSMContext):
    lang = user_lang.get(message.from_user.id, "ru")
    phone = message.text.strip().replace(" ", "")

    if phone.startswith("8") and len(phone) == 11:
        phone = "+7" + phone[1:]

    if not re.match(r"^\+7\d{10}$", phone):
        await message.answer(
            "⚠️ Телефон нөміріңізді дұрыс енгізіңіз (+7XXXXXXXXXX немесе 8XXXXXXXXXX)."
            if lang == "kk" else
            "⚠️ Введите корректный номер телефона (+7XXXXXXXXXX или 8XXXXXXXXXX)."
        )
        return

    await state.update_data(phone=phone)
    await message.answer(
        "👤 Атыңызды енгізіңіз:" if lang == "kk" else
        "👤 Введите ваше имя:"
    )

    await state.set_state(HelpState.name)


@dp.message(StateFilter(HelpState.name))
async def enter_help_name(message: Message, state: FSMContext):
    lang = user_lang.get(message.from_user.id, "ru")

    user_data = await state.get_data()
    sheet_help.append_row([  # Используем правильный лист
        "Помощь",  # Тип запроса
        user_data.get('issue', 'Не указан'),
        user_data.get('phone', 'Не указан'),
        message.text  # Имя пользователя
    ])

    await message.answer(
        "✅ Өтінішіңіз қабылданды! Менеджер сізге жақын арада WhatsApp арқылы хабарласады."
        if lang == "kk" else
        "✅ Ваш запрос принят! Менеджер свяжется с вами в ближайшее время в WhatsApp."
    )

    await state.clear()
    await message.answer("ℹ️ Выберите команду:", reply_markup=main_menu_keyboard)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())