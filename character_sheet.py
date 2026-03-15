"""Утилиты для работы с листом персонажа"""


def get_modifier(stat: int) -> int:
    """Вычислить модификатор характеристики"""
    return (stat - 10) // 2


def format_modifier(value: int) -> str:
    """Форматировать модификатор со знаком"""
    return f"+{value}" if value >= 0 else str(value)


def format_character_sheet(char) -> str:
    """Форматировать полный лист персонажа"""
    # Модификаторы характеристик
    str_mod = get_modifier(char['strength'])
    dex_mod = get_modifier(char['dexterity'])
    con_mod = get_modifier(char['constitution'])
    int_mod = get_modifier(char['intelligence'])
    wis_mod = get_modifier(char['wisdom'])
    cha_mod = get_modifier(char['charisma'])
    
    sheet = f"""
🎭 <b>{char['name']}</b>
{char['race']} | {char['class']} | Уровень {char['level']}

━━━━━━━━━━━━━━━━━━━━
⚔️ <b>БОЕВЫЕ ХАРАКТЕРИСТИКИ</b>
❤️ HP: {char['current_hp']}/{char['max_hp']}
🛡 AC: {char['armor_class']}
⚡️ Инициатива: {format_modifier(char['initiative_bonus'])}
🏃 Скорость: {char['speed']} фт.

━━━━━━━━━━━━━━━━━━━━
📊 <b>ХАРАКТЕРИСТИКИ</b>
💪 Сила: {char['strength']} ({format_modifier(str_mod)})
🤸 Ловкость: {char['dexterity']} ({format_modifier(dex_mod)})
🫀 Телосложение: {char['constitution']} ({format_modifier(con_mod)})
🧠 Интеллект: {char['intelligence']} ({format_modifier(int_mod)})
🦉 Мудрость: {char['wisdom']} ({format_modifier(wis_mod)})
✨ Харизма: {char['charisma']} ({format_modifier(cha_mod)})

━━━━━━━━━━━━━━━━━━━━
🎯 <b>НАВЫКИ</b>
👁 Пассивное восприятие: {char['passive_perception']}
⭐️ Бонус мастерства: +{char['proficiency_bonus']}
"""
    return sheet.strip()


async def format_character_with_features(char, features) -> str:
    """Форматировать лист персонажа с особенностями"""
    base_sheet = format_character_sheet(char)
    
    if not features:
        return base_sheet
    
    # Группируем особенности по типам
    racial_features = [f for f in features if f['feature_type'] == 'racial']
    class_features = [f for f in features if f['feature_type'] == 'class']
    
    features_text = ""
    
    if racial_features:
        features_text += "\n\n━━━━━━━━━━━━━━━━━━━━\n🧬 <b>РАСОВЫЕ ОСОБЕННОСТИ</b>\n"
        for feature in racial_features:
            features_text += f"• <b>{feature['feature_name']}</b>\n"
            if feature['feature_description']:
                features_text += f"  {feature['feature_description']}\n"
    
    if class_features:
        features_text += "\n━━━━━━━━━━━━━━━━━━━━\n⚔️ <b>КЛАССОВЫЕ ОСОБЕННОСТИ</b>\n"
        for feature in class_features:
            features_text += f"• <b>{feature['feature_name']}</b>\n"
            if feature['feature_description']:
                features_text += f"  {feature['feature_description']}\n"
    
    return base_sheet + features_text


def format_character_short(char) -> str:
    """Краткая карточка персонажа"""
    return (
        f"🎭 <b>{char['name']}</b>\n"
        f"{char['race']} {char['class']} {char['level']} ур.\n"
        f"❤️ {char['current_hp']}/{char['max_hp']} HP | 🛡 {char['armor_class']} AC"
    )
