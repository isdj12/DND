"""Интеграция с D&D 5e API"""
import aiohttp
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.dnd5eapi.co/api"

# Переводы на русский
RACE_TRANSLATIONS = {
    "dragonborn": "Драконорожденный",
    "dwarf": "Дварф", 
    "elf": "Эльф",
    "gnome": "Гном",
    "half-elf": "Полуэльф",
    "half-orc": "Полуорк",
    "halfling": "Полурослик",
    "human": "Человек",
    "tiefling": "Тифлинг"
}

CLASS_TRANSLATIONS = {
    "barbarian": "Варвар",
    "bard": "Бард",
    "cleric": "Жрец",
    "druid": "Друид",
    "fighter": "Воин",
    "monk": "Монах",
    "paladin": "Паладин",
    "ranger": "Следопыт",
    "rogue": "Плут",
    "sorcerer": "Чародей",
    "warlock": "Колдун",
    "wizard": "Волшебник"
}


async def get_races():
    """Получить список рас"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/races") as response:
                if response.status == 200:
                    data = await response.json()
                    races = []
                    for race in data.get('results', []):
                        name_en = race['index']
                        name_ru = RACE_TRANSLATIONS.get(name_en, race['name'])
                        races.append({
                            'index': name_en,
                            'name': name_ru,
                            'name_en': race['name']
                        })
                    return races
    except Exception as e:
        logger.error(f"Ошибка получения рас: {e}")
    
    # Fallback - базовые расы
    return [
        {'index': 'human', 'name': 'Человек', 'name_en': 'Human'},
        {'index': 'elf', 'name': 'Эльф', 'name_en': 'Elf'},
        {'index': 'dwarf', 'name': 'Дварф', 'name_en': 'Dwarf'},
        {'index': 'halfling', 'name': 'Полурослик', 'name_en': 'Halfling'}
    ]


async def get_classes():
    """Получить список классов"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/classes") as response:
                if response.status == 200:
                    data = await response.json()
                    classes = []
                    for cls in data.get('results', []):
                        name_en = cls['index']
                        name_ru = CLASS_TRANSLATIONS.get(name_en, cls['name'])
                        classes.append({
                            'index': name_en,
                            'name': name_ru,
                            'name_en': cls['name']
                        })
                    return classes
    except Exception as e:
        logger.error(f"Ошибка получения классов: {e}")
    
    # Fallback - базовые классы
    return [
        {'index': 'fighter', 'name': 'Воин', 'name_en': 'Fighter'},
        {'index': 'wizard', 'name': 'Волшебник', 'name_en': 'Wizard'},
        {'index': 'rogue', 'name': 'Плут', 'name_en': 'Rogue'},
        {'index': 'cleric', 'name': 'Жрец', 'name_en': 'Cleric'}
    ]


async def get_race_info(race_index: str):
    """Получить подробную информацию о расе"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/races/{race_index}") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'name': RACE_TRANSLATIONS.get(race_index, data['name']),
                        'size': data.get('size', 'Medium'),
                        'speed': data.get('speed', 30),
                        'ability_bonuses': data.get('ability_bonuses', []),
                        'traits': data.get('traits', [])
                    }
    except Exception as e:
        logger.error(f"Ошибка получения информации о расе {race_index}: {e}")
    return None


async def get_class_info(class_index: str):
    """Получить подробную информацию о классе"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/classes/{class_index}") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'name': CLASS_TRANSLATIONS.get(class_index, data['name']),
                        'hit_die': data.get('hit_die', 8),
                        'primary_ability': data.get('primary_ability', []),
                        'saving_throws': data.get('saving_throw_proficiencies', []),
                        'proficiencies': data.get('proficiencies', [])
                    }
    except Exception as e:
        logger.error(f"Ошибка получения информации о классе {class_index}: {e}")
    return None


def calculate_hp_by_class(class_index: str, level: int = 1, con_modifier: int = 0):
    """Рассчитать HP по классу"""
    hit_dice = {
        'barbarian': 12, 'fighter': 10, 'paladin': 10, 'ranger': 10,
        'bard': 8, 'cleric': 8, 'druid': 8, 'monk': 8, 'rogue': 8, 'warlock': 8,
        'sorcerer': 6, 'wizard': 6
    }
    
    base_hp = hit_dice.get(class_index, 8)
    return base_hp + con_modifier + (level - 1) * (hit_dice.get(class_index, 8) // 2 + 1 + con_modifier)


async def get_race_features(race_index: str):
    """Получить особенности расы"""
    race_features = {
        'human': [
            {'name': 'Дополнительный навык', 'description': 'Получаешь владение одним навыком на выбор'},
            {'name': 'Дополнительный язык', 'description': 'Знаешь один дополнительный язык'},
            {'name': 'Универсальность', 'description': '+1 ко всем характеристикам'}
        ],
        'elf': [
            {'name': 'Темное зрение', 'description': 'Видишь в темноте на 60 футов'},
            {'name': 'Острые чувства', 'description': 'Владение навыком Восприятие'},
            {'name': 'Наследие фей', 'description': 'Преимущество на спасброски от очарования'},
            {'name': 'Транс', 'description': 'Не нужно спать, достаточно 4 часов медитации'}
        ],
        'dwarf': [
            {'name': 'Темное зрение', 'description': 'Видишь в темноте на 60 футов'},
            {'name': 'Стойкость дварфов', 'description': 'Преимущество на спасброски от яда'},
            {'name': 'Знание камня', 'description': 'Удваиваешь бонус мастерства для проверок Истории, связанных с камнем'},
            {'name': 'Боевая подготовка', 'description': 'Владение боевыми топорами, ручными топорами, легкими и боевыми молотами'}
        ],
        'halfling': [
            {'name': 'Удачливый', 'description': 'Можешь перебросить 1 на d20, должен использовать новый результат'},
            {'name': 'Храбрый', 'description': 'Преимущество на спасброски от испуга'},
            {'name': 'Проворство полуросликов', 'description': 'Можешь проходить через пространство существ на размер больше тебя'}
        ],
        'dragonborn': [
            {'name': 'Драконье происхождение', 'description': 'Выбираешь тип дракона, определяющий дыхательное оружие'},
            {'name': 'Дыхательное оружие', 'description': 'Можешь выдохнуть разрушительную энергию'},
            {'name': 'Сопротивление урону', 'description': 'Сопротивление типу урона, связанному с твоим драконьим происхождением'}
        ]
    }
    
    try:
        # Пытаемся получить из API
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/races/{race_index}") as response:
                if response.status == 200:
                    data = await response.json()
                    api_features = []
                    for trait in data.get('traits', []):
                        api_features.append({
                            'name': trait.get('name', ''),
                            'description': trait.get('desc', [''])[0] if trait.get('desc') else ''
                        })
                    if api_features:
                        return api_features
    except Exception as e:
        logger.error(f"Ошибка получения особенностей расы из API: {e}")
    
    # Fallback на локальные данные
    return race_features.get(race_index, [])


async def get_class_features(class_index: str, level: int = 1):
    """Получить особенности класса"""
    class_features = {
        'fighter': [
            {'name': 'Боевой стиль', 'description': 'Выбираешь специализацию в определенном стиле боя'},
            {'name': 'Второе дыхание', 'description': 'Можешь восстановить хиты в бою'}
        ],
        'wizard': [
            {'name': 'Заклинания', 'description': 'Можешь творить заклинания из книги заклинаний'},
            {'name': 'Восстановление заклинаний', 'description': 'Восстанавливаешь часть ячеек заклинаний на коротком отдыхе'}
        ],
        'rogue': [
            {'name': 'Экспертиза', 'description': 'Удваиваешь бонус мастерства для двух навыков'},
            {'name': 'Скрытая атака', 'description': 'Наносишь дополнительный урон при атаке с преимуществом'},
            {'name': 'Воровской жаргон', 'description': 'Знаешь воровской жаргон и тайные знаки'}
        ],
        'cleric': [
            {'name': 'Заклинания', 'description': 'Можешь творить божественные заклинания'},
            {'name': 'Божественный домен', 'description': 'Выбираешь домен, определяющий твои способности'},
            {'name': 'Ритуальное колдовство', 'description': 'Можешь творить заклинания как ритуалы'}
        ]
    }
    
    try:
        # Пытаемся получить из API
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/classes/{class_index}/levels/{level}") as response:
                if response.status == 200:
                    data = await response.json()
                    api_features = []
                    for feature in data.get('features', []):
                        api_features.append({
                            'name': feature.get('name', ''),
                            'description': feature.get('desc', [''])[0] if feature.get('desc') else ''
                        })
                    if api_features:
                        return api_features
    except Exception as e:
        logger.error(f"Ошибка получения особенностей класса из API: {e}")
    
    # Fallback на локальные данные
    return class_features.get(class_index, [])