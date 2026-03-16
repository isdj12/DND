import aiohttp
import logging

logger = logging.getLogger(__name__)
BASE_URL = "https://www.dnd5eapi.co/api"

RACE_TRANSLATIONS = {
    "dragonborn": "Драконорожденный", "dwarf": "Дварф", "elf": "Эльф",
    "gnome": "Гном", "half-elf": "Полуэльф", "half-orc": "Полуорк",
    "halfling": "Полурослик", "human": "Человек", "tiefling": "Тифлинг"
}

CLASS_TRANSLATIONS = {
    "barbarian": "Варвар", "bard": "Бард", "cleric": "Жрец", "druid": "Друид",
    "fighter": "Воин", "monk": "Монах", "paladin": "Паладин", "ranger": "Следопыт",
    "rogue": "Плут", "sorcerer": "Чародей", "warlock": "Колдун", "wizard": "Волшебник"
}

FALLBACK_RACES = [
    {'index': 'human', 'name': 'Человек'}, {'index': 'elf', 'name': 'Эльф'},
    {'index': 'dwarf', 'name': 'Дварф'}, {'index': 'halfling', 'name': 'Полурослик'},
    {'index': 'dragonborn', 'name': 'Драконорожденный'}, {'index': 'gnome', 'name': 'Гном'},
    {'index': 'half-elf', 'name': 'Полуэльф'}, {'index': 'half-orc', 'name': 'Полуорк'},
    {'index': 'tiefling', 'name': 'Тифлинг'}
]

FALLBACK_CLASSES = [
    {'index': 'fighter', 'name': 'Воин'}, {'index': 'wizard', 'name': 'Волшебник'},
    {'index': 'rogue', 'name': 'Плут'}, {'index': 'cleric', 'name': 'Жрец'},
    {'index': 'barbarian', 'name': 'Варвар'}, {'index': 'bard', 'name': 'Бард'},
    {'index': 'druid', 'name': 'Друид'}, {'index': 'monk', 'name': 'Монах'},
    {'index': 'paladin', 'name': 'Паладин'}, {'index': 'ranger', 'name': 'Следопыт'},
    {'index': 'sorcerer', 'name': 'Чародей'}, {'index': 'warlock', 'name': 'Колдун'}
]

LOCAL_RACE_FEATURES = {
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
        {'name': 'Боевая подготовка', 'description': 'Владение боевыми топорами, ручными топорами, молотами'}
    ],
    'halfling': [
        {'name': 'Удачливый', 'description': 'Можешь перебросить 1 на d20'},
        {'name': 'Храбрый', 'description': 'Преимущество на спасброски от испуга'},
        {'name': 'Проворство', 'description': 'Можешь проходить через пространство существ на размер больше'}
    ],
    'dragonborn': [
        {'name': 'Драконье происхождение', 'description': 'Выбираешь тип дракона, определяющий дыхательное оружие'},
        {'name': 'Дыхательное оружие', 'description': 'Можешь выдохнуть разрушительную энергию'},
        {'name': 'Сопротивление урону', 'description': 'Сопротивление типу урона своего происхождения'}
    ],
    'gnome': [
        {'name': 'Темное зрение', 'description': 'Видишь в темноте на 60 футов'},
        {'name': 'Гномья хитрость', 'description': 'Преимущество на спасброски Интеллекта, Мудрости и Харизмы от магии'}
    ],
    'half-elf': [
        {'name': 'Темное зрение', 'description': 'Видишь в темноте на 60 футов'},
        {'name': 'Наследие фей', 'description': 'Преимущество на спасброски от очарования'},
        {'name': 'Универсальность навыков', 'description': 'Владение двумя навыками на выбор'}
    ],
    'half-orc': [
        {'name': 'Темное зрение', 'description': 'Видишь в темноте на 60 футов'},
        {'name': 'Непоколебимость', 'description': 'Когда тебя должны убить, остаешься с 1 HP (1 раз в день)'},
        {'name': 'Свирепые атаки', 'description': 'Дополнительный кубик урона при критическом ударе'}
    ],
    'tiefling': [
        {'name': 'Темное зрение', 'description': 'Видишь в темноте на 60 футов'},
        {'name': 'Адское сопротивление', 'description': 'Сопротивление урону огнем'},
        {'name': 'Адское наследие', 'description': 'Знаешь заговор Огонь в руке'}
    ]
}

LOCAL_CLASS_FEATURES = {
    'fighter': [
        {'name': 'Боевой стиль', 'description': 'Специализация в определенном стиле боя'},
        {'name': 'Второе дыхание', 'description': 'Восстанавливаешь хиты бонусным действием в бою'}
    ],
    'wizard': [
        {'name': 'Заклинания', 'description': 'Творишь заклинания из книги заклинаний'},
        {'name': 'Восстановление заклинаний', 'description': 'Восстанавливаешь ячейки заклинаний на коротком отдыхе'}
    ],
    'rogue': [
        {'name': 'Экспертиза', 'description': 'Удваиваешь бонус мастерства для двух навыков'},
        {'name': 'Скрытая атака', 'description': 'Дополнительный урон при атаке с преимуществом'},
        {'name': 'Воровской жаргон', 'description': 'Знаешь тайный язык воров'}
    ],
    'cleric': [
        {'name': 'Заклинания', 'description': 'Творишь божественные заклинания'},
        {'name': 'Божественный домен', 'description': 'Выбираешь домен, определяющий способности'},
        {'name': 'Ритуальное колдовство', 'description': 'Можешь творить заклинания как ритуалы'}
    ],
    'barbarian': [
        {'name': 'Ярость', 'description': 'Входишь в состояние ярости, получая бонусы к атаке и урону'},
        {'name': 'Защита без доспехов', 'description': 'AC = 10 + мод. Ловкости + мод. Телосложения'}
    ],
    'bard': [
        {'name': 'Заклинания', 'description': 'Творишь заклинания через музыку и слова'},
        {'name': 'Бардовское вдохновение', 'description': 'Даешь союзнику кубик вдохновения'}
    ],
    'druid': [
        {'name': 'Заклинания', 'description': 'Творишь заклинания природы'},
        {'name': 'Дикий облик', 'description': 'Превращаешься в животное'}
    ],
    'monk': [
        {'name': 'Боевые искусства', 'description': 'Особые удары без оружия'},
        {'name': 'Очки ки', 'description': 'Используешь ки для особых способностей'}
    ],
    'paladin': [
        {'name': 'Божественное чувство', 'description': 'Чувствуешь присутствие зла и добра'},
        {'name': 'Наложение рук', 'description': 'Исцеляешь касанием'}
    ],
    'ranger': [
        {'name': 'Избранный враг', 'description': 'Бонус к урону против определенного типа существ'},
        {'name': 'Природный исследователь', 'description': 'Бонусы в определенной местности'}
    ],
    'sorcerer': [
        {'name': 'Заклинания', 'description': 'Врожденная магия'},
        {'name': 'Источник магии', 'description': 'Очки чародейства для усиления заклинаний'}
    ],
    'warlock': [
        {'name': 'Покровитель', 'description': 'Заключаешь договор с могущественным существом'},
        {'name': 'Магия договора', 'description': 'Заклинания, восстанавливаемые на коротком отдыхе'}
    ]
}


async def get_races():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/races") as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {'index': r['index'], 'name': RACE_TRANSLATIONS.get(r['index'], r['name'])}
                        for r in data.get('results', [])
                    ]
    except Exception as e:
        logger.error(f"Ошибка получения рас: {e}")
    return FALLBACK_RACES


async def get_classes():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/classes") as response:
                if response.status == 200:
                    data = await response.json()
                    return [
                        {'index': c['index'], 'name': CLASS_TRANSLATIONS.get(c['index'], c['name'])}
                        for c in data.get('results', [])
                    ]
    except Exception as e:
        logger.error(f"Ошибка получения классов: {e}")
    return FALLBACK_CLASSES


async def get_race_info(race_index: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/races/{race_index}") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'name': RACE_TRANSLATIONS.get(race_index, data['name']),
                        'speed': data.get('speed', 30),
                        'ability_bonuses': data.get('ability_bonuses', [])
                    }
    except Exception as e:
        logger.error(f"Ошибка получения расы {race_index}: {e}")
    return None


async def get_class_info(class_index: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/classes/{class_index}") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'name': CLASS_TRANSLATIONS.get(class_index, data['name']),
                        'hit_die': data.get('hit_die', 8)
                    }
    except Exception as e:
        logger.error(f"Ошибка получения класса {class_index}: {e}")
    return None


def calculate_hp_by_class(class_index: str, level: int = 1, con_modifier: int = 0):
    hit_dice = {
        'barbarian': 12, 'fighter': 10, 'paladin': 10, 'ranger': 10,
        'bard': 8, 'cleric': 8, 'druid': 8, 'monk': 8, 'rogue': 8, 'warlock': 8,
        'sorcerer': 6, 'wizard': 6
    }
    hd = hit_dice.get(class_index, 8)
    return hd + con_modifier + (level - 1) * (hd // 2 + 1 + con_modifier)


async def get_race_features(race_index: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/races/{race_index}") as response:
                if response.status == 200:
                    data = await response.json()
                    features = [
                        {'name': t.get('name', ''), 'description': t.get('desc', [''])[0] if t.get('desc') else ''}
                        for t in data.get('traits', [])
                    ]
                    if features:
                        return features
    except Exception as e:
        logger.error(f"Ошибка получения особенностей расы {race_index}: {e}")
    return LOCAL_RACE_FEATURES.get(race_index, [])


async def get_class_features(class_index: str, level: int = 1):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/classes/{class_index}/levels/{level}") as response:
                if response.status == 200:
                    data = await response.json()
                    features = [
                        {'name': f.get('name', ''), 'description': f.get('desc', [''])[0] if f.get('desc') else ''}
                        for f in data.get('features', [])
                    ]
                    if features:
                        return features
    except Exception as e:
        logger.error(f"Ошибка получения особенностей класса {class_index}: {e}")
    return LOCAL_CLASS_FEATURES.get(class_index, [])
