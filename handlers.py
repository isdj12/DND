from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import database as db
import keyboards as kb
from character_sheet import format_character_sheet, get_modifier, format_character_with_features
from dnd_api import get_races, get_classes, get_race_info, get_class_info, calculate_hp_by_class, get_race_features, get_class_features

router = Router()

DEFAULT_CHAR = {
    'name': 'Новый герой', 'race': 'Человек', 'class': 'Воин', 'level': 1,
    'strength': 10, 'dexterity': 10, 'constitution': 10,
    'intelligence': 10, 'wisdom': 10, 'charisma': 10,
    'max_hp': 10, 'current_hp': 10, 'armor_class': 10,
    'initiative_bonus': 0, 'speed': 30, 'passive_perception': 10, 'proficiency_bonus': 2
}

FALLBACK_RACES = [
    {'index': 'human', 'name': 'Человек'}, {'index': 'elf', 'name': 'Эльф'},
    {'index': 'dwarf', 'name': 'Дварф'}, {'index': 'halfling', 'name': 'Полурослик'}
]

FALLBACK_CLASSES = [
    {'index': 'fighter', 'name': 'Воин'}, {'index': 'wizard', 'name': 'Волшебник'},
    {'index': 'rogue', 'name': 'Плут'}, {'index': 'cleric', 'name': 'Жрец'}
]

FALLBACK_RACE_NAMES = {'human': 'Человек', 'elf': 'Эльф', 'dwarf': 'Дварф', 'halfling': 'Полурослик'}
FALLBACK_CLASS_NAMES = {'fighter': 'Воин', 'wizard': 'Волшебник', 'rogue': 'Плут', 'cleric': 'Жрец'}

NUMERIC_FIELDS = [
    'level', 'strength', 'dexterity', 'constitution', 'intelligence',
    'wisdom', 'charisma', 'max_hp', 'current_hp', 'armor_class',
    'initiative_bonus', 'speed', 'passive_perception', 'proficiency_bonus'
]

EDIT_FIELD_MAP = {
    "edit_name": ("name", "Введи новое имя:"),
    "edit_level": ("level", "Введи уровень:"),
    "edit_str": ("strength", "Введи Силу (8-20):"),
    "edit_dex": ("dexterity", "Введи Ловкость (8-20):"),
    "edit_con": ("constitution", "Введи Телосложение (8-20):"),
    "edit_int": ("intelligence", "Введи Интеллект (8-20):"),
    "edit_wis": ("wisdom", "Введи Мудрость (8-20):"),
    "edit_cha": ("charisma", "Введи Харизму (8-20):"),
    "edit_max_hp": ("max_hp", "Введи максимум HP:"),
    "edit_current_hp": ("current_hp", "Введи текущие HP:"),
    "edit_ac": ("armor_class", "Введи класс брони (AC):"),
    "edit_init": ("initiative_bonus", "Введи бонус инициативы:"),
    "edit_speed": ("speed", "Введи скорость (фт):"),
    "edit_perception": ("passive_perception", "Введи пассивное восприятие:"),
    "edit_prof": ("proficiency_bonus", "Введи бонус мастерства:")
}


class CharacterCreation(StatesGroup):
    editing_sheet = State()


class CharacterEdit(StatesGroup):
    waiting_for_value = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await db.create_user(message.from_user.id)
    await message.answer(
        f"Приветствую, {message.from_user.first_name}! 🎲\n\n"
        "Я помогу Мастеру отправлять скрытые события игрокам.\n\n"
        "Команды:\n/hero - Мой герой\n/cancel - Отмена",
        reply_markup=kb.get_main_menu()
    )


@router.message(Command("hero"))
async def cmd_hero(message: Message):
    character = await db.get_character(message.from_user.id)
    if not character:
        await db.create_character(message.from_user.id, DEFAULT_CHAR)
        character = await db.get_character(message.from_user.id)
    features = await db.get_character_features(message.from_user.id)
    char_text = await format_character_with_features(character, features)
    await message.answer(char_text, reply_markup=kb.get_character_menu())


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять.")
        return
    await state.clear()
    await message.answer("Действие отменено. Используй /start для открытия меню.")


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text("Выбери действие:", reply_markup=kb.get_main_menu())
    await callback.answer()


@router.callback_query(F.data == "my_character")
async def show_character(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    character = await db.get_character(callback.from_user.id)
    if not character:
        await db.create_character(callback.from_user.id, DEFAULT_CHAR)
        character = await db.get_character(callback.from_user.id)
    features = await db.get_character_features(callback.from_user.id)
    char_text = await format_character_with_features(character, features)
    await callback.message.edit_text(char_text, reply_markup=kb.get_character_menu())
    await callback.answer()


@router.callback_query(F.data == "edit_character")
async def edit_character_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CharacterCreation.editing_sheet)
    character = await db.get_character(callback.from_user.id)
    features = await db.get_character_features(callback.from_user.id)
    char_text = await format_character_with_features(character, features)
    await callback.message.edit_text(
        f"{char_text}\n\n<b>Выбери параметр для изменения:</b>",
        reply_markup=kb.get_sheet_edit_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_"), F.data != "edit_character")
async def start_edit(callback: CallbackQuery, state: FSMContext):
    field, prompt = EDIT_FIELD_MAP.get(callback.data, (None, None))
    if field:
        await state.update_data(edit_field=field, edit_message_id=callback.message.message_id)
        await state.set_state(CharacterEdit.waiting_for_value)
        await callback.message.edit_text(prompt)
    await callback.answer()


@router.message(CharacterEdit.waiting_for_value)
async def process_edit(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data.get('edit_field')
    edit_message_id = data.get('edit_message_id')
    value = message.text
    try:
        if field in NUMERIC_FIELDS:
            value = int(value)
        
        # Сразу сохраняем изменение
        await db.update_character(message.from_user.id, field, value)
        await state.set_state(CharacterCreation.editing_sheet)
        
        try:
            await message.delete()
        except:
            pass
        
        # Получаем обновленный лист для вывода
        character = await db.get_character(message.from_user.id)
        features = await db.get_character_features(message.from_user.id)
        char_text = await format_character_with_features(character, features)
        
        # Остаемся в меню редактирования
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=edit_message_id,
            text=f"✅ Обновлено!\n\n{char_text}\n\n<b>Выбери параметр для изменения:</b>",
            reply_markup=kb.get_sheet_edit_menu()
        )
    except ValueError:
        await message.answer("Введи число.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
        await state.set_state(CharacterCreation.editing_sheet)


@router.callback_query(F.data == "select_race")
async def show_race_selection(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CharacterCreation.editing_sheet)
    try:
        races = await get_races()
    except Exception:
        races = FALLBACK_RACES
    await callback.message.edit_text("🧬 Выбери расу:", reply_markup=kb.get_race_selection_menu(races))
    await callback.answer()


@router.callback_query(F.data.startswith("select_race_"))
async def select_race(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CharacterCreation.editing_sheet)
    race_index = callback.data.replace("select_race_", "")
    try:
        race_info = await get_race_info(race_index)
        if race_info:
            race_name = race_info['name']
            await db.update_character(callback.from_user.id, "race", race_name)
            if 'speed' in race_info:
                await db.update_character(callback.from_user.id, "speed", race_info['speed'])
        else:
            race_name = FALLBACK_RACE_NAMES.get(race_index, 'Человек')
            await db.update_character(callback.from_user.id, "race", race_name)

        await db.clear_character_features_by_type(callback.from_user.id, 'racial')
        for feature in await get_race_features(race_index):
            await db.add_character_feature(callback.from_user.id, feature['name'], feature['description'], 'racial', race_name)
    except Exception as e:
        race_name = FALLBACK_RACE_NAMES.get(race_index, 'Человек')
        await db.update_character(callback.from_user.id, "race", race_name)

    character = await db.get_character(callback.from_user.id)
    features = await db.get_character_features(callback.from_user.id)
    char_text = await format_character_with_features(character, features)
    await callback.message.edit_text(f"✅ Раса изменена на {race_name}!\n\n{char_text}\n\n<b>Выбери параметр для изменения:</b>", reply_markup=kb.get_sheet_edit_menu())
    await callback.answer()


@router.callback_query(F.data == "select_class")
async def show_class_selection(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CharacterCreation.editing_sheet)
    try:
        classes = await get_classes()
    except Exception:
        classes = FALLBACK_CLASSES
    await callback.message.edit_text("⚔️ Выбери класс:", reply_markup=kb.get_class_selection_menu(classes))
    await callback.answer()


@router.callback_query(F.data.startswith("select_class_"))
async def select_class(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CharacterCreation.editing_sheet)
    class_index = callback.data.replace("select_class_", "")
    hp_text = ""
    try:
        class_info = await get_class_info(class_index)
        character = await db.get_character(callback.from_user.id)
        if class_info:
            class_name = class_info['name']
            await db.update_character(callback.from_user.id, "class", class_name)
            con_mod = get_modifier(character['constitution'])
            new_hp = calculate_hp_by_class(class_index, character['level'], con_mod)
            await db.update_character(callback.from_user.id, "max_hp", new_hp)
            await db.update_character(callback.from_user.id, "current_hp", new_hp)
            hp_text = f"HP: {new_hp}\n"
        else:
            class_name = FALLBACK_CLASS_NAMES.get(class_index, 'Воин')
            await db.update_character(callback.from_user.id, "class", class_name)

        await db.clear_character_features_by_type(callback.from_user.id, 'class')
        for feature in await get_class_features(class_index, character['level']):
            await db.add_character_feature(callback.from_user.id, feature['name'], feature['description'], 'class', class_name)
    except Exception as e:
        class_name = FALLBACK_CLASS_NAMES.get(class_index, 'Воин')
        await db.update_character(callback.from_user.id, "class", class_name)

    character = await db.get_character(callback.from_user.id)
    features = await db.get_character_features(callback.from_user.id)
    char_text = await format_character_with_features(character, features)
    await callback.message.edit_text(f"✅ Класс изменен на {class_name}!\n{hp_text}\n{char_text}\n\n<b>Выбери параметр для изменения:</b>", reply_markup=kb.get_sheet_edit_menu())
    await callback.answer()


@router.callback_query(F.data == "join_game")
async def join_game(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎲 Функция присоединения к игре будет в Этапе 3.",
        reply_markup=kb.get_back_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "be_dm")
async def be_dm(callback: CallbackQuery):
    await callback.message.edit_text(
        "🎭 Функция Мастера будет в Этапе 3.",
        reply_markup=kb.get_back_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "delete_character")
async def confirm_delete(callback: CallbackQuery):
    await callback.message.edit_text("⚠️ Удалить персонажа? Это нельзя отменить!", reply_markup=kb.get_confirm_delete())
    await callback.answer()


@router.callback_query(F.data == "confirm_delete")
async def delete_char(callback: CallbackQuery):
    await db.delete_character(callback.from_user.id)
    await db.clear_all_character_features(callback.from_user.id)
    await callback.message.edit_text("🗑 Персонаж удален.")
    await callback.answer()


@router.message()
async def unknown_message(message: Message):
    await message.answer("Используй /start для открытия меню.")
