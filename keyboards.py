from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import pandas as pd

# ============ REPLY КЛАВИАТУРА (вместо клавиатуры телефона) ============

def get_main_keyboard() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🏠 Главное меню")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ============ INLINE КЛАВИАТУРЫ ============

def get_main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏡 Проекты", callback_data="menu_projects"),
        InlineKeyboardButton(text="🏖️ Пляжи", callback_data="menu_beaches")
    )
    builder.row(
        InlineKeyboardButton(text="🏫 Школы", callback_data="menu_schools"),
        InlineKeyboardButton(text="🏥 Больницы", callback_data="menu_hospitals")
    )
    builder.row(
        InlineKeyboardButton(text="👶 Сады", callback_data="menu_kindergartens"),
        InlineKeyboardButton(text="🏗️ Застройщики", callback_data="menu_developers")
    )
    builder.row(
        InlineKeyboardButton(text="📍 Районы", callback_data="menu_districts"),
        InlineKeyboardButton(text="💰 Аренда", callback_data="menu_rental")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Налоги", callback_data="menu_taxes"),
        InlineKeyboardButton(text="🛂 Визы", callback_data="menu_visas")
    )
    builder.row(
        InlineKeyboardButton(text="🌍 Страны", callback_data="menu_countries"),
        InlineKeyboardButton(text="📚 FAQ", callback_data="menu_faq")
    )
    builder.row(
        InlineKeyboardButton(text="⭐ Подобрать под меня", callback_data="menu_scenario")
    )
    return builder.as_markup()

def get_projects_filters() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📍 По району", callback_data="filter_district"),
        InlineKeyboardButton(text="🏠 По типу", callback_data="filter_type")
    )
    builder.row(
        InlineKeyboardButton(text="💵 По цене", callback_data="filter_price"),
        InlineKeyboardButton(text="🏗️ По застройщику", callback_data="filter_developer")
    )
    builder.row(
        InlineKeyboardButton(text="🏫 Рядом со школой", callback_data="filter_school"),
        InlineKeyboardButton(text="🏖️ Рядом с пляжем", callback_data="filter_beach")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_main")
    )
    return builder.as_markup()

def get_district_keyboard(districts: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    row = []
    for district in districts:
        if district and pd.notna(district):
            row.append(InlineKeyboardButton(text=district[:20], callback_data=f"district_{district}"))
            if len(row) == 3:
                builder.row(*row)
                row = []
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_filters"))
    return builder.as_markup()

def get_type_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏢 Кондо", callback_data="type_Кондо"),
        InlineKeyboardButton(text="🏡 Вилла", callback_data="type_Вилла")
    )
    builder.row(
        InlineKeyboardButton(text="🏘️ Таунхаус", callback_data="type_Таунхаус"),
        InlineKeyboardButton(text="🏨 Другое", callback_data="type_Другое")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_filters")
    )
    return builder.as_markup()

def get_beach_keyboard(beaches: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    row = []
    for beach in beaches[:12]:
        name = beach.get("Пляж", "")
        if name:
            row.append(InlineKeyboardButton(text=name[:20], callback_data=f"beach_{name}"))
            if len(row) == 3:
                builder.row(*row)
                row = []
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"))
    return builder.as_markup()

def get_school_keyboard(schools: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    row = []
    for school in schools[:11]:
        name = school.get("Название", "")
        if name:
            short_name = name.replace(" International School", "").replace(" Phuket", "").strip()
            row.append(InlineKeyboardButton(text=short_name[:15], callback_data=f"school_{short_name}"))
            if len(row) == 3:
                builder.row(*row)
                row = []
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_main"))
    return builder.as_markup()

def get_developer_keyboard(developers: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    row = []
    for dev in developers[:12]:
        name = dev.get("Застройщик", "")
        if name:
            row.append(InlineKeyboardButton(text=name[:18], callback_data=f"dev_{name}"))
            if len(row) == 2:
                builder.row(*row)
                row = []
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data="back_filters"))
    return builder.as_markup()

def get_scenario_budget() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="до 5 млн ฿", callback_data="scenario_budget_до 5 млн"),
        InlineKeyboardButton(text="5–10 млн ฿", callback_data="scenario_budget_5–10 млн")
    )
    builder.row(
        InlineKeyboardButton(text="10–30 млн ฿", callback_data="scenario_budget_10–30 млн"),
        InlineKeyboardButton(text="30–50 млн ฿", callback_data="scenario_budget_30–50 млн")
    )
    builder.row(
        InlineKeyboardButton(text="от 50 млн ฿", callback_data="scenario_budget_от 50 млн")
    )
    return builder.as_markup()

def get_scenario_type() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏢 Кондо", callback_data="scenario_type_Кондо"),
        InlineKeyboardButton(text="🏡 Вилла", callback_data="scenario_type_Вилла")
    )
    builder.row(
        InlineKeyboardButton(text="🏘️ Таунхаус", callback_data="scenario_type_Таунхаус"),
        InlineKeyboardButton(text="Любой", callback_data="scenario_type_Любой")
    )
    return builder.as_markup()

def get_scenario_priority() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏖️ Близость к морю", callback_data="scenario_priority_море"),
        InlineKeyboardButton(text="🏫 Близость к школе", callback_data="scenario_priority_школа")
    )
    builder.row(
        InlineKeyboardButton(text="🏪 Инфраструктура", callback_data="scenario_priority_инфра"),
        InlineKeyboardButton(text="🌿 Приватность/тишина", callback_data="scenario_priority_приватность")
    )
    builder.row(
        InlineKeyboardButton(text="💰 Доходность", callback_data="scenario_priority_доходность")
    )
    return builder.as_markup()

def get_scenario_who() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="👨‍👩‍👧‍👦 Семья с детьми", callback_data="scenario_who_семья"),
        InlineKeyboardButton(text="💼 Инвестор", callback_data="scenario_who_инвестор")
    )
    builder.row(
        InlineKeyboardButton(text="👴 Пенсионер", callback_data="scenario_who_пенсионер"),
        InlineKeyboardButton(text="💻 Цифровой кочевник", callback_data="scenario_who_номад")
    )
    builder.row(
        InlineKeyboardButton(text="🏖️ Для отдыха", callback_data="scenario_who_отдых")
    )
    return builder.as_markup()

def get_back_button(callback: str = "back_main") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=callback))
    return builder.as_markup()

def get_access_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для входа в бота"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔑 Ввести код доступа", callback_data="enter_code")
    )
    return builder.as_markup()