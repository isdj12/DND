def get_modifier(stat: int) -> int:
    return (stat - 10) // 2


def format_modifier(value: int) -> str:
    return f"+{value}" if value >= 0 else str(value)


def format_character_sheet(char) -> str:
    str_mod = get_modifier(char['strength'])
    dex_mod = get_modifier(char['dexterity'])
    con_mod = get_modifier(char['constitution'])
    int_mod = get_modifier(char['intelligence'])
    wis_mod = get_modifier(char['wisdom'])
    cha_mod = get_modifier(char['charisma'])

    return (
        f"🎭 <b>{char['name']}</b>\n"
        f"{char['race']} | {char['class']} | Уровень {char['level']}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚔️ <b>БОЕВЫЕ ХАРАКТЕРИСТИКИ</b>\n"
        f"❤️ HP: {char['current_hp']}/{char['max_hp']}\n"
        f"🛡 AC: {char['armor_class']}\n"
        f"⚡️ Инициатива: {format_modifier(char['initiative_bonus'])}\n"
        f"🏃 Скорость: {char['speed']} фт.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>ХАРАКТЕРИСТИКИ</b>\n"
        f"💪 Сила: {char['strength']} ({format_modifier(str_mod)})\n"
        f"🤸 Ловкость: {char['dexterity']} ({format_modifier(dex_mod)})\n"
        f"🫀 Телосложение: {char['constitution']} ({format_modifier(con_mod)})\n"
        f"🧠 Интеллект: {char['intelligence']} ({format_modifier(int_mod)})\n"
        f"🦉 Мудрость: {char['wisdom']} ({format_modifier(wis_mod)})\n"
        f"✨ Харизма: {char['charisma']} ({format_modifier(cha_mod)})\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 <b>НАВЫКИ</b>\n"
        f"👁 Пассивное восприятие: {char['passive_perception']}\n"
        f"⭐️ Бонус мастерства: +{char['proficiency_bonus']}"
    )


async def format_character_with_features(char, features) -> str:
    base_sheet = format_character_sheet(char)
    if not features:
        return base_sheet

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
    return (
        f"🎭 <b>{char['name']}</b>\n"
        f"{char['race']} {char['class']} {char['level']} ур.\n"
        f"❤️ {char['current_hp']}/{char['max_hp']} HP | 🛡 {char['armor_class']} AC"
    )
