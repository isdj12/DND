from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu():
    """Главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Мой герой", callback_data="my_character")],
        [InlineKeyboardButton(text="🎲 Присоединиться к игре", callback_data="join_game")],
        [InlineKeyboardButton(text="🎭 Стать Мастером", callback_data="be_dm")]
    ])


def get_character_menu():
    """Меню персонажа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_character")],
        [InlineKeyboardButton(text="🗑 Удалить", callback_data="delete_character")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])


def get_race_selection_menu(races):
    """Меню выбора расы"""
    keyboard = []
    for i in range(0, len(races), 2):
        row = []
        for j in range(2):
            if i + j < len(races):
                race = races[i + j]
                row.append(InlineKeyboardButton(
                    text=race['name'], 
                    callback_data=f"select_race_{race['index']}"
                ))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="my_character")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_class_selection_menu(classes):
    """Меню выбора класса"""
    keyboard = []
    for i in range(0, len(classes), 2):
        row = []
        for j in range(2):
            if i + j < len(classes):
                cls = classes[i + j]
                row.append(InlineKeyboardButton(
                    text=cls['name'], 
                    callback_data=f"select_class_{cls['index']}"
                ))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="my_character")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_sheet_edit_menu():
    """Меню редактирования листа персонажа"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 Имя", callback_data="edit_name"),
            InlineKeyboardButton(text="🧬 Раса", callback_data="select_race"),
            InlineKeyboardButton(text="⚔️ Класс", callback_data="select_class")
        ],
        [
            InlineKeyboardButton(text="⭐️ Уровень", callback_data="edit_level"),
            InlineKeyboardButton(text="❤️ HP", callback_data="edit_max_hp"),
            InlineKeyboardButton(text="🛡 AC", callback_data="edit_ac")
        ],
        [
            InlineKeyboardButton(text="💪 СИЛ", callback_data="edit_str"),
            InlineKeyboardButton(text="🤸 ЛОВ", callback_data="edit_dex"),
            InlineKeyboardButton(text="🫀 ТЕЛ", callback_data="edit_con")
        ],
        [
            InlineKeyboardButton(text="🧠 ИНТ", callback_data="edit_int"),
            InlineKeyboardButton(text="🦉 МДР", callback_data="edit_wis"),
            InlineKeyboardButton(text="✨ ХАР", callback_data="edit_cha")
        ],
        [
            InlineKeyboardButton(text="⚡️ Инициатива", callback_data="edit_init"),
            InlineKeyboardButton(text="🏃 Скорость", callback_data="edit_speed")
        ],
        [
            InlineKeyboardButton(text="👁 Восприятие", callback_data="edit_perception"),
            InlineKeyboardButton(text="⭐️ Мастерство", callback_data="edit_prof")
        ],
        [InlineKeyboardButton(text="◀️ Назад к листу", callback_data="my_character")]
    ])


def get_edit_menu():
    """Меню редактирования (старое, оставлено для совместимости)"""
    return get_sheet_edit_menu()


def get_back_menu():
    """Кнопка назад"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back_to_menu")]
    ])


def get_confirm_delete():
    """Подтверждение удаления"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_delete")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="my_character")]
    ])
