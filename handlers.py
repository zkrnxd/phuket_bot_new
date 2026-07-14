import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from data_loader import DataLoader
from keyboards import *
from config import ACCESS_CODE

router = Router()

# Состояния для FSM
class AccessStates(StatesGroup):
    waiting_for_code = State()

class FilterStates(StatesGroup):
    price_min = State()
    price_max = State()

# Инициализация данных
data_loader = None

# Хранилище авторизованных пользователей
authorized_users = set()

def init_data_loader(file_path: str):
    global data_loader
    data_loader = DataLoader(file_path)

def is_authorized(user_id: int) -> bool:
    return user_id in authorized_users

# ============ ФОРМАТИРОВАНИЕ ВЫВОДА ============

def format_project(row, index: int = None) -> str:
    name = row.get("Название проекта", "Не указано")
    district = row.get("Район", "Не указан")
    price = row.get("Цена от", "Не указана")
    developer = row.get("Застройщик", "Не указан")
    beach_dist = row.get("До моря,м", "Не указано")
    site = row.get("Официальный сайт проекта", "")
    
    bisp = row.get("До BISP, км", "—")
    uwc = row.get("До UWC, км", "—")
    headstart = row.get("До HeadStart, км", "—")
    
    text = f"🏡 *{name}*\n"
    text += f"📍 Район: {district}\n"
    text += f"💵 Цена: {price}\n"
    text += f"🏗️ Застройщик: {developer}\n"
    text += f"🏖️ До моря: {beach_dist} м\n"
    text += f"🏫 Школы: BISP {bisp} км, UWC {uwc} км, HeadStart {headstart} км\n"
    if site and isinstance(site, str) and site.startswith("http"):
        text += f"🔗 [Сайт]({site})"
    return text

def format_projects(projects, limit: int = 5) -> str:
    if not projects:
        return "❌ Проектов не найдено"
    
    text = f"🏡 Найдено {len(projects)} проектов:\n\n"
    for i, row in enumerate(projects[:limit], 1):
        text += f"{i}. {format_project(row)}\n\n"
    
    if len(projects) > limit:
        text += f"... и еще {len(projects) - limit} проектов"
    
    return text

def format_beach(beach: dict) -> str:
    name = beach.get("Пляж", "Неизвестно")
    region = beach.get("Регион", "—")
    districts = beach.get("Районы", "—")
    description = beach.get("Описание", "Нет описания")
    suitable = beach.get("Для кого подходит", "—")
    infrastructure = beach.get("Инфраструктура", "—")
    
    text = f"🏖️ *{name}*\n"
    text += f"📍 Регион: {region}\n"
    text += f"📌 Районы: {districts}\n\n"
    text += f"📝 {description}\n\n"
    text += f"👨‍👩‍👧‍👦 Для кого: {suitable}\n"
    text += f"🏪 Инфраструктура: {infrastructure}"
    return text

def format_school(school: dict) -> str:
    name = school.get("Название", "Неизвестно")
    region = school.get("Регион", "—")
    district = school.get("Район", "—")
    program = school.get("Программа", "—")
    age = school.get("Возраст", "—")
    cost = school.get("Стоимость в год", "—")
    site = school.get("Сайт", "")
    
    text = f"🏫 *{name}*\n"
    text += f"📍 Регион: {region}\n"
    text += f"📌 Район: {district}\n"
    text += f"📚 Программа: {program}\n"
    text += f"👶 Возраст: {age}\n"
    text += f"💰 Стоимость: {cost}\n"
    if site and isinstance(site, str) and site.startswith("http"):
        text += f"🔗 [Сайт]({site})"
    return text

def format_developer(dev: dict) -> str:
    name = dev.get("Застройщик", "Неизвестно")
    description = dev.get("Описание", "Нет описания")
    site = dev.get("Официальный сайт", "")
    count = dev.get("Количество проектов", 0)
    
    text = f"🏗️ *{name}*\n\n"
    text += f"📝 {description[:300]}...\n\n" if len(description) > 300 else f"📝 {description}\n\n"
    text += f"📊 Проектов: {count}\n"
    if site and isinstance(site, str) and site.startswith("http"):
        text += f"🔗 [Сайт]({site})"
    return text

# ============ ПРОВЕРКА ДОСТУПА ============

async def check_access(message: Message) -> bool:
    user_id = message.from_user.id
    if not is_authorized(user_id):
        await message.answer(
            "🔒 *Доступ ограничен*\n\n"
            "Этот бот доступен только по приглашению.\n"
            "Введите код доступа, который вы получили от администратора.\n\n"
            "Нажмите кнопку ниже:",
            reply_markup=get_access_keyboard(),
            parse_mode="Markdown"
        )
        return False
    return True

# ============ ОБРАБОТЧИКИ КОМАНД ============

@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    # Проверяем, авторизован ли пользователь
    if is_authorized(user_id):
        await message.answer(
            "🏠 *ДОБРО ПОЖАЛОВАТЬ В СПРАВОЧНИК ПХУКЕТА!*\n\n"
            "Выберите раздел в меню:",
            reply_markup=get_main_keyboard(),
            parse_mode="Markdown"
        )
        await message.answer(
            "📋 Главное меню:",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(
            "🔒 *Доступ ограничен*\n\n"
            "Этот бот доступен только по приглашению.\n"
            "Введите код доступа, который вы получили от администратора.\n\n"
            "Нажмите кнопку ниже:",
            reply_markup=get_access_keyboard(),
            parse_mode="Markdown"
        )

@router.callback_query(F.data == "enter_code")
async def enter_code(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "🔑 *Введите код доступа*\n\n"
        "Отправьте код одним сообщением.",
        parse_mode="Markdown"
    )
    await state.set_state(AccessStates.waiting_for_code)
    await callback.answer()

@router.message(AccessStates.waiting_for_code)
async def process_code(message: Message, state: FSMContext):
    user_id = message.from_user.id
    code = message.text.strip()
    
    if code == ACCESS_CODE:
        authorized_users.add(user_id)
        await state.clear()
        await message.answer(
            "✅ *Доступ разрешен!*\n\n"
            "Добро пожаловать в справочник Пхукета!",
            parse_mode="Markdown"
        )
        await cmd_start(message)
    else:
        await message.answer(
            "❌ *Неверный код доступа*\n\n"
            "Пожалуйста, проверьте код и попробуйте снова.\n"
            "Или обратитесь к администратору.",
            parse_mode="Markdown"
        )

# ============ ГЛАВНОЕ МЕНЮ ============

@router.message(F.text == "🏠 Главное меню")
async def back_to_main(message: Message):
    if not await check_access(message):
        return
    await message.answer(
        "📋 Главное меню:",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "back_main")
async def back_to_main_callback(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.message.edit_text("🔒 Доступ ограничен. Нажмите /start")
        await callback.answer()
        return
    await callback.message.edit_text(
        "📋 Главное меню:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "back_filters")
async def back_to_filters(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "🔍 Выберите фильтр:",
        reply_markup=get_projects_filters()
    )
    await callback.answer()

# ============ ПРОЕКТЫ ============

@router.callback_query(F.data == "menu_projects")
async def menu_projects(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "🔍 Выберите фильтр для поиска проектов:",
        reply_markup=get_projects_filters()
    )
    await callback.answer()

@router.callback_query(F.data == "filter_district")
async def filter_district(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    districts = data_loader.get_districts()
    await callback.message.edit_text(
        "📍 Выберите район:",
        reply_markup=get_district_keyboard(districts)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("district_"))
async def show_district_projects(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    district = callback.data.replace("district_", "")
    projects = data_loader.get_projects_by_district(district)
    text = format_projects(projects)
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button("back_filters"),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data == "filter_type")
async def filter_type(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "🏠 Выберите тип недвижимости:",
        reply_markup=get_type_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("type_"))
async def show_type_projects(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    typ = callback.data.replace("type_", "")
    projects = data_loader.get_projects_by_type(typ)
    text = format_projects(projects)
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button("back_filters"),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data == "filter_price")
async def filter_price(callback: CallbackQuery, state: FSMContext):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "💰 Введите цену *от* в миллионах бат:\n"
        "Например: 3",
        parse_mode="Markdown"
    )
    await state.set_state(FilterStates.price_min)
    await callback.answer()

@router.message(FilterStates.price_min)
async def process_price_min(message: Message, state: FSMContext):
    if not is_authorized(message.from_user.id):
        await message.answer("🔒 Доступ ограничен")
        await state.clear()
        return
    try:
        min_price = float(message.text) * 1000000
        await state.update_data(price_min=min_price)
        await message.answer(
            "💰 Введите цену *до* в миллионах бат:\n"
            "Например: 10",
            parse_mode="Markdown"
        )
        await state.set_state(FilterStates.price_max)
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число. Например: 3")

@router.message(FilterStates.price_max)
async def process_price_max(message: Message, state: FSMContext):
    if not is_authorized(message.from_user.id):
        await message.answer("🔒 Доступ ограничен")
        await state.clear()
        return
    try:
        max_price = float(message.text) * 1000000
        data = await state.get_data()
        min_price = data.get("price_min")
        projects = data_loader.get_projects_by_price(min_price, max_price)
        text = format_projects(projects)
        await message.answer(
            text,
            reply_markup=get_back_button("back_filters"),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        await state.clear()
    except ValueError:
        await message.answer("❌ Пожалуйста, введите число. Например: 10")

@router.callback_query(F.data == "filter_developer")
async def filter_developer(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    developers = data_loader.get_developers()
    await callback.message.edit_text(
        "🏗️ Выберите застройщика:",
        reply_markup=get_developer_keyboard(developers)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("dev_"))
async def show_developer_projects(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    dev_name = callback.data.replace("dev_", "")
    projects = data_loader.get_projects_by_developer(dev_name)
    text = f"🏗️ Проекты застройщика *{dev_name}*:\n\n" + format_projects(projects)
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button("back_filters"),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data == "filter_school")
async def filter_school(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    schools = data_loader.get_schools()
    await callback.message.edit_text(
        "🏫 Выберите школу:",
        reply_markup=get_school_keyboard(schools)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("school_"))
async def show_school_projects(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    school_name = callback.data.replace("school_", "")
    
    school_columns = {
        "BISP": "До BISP, км",
        "UWC": "До UWC, км",
        "HeadStart": "До HeadStart, км",
        "Русская школа": "До Русской школы, км"
    }
    
    col = school_columns.get(school_name)
    if not col:
        await callback.answer("❌ Школа не найдена")
        return
    
    projects = data_loader.get_projects_by_school(col, 3.0)
    text = f"🏫 Проекты рядом со школой *{school_name}* (до 3 км):\n\n" + format_projects(projects)
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button("back_filters"),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await callback.answer()

@router.callback_query(F.data == "filter_beach")
async def filter_beach(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    beaches = data_loader.get_beaches()
    await callback.message.edit_text(
        "🏖️ Выберите пляж:",
        reply_markup=get_beach_keyboard(beaches)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("beach_"))
async def show_beach_projects(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    beach_name = callback.data.replace("beach_", "")
    projects = data_loader.get_projects_by_beach(1000)
    if projects:
        text = f"🏖️ Проекты рядом с пляжем (до 1 км):\n\n" + format_projects(projects)
    else:
        text = "❌ Нет проектов рядом с пляжем"
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button("back_filters"),
        parse_mode="Markdown",
        disable_web_page_preview=True
    )
    await callback.answer()

# ============ ПЛЯЖИ ============

@router.callback_query(F.data == "menu_beaches")
async def menu_beaches(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    beaches = data_loader.get_beaches()
    await callback.message.edit_text(
        "🏖️ Выберите пляж:",
        reply_markup=get_beach_keyboard(beaches)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("beach_"))
async def show_beach_info(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    beach_name = callback.data.replace("beach_", "")
    beaches = data_loader.get_beaches()
    for beach in beaches:
        if beach.get("Пляж") == beach_name:
            text = format_beach(beach)
            await callback.message.edit_text(
                text,
                reply_markup=get_back_button("back_main"),
                parse_mode="Markdown"
            )
            await callback.answer()
            return
    await callback.answer("❌ Пляж не найден")

# ============ ШКОЛЫ ============

@router.callback_query(F.data == "menu_schools")
async def menu_schools(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    schools = data_loader.get_schools()
    await callback.message.edit_text(
        "🏫 Выберите школу:",
        reply_markup=get_school_keyboard(schools)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("school_"))
async def show_school_info(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    school_name = callback.data.replace("school_", "")
    schools = data_loader.get_schools()
    for school in schools:
        name = school.get("Название", "")
        if school_name in name.replace(" International School", "").replace(" Phuket", "").strip():
            text = format_school(school)
            await callback.message.edit_text(
                text,
                reply_markup=get_back_button("back_main"),
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            await callback.answer()
            return
    await callback.answer("❌ Школа не найдена")

# ============ ЗАСТРОЙЩИКИ ============

@router.callback_query(F.data == "menu_developers")
async def menu_developers(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    developers = data_loader.get_developers()
    await callback.message.edit_text(
        "🏗️ Выберите застройщика:",
        reply_markup=get_developer_keyboard(developers)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("dev_"))
async def show_developer_info(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    dev_name = callback.data.replace("dev_", "")
    developers = data_loader.get_developers()
    for dev in developers:
        if dev.get("Застройщик") == dev_name:
            text = format_developer(dev)
            await callback.message.edit_text(
                text,
                reply_markup=get_back_button("back_main"),
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
            await callback.answer()
            return
    await callback.answer("❌ Застройщик не найден")

# ============ ВИЗЫ ============

@router.callback_query(F.data == "menu_visas")
async def menu_visas(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    visas = data_loader.get_visas()
    text = "🛂 *ВИЗЫ В ТАИЛАНД*\n\n"
    for visa in visas:
        text += f"📌 *{visa.get('Тип визы', '')}*\n"
        text += f"   Срок: {visa.get('Срок', '—')}\n"
        text += f"   Требования: {visa.get('Требования', '—')[:100]}...\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button("back_main"),
        parse_mode="Markdown"
    )
    await callback.answer()

# ============ НАЛОГИ ============

@router.callback_query(F.data == "menu_taxes")
async def menu_taxes(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    taxes = data_loader.get_taxes()
    text = "📊 *НАЛОГИ В ТАИЛАНДЕ*\n\n"
    for _, row in taxes.iterrows():
        category = row.get("A", "")
        if category and "FREEHOLD" in category.upper():
            text += f"\n🔹 *{category}*\n"
        elif category and not category.startswith("Сравнение") and category.strip():
            text += f"   • {category}: {row.get('B', '—')}\n"
    
    await callback.message.edit_text(
        text[:4000],
        reply_markup=get_back_button("back_main"),
        parse_mode="Markdown"
    )
    await callback.answer()

# ============ ДРУГИЕ РАЗДЕЛЫ (заглушки) ============

@router.callback_query(F.data == "menu_hospitals")
async def menu_hospitals(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "🏥 *Больницы Пхукета*\n\n"
        "• Bangkok Hospital Phuket — JCI, 24/7\n"
        "• Siriroj Hospital — JCI, 24/7\n"
        "• Phuket International Hospital — 24/7\n"
        "• Dibuk Hospital — ограниченно\n\n"
        "Подробности в разработке.",
        reply_markup=get_back_button("back_main"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_kindergartens")
async def menu_kindergartens(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "👶 *Детские сады Пхукета*\n\n"
        "• Indigo School (Bang Tao) — русскоязычная\n"
        "• Chalong Kindergarten — билингвальный\n"
        "• Buds Nursery — международный\n"
        "• Детский сад «Сказка» (Rawai) — билингвальный\n\n"
        "Подробности в разработке.",
        reply_markup=get_back_button("back_main"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_districts")
async def menu_districts(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    districts = data_loader.get_districts()
    text = "📍 *Районы Пхукета*\n\n"
    for d in districts[:22]:
        text += f"• {d}\n"
    text += "\nВыберите район в разделе «Проекты» → «По району»"
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button("back_main"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_rental")
async def menu_rental(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "💰 *Арендная доходность на Пхукете*\n\n"
        "Средняя доходность: 6–10% годовых\n\n"
        "🏖️ Bang Tao: 9–10%\n"
        "🏖️ Patong: до 9.1%\n"
        "🏖️ Kamala: 8.1%\n"
        "🏖️ Rawai/Chalong: 5–7%\n\n"
        "Подробные таблицы в разработке.",
        reply_markup=get_back_button("back_main"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_countries")
async def menu_countries(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "🌍 *Сравнение стран для инвестиций*\n\n"
        "🇹🇭 Таиланд (Пхукет): $100k+, 6–10%\n"
        "🇦🇪 ОАЭ (Дубай): $250k+, 3–5%\n"
        "🇹🇷 Турция: $60k+, 4–7%\n"
        "🇻🇳 Вьетнам: $80k+, 5–8%\n\n"
        "Подробности в разработке.",
        reply_markup=get_back_button("back_main"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_faq")
async def menu_faq(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "📚 *Частые вопросы*\n\n"
        "• Какие визы дают право на работу?\n"
        "• Какие налоги при покупке Freehold?\n"
        "• Какая доходность от аренды?\n"
        "• Какие школы на Пхукете?\n\n"
        "Подробные ответы в разработке.",
        reply_markup=get_back_button("back_main"),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_scenario")
async def menu_scenario(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    await callback.message.edit_text(
        "⭐ *ПОДБОР НЕДВИЖИМОСТИ*\n\n"
        "Ответьте на 4 вопроса, и я подберу лучшие варианты.\n\n"
        "Вопрос 1: Какой у вас бюджет?",
        reply_markup=get_scenario_budget()
    )
    await callback.answer()

# ============ СЦЕНАРИЙ ПОДБОРА ============

scenario_data = {}

@router.callback_query(F.data.startswith("scenario_budget_"))
async def scenario_budget(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    user_id = callback.from_user.id
    scenario_data[user_id] = {"budget": callback.data.replace("scenario_budget_", "")}
    await callback.message.edit_text(
        "⭐ *ПОДБОР НЕДВИЖИМОСТИ*\n\n"
        "Вопрос 2: Какой тип недвижимости вас интересует?",
        reply_markup=get_scenario_type()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("scenario_type_"))
async def scenario_type(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    user_id = callback.from_user.id
    scenario_data[user_id]["type"] = callback.data.replace("scenario_type_", "")
    await callback.message.edit_text(
        "⭐ *ПОДБОР НЕДВИЖИМОСТИ*\n\n"
        "Вопрос 3: Что для вас важнее всего?",
        reply_markup=get_scenario_priority()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("scenario_priority_"))
async def scenario_priority(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    user_id = callback.from_user.id
    scenario_data[user_id]["priority"] = callback.data.replace("scenario_priority_", "")
    await callback.message.edit_text(
        "⭐ *ПОДБОР НЕДВИЖИМОСТИ*\n\n"
        "Вопрос 4: Кто будет жить в недвижимости?",
        reply_markup=get_scenario_who()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("scenario_who_"))
async def scenario_who(callback: CallbackQuery):
    if not is_authorized(callback.from_user.id):
        await callback.answer("🔒 Доступ ограничен")
        return
    user_id = callback.from_user.id
    scenario_data[user_id]["who"] = callback.data.replace("scenario_who_", "")
    
    data = scenario_data.get(user_id, {})
    
    # Генерируем рекомендации на основе ответов
    recommendations = []
    
    # Базовые рекомендации по бюджету
    budget = data.get("budget", "")
    typ = data.get("type", "")
    
    if "10–30" in budget or "30–50" in budget:
        if typ == "Вилла" or typ == "Любой":
            recommendations = [
                ("Aileen Villas Layan Phase V", "Layan", "17.5 млн ฿", "Отличный выбор для семьи, приватная вилла с бассейном"),
                ("Botanica Louvre", "Si Sunthon", "19.9 млн ฿", "Премиальный застройщик, всего 8 вилл, рядом с HeadStart"),
                ("Proxima Phuket Villas", "Si Sunthon", "13.8 млн ฿", "Энергоэффективный дизайн, современная архитектура")
            ]
        else:
            recommendations = [
                ("Origin Residences Phuket Bangtao", "Bang Tao", "4.6 млн ฿", "Премиальное кондо от Origin, высокая доходность"),
                ("The Title Modeva", "Bang Tao", "4.8 млн ฿", "59 зон отдыха, pet-friendly, высокая доходность")
            ]
    elif "до 5" in budget or "5–10" in budget:
        recommendations = [
            ("Above Element Condominium", "Pasak", "5.7 млн ฿", "От Art House, хорошая доходность"),
            ("Capri Residence Bang Tao", "Bang Tao", "5.8 млн ฿", "Готовое кондо, рядом с инфраструктурой"),
            ("The Title Sierra", "Choeng Thale", "3.1 млн ฿", "Бюджетное кондо в центре Bang Tao")
        ]
    else:
        recommendations = [
            ("Poetry Villas", "Bang Tao", "60.7 млн ฿", "Элитные виллы у моря, 325 м до пляжа"),
            ("Botanica Sky Valley", "Choeng Thale", "71.4 млн ฿", "Ультра-люкс, видовые виллы на холме")
        ]
    
    # Формируем ответ
    text = "⭐ *ВАШИ РЕКОМЕНДАЦИИ*\n\n"
    text += f"📊 Бюджет: {data.get('budget', '—')}\n"
    text += f"🏠 Тип: {data.get('type', '—')}\n"
    text += f"🎯 Приоритет: {data.get('priority', '—')}\n"
    text += f"👤 Кто живет: {data.get('who', '—')}\n\n"
    text += "🏡 *Рекомендуемые проекты:*\n\n"
    
    for i, (name, district, price, reason) in enumerate(recommendations[:3], 1):
        text += f"{i}. *{name}*\n"
        text += f"   📍 {district}\n"
        text += f"   💵 {price}\n"
        text += f"   ✅ {reason}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_back_button("back_main"),
        parse_mode="Markdown"
    )
    await callback.answer()