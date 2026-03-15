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


class CharacterCreation(StatesGroup):
    """Состояния для создания персонажа"""
    editing_sheet = State()  # Редактирование через inline-кнопки


class CharacterEdit(StatesGroup):
    """Состояния для редактирования персонажа"""
    waiting_for_value = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start"""
    await db.create_user(message.from_user.id)
    await message.answer(
        f"Приветствую, {message.from_user.first_name}! 🎲\n\n"
        "Я помогу Мастеру отправлять скрытые события игрокам.\n\n"
        "Команды:\n"
        "/hero - Мой герой\n"
        "/help - Помощь",
        reply_markup=kb.get_main_menu()
    )


@router.message(Command("hero"))
async def cmd_hero(message: Message):
    """Команда /hero"""
    character = await db.get_character(message.from_user.id)
    
    if not character:
        # Создаем пустой лист с дефолтными значениями
        default_char = {
            'name': 'Новый герой',
            'race': 'Человек',
            'class': 'Воин',
            'level': 1,
            'strength': 10, 'dexterity': 10, 'constitution': 10,
            'intelligence': 10, 'wisdom': 10, 'charisma': 10,
            'max_hp': 10, 'current_hp': 10, 'armor_class': 10,
            'initiative_bonus': 0, 'speed': 30,
            'passive_perception': 10, 'proficiency_bonus': 2
        }
        await db.create_character(message.from_user.id, default_char)
        character = await db.get_character(message.from_user.id)
    
    char_text = format_character_sheet(character)
    await message.answer(char_text, reply_markup=kb.get_character_menu())


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        "Выбери действие:",
        reply_markup=kb.get_main_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "my_character")
async def show_character(callback: CallbackQuery, state: FSMContext):
    """Показать персонажа"""
    print(f"DEBUG: Получен callback my_character от {callback.from_user.id}")
    try:
        await state.clear()
        character = await db.get_character(callback.from_user.id)
        
        if not character:
            # Создаем пустой лист с дефолтными значениями
            default_char = {
                'name': 'Новый герой',
                'race': 'Человек',
                'class': 'Воин',
                'level': 1,
                'strength': 10, 'dexterity': 10, 'constitution': 10,
                'intelligence': 10, 'wisdom': 10, 'charisma': 10,
                'max_hp': 10, 'current_hp': 10, 'armor_class': 10,
                'initiative_bonus': 0, 'speed': 30,
                'passive_perception': 10, 'proficiency_bonus': 2
            }
            await db.create_character(callback.from_user.id, default_char)
            character = await db.get_character(callback.from_user.id)
        
        # Получаем особенности персонажа
        features = await db.get_character_features(callback.from_user.id)
        char_text = await format_character_with_features(character, features)
        
        await callback.message.edit_text(char_text, reply_markup=kb.get_character_menu())
        await callback.answer()
        print("DEBUG: Персонаж показан успешно")
    except Exception as e:
        print(f"DEBUG: Ошибка в show_character: {e}")
        await callback.answer("Произошла ошибка")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего действия"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нечего отменять. Используй /start для меню.")
        return
    
    await state.clear()
    await message.answer("Действие отменено. Используй /start для возврата в меню.")


@router.callback_query(F.data == "edit_character")
async def edit_character_menu(callback: CallbackQuery, state: FSMContext):
    """Меню редактирования"""
    await state.set_state(CharacterCreation.editing_sheet)
    character = await db.get_character(callback.from_user.id)
    char_text = format_character_sheet(character)
    
    await callback.message.edit_text(
        f"{char_text}\n\n<b>Выбери параметр для изменения:</b>",
        reply_markup=kb.get_sheet_edit_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("edit_"))
async def start_edit(callback: CallbackQuery, state: FSMContext):
    """Начало редактирования поля"""
    field_map = {
        "edit_name": ("name", "Введи новое имя:"),
        "edit_race": ("race", "Введи расу:"),
        "edit_class": ("class", "Введи класс:"),
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
    
    field, prompt = field_map.get(callback.data, (None, None))
    if field:
        await state.update_data(edit_field=field)
        await state.set_state(CharacterEdit.waiting_for_value)
        await callback.message.edit_text(prompt)
    
    await callback.answer()


@router.message(CharacterEdit.waiting_for_value)
async def process_edit(message: Message, state: FSMContext):
    """Обработка нового значения"""
    data = await state.get_data()
    field = data.get('edit_field')
    value = message.text
    
    numeric_fields = [
        'level', 'strength', 'dexterity', 'constitution', 'intelligence', 
        'wisdom', 'charisma', 'max_hp', 'current_hp', 'armor_class', 
        'initiative_bonus', 'speed', 'passive_perception', 'proficiency_bonus'
    ]
    
    try:
        if field in numeric_fields:
            value = int(value)
        
        await db.update_character(message.from_user.id, field, value)
        
        character = await db.get_character(message.from_user.id)
        char_text = format_character_sheet(character)
        
        await message.answer(
            f"✅ Обновлено!\n\n{char_text}",
            reply_markup=kb.get_character_menu()
        )
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введи число.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
        await state.clear()


@router.message()
async def unknown_message(message: Message):
    """Обработка неизвестных сообщений"""
    await message.answer(
        "Я не понимаю эту команду. Используй /start для открытия меню."
    )


@router.callback_query(F.data == "select_race")
async def show_race_selection(callback: CallbackQuery):
    """Показать выбор расы"""
    try:
        races = await get_races()
        await callback.message.edit_text(
            "🧬 Выбери расу для своего персонажа:",
            reply_markup=kb.get_race_selection_menu(races)
        )
    except Exception as e:
        print(f"Ошибка загрузки рас: {e}")
        # Fallback на статический список
        races = [
            {'index': 'human', 'name': 'Человек'},
            {'index': 'elf', 'name': 'Эльф'},
            {'index': 'dwarf', 'name': 'Дварф'},
            {'index': 'halfling', 'name': 'Полурослик'}
        ]
        await callback.message.edit_text(
            "🧬 Выбери расу для своего персонажа:",
            reply_markup=kb.get_race_selection_menu(races)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("select_race_"))
async def select_race(callback: CallbackQuery):
    """Выбор расы"""
    race_index = callback.data.replace("select_race_", "")
    
    try:
        race_info = await get_race_info(race_index)
        if race_info:
            await db.update_character(callback.from_user.id, "race", race_info['name'])
            
            # Обновляем скорость если есть
            if 'speed' in race_info:
                await db.update_character(callback.from_user.id, "speed", race_info['speed'])
            
            race_name = race_info['name']
        else:
            # Fallback
            race_names = {
                'human': 'Человек', 'elf': 'Эльф', 
                'dwarf': 'Дварф', 'halfling': 'Полурослик'
            }
            race_name = race_names.get(race_index, 'Человек')
            await db.update_character(callback.from_user.id, "race", race_name)
        
        # Очищаем старые расовые особенности и добавляем новые
        await db.clear_character_features_by_type(callback.from_user.id, 'racial')
        race_features = await get_race_features(race_index)
        
        for feature in race_features:
            await db.add_character_feature(
                callback.from_user.id,
                feature['name'],
                feature['description'],
                'racial',
                race_name
            )
        
    except Exception as e:
        print(f"Ошибка получения информации о расе: {e}")
        # Fallback
        race_names = {
            'human': 'Человек', 'elf': 'Эльф', 
            'dwarf': 'Дварф', 'halfling': 'Полурослик'
        }
        race_name = race_names.get(race_index, 'Человек')
        await db.update_character(callback.from_user.id, "race", race_name)
    
    character = await db.get_character(callback.from_user.id)
    features = await db.get_character_features(callback.from_user.id)
    char_text = await format_character_with_features(character, features)
    
    await callback.message.edit_text(
        f"✅ Раса изменена на {race_name}!\n\n{char_text}",
        reply_markup=kb.get_character_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "select_class")
async def show_class_selection(callback: CallbackQuery):
    """Показать выбор класса"""
    try:
        classes = await get_classes()
        await callback.message.edit_text(
            "⚔️ Выбери класс для своего персонажа:",
            reply_markup=kb.get_class_selection_menu(classes)
        )
    except Exception as e:
        print(f"Ошибка загрузки классов: {e}")
        # Fallback на статический список
        classes = [
            {'index': 'fighter', 'name': 'Воин'},
            {'index': 'wizard', 'name': 'Волшебник'},
            {'index': 'rogue', 'name': 'Плут'},
            {'index': 'cleric', 'name': 'Жрец'}
        ]
        await callback.message.edit_text(
            "⚔️ Выбери класс для своего персонажа:",
            reply_markup=kb.get_class_selection_menu(classes)
        )
    await callback.answer()


@router.callback_query(F.data.startswith("select_class_"))
async def select_class(callback: CallbackQuery):
    """Выбор класса"""
    class_index = callback.data.replace("select_class_", "")
    
    try:
        class_info = await get_class_info(class_index)
        character = await db.get_character(callback.from_user.id)
        
        if class_info:
            # Обновляем класс
            await db.update_character(callback.from_user.id, "class", class_info['name'])
            
            # Пересчитываем HP по классу
            con_mod = get_modifier(character['constitution'])
            new_hp = calculate_hp_by_class(class_index, character['level'], con_mod)
            await db.update_character(callback.from_user.id, "max_hp", new_hp)
            await db.update_character(callback.from_user.id, "current_hp", new_hp)
            
            class_name = class_info['name']
            hp_text = f"HP пересчитано: {new_hp}\n"
        else:
            # Fallback
            class_names = {
                'fighter': 'Воин', 'wizard': 'Волшебник',
                'rogue': 'Плут', 'cleric': 'Жрец'
            }
            class_name = class_names.get(class_index, 'Воин')
            await db.update_character(callback.from_user.id, "class", class_name)
            hp_text = ""
        
        # Очищаем старые классовые особенности и добавляем новые
        await db.clear_character_features_by_type(callback.from_user.id, 'class')
        class_features = await get_class_features(class_index, character['level'])
        
        for feature in class_features:
            await db.add_character_feature(
                callback.from_user.id,
                feature['name'],
                feature['description'],
                'class',
                class_name
            )
            
    except Exception as e:
        print(f"Ошибка получения информации о классе: {e}")
        # Fallback
        class_names = {
            'fighter': 'Воин', 'wizard': 'Волшебник',
            'rogue': 'Плут', 'cleric': 'Жрец'
        }
        class_name = class_names.get(class_index, 'Воин')
        await db.update_character(callback.from_user.id, "class", class_name)
        hp_text = ""
    
    character = await db.get_character(callback.from_user.id)
    features = await db.get_character_features(callback.from_user.id)
    char_text = await format_character_with_features(character, features)
    
    await callback.message.edit_text(
        f"✅ Класс изменен на {class_name}!\n{hp_text}\n{char_text}",
        reply_markup=kb.get_character_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "join_game")
async def join_game(callback: CallbackQuery):
    """Присоединиться к игре"""
    await callback.message.edit_text(
        "🎲 Функция присоединения к игре\n\n"
        "Эта функция будет реализована в Этапе 3.\n"
        "Здесь ты сможешь ввести код комнаты от Мастера.",
        reply_markup=kb.get_back_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "be_dm")
async def be_dm(callback: CallbackQuery):
    """Стать Мастером"""
    await callback.message.edit_text(
        "🎭 Функция создания комнаты Мастера\n\n"
        "Эта функция будет реализована в Этапе 3.\n"
        "Здесь ты получишь уникальный код для своей игровой сессии.",
        reply_markup=kb.get_back_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "delete_character")
async def confirm_delete(callback: CallbackQuery):
    """Подтверждение удаления"""
    await callback.message.edit_text(
        "⚠️ Ты уверен? Это действие нельзя отменить!",
        reply_markup=kb.get_confirm_delete()
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_delete")
async def delete_char(callback: CallbackQuery):
    """Удаление персонажа"""
    await db.delete_character(callback.from_user.id)
    await callback.message.edit_text(
        "🗑 Персонаж удален. Используй /start для создания нового."
    )
    await callback.answer()
