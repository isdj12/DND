import aiosqlite
import logging

logger = logging.getLogger(__name__)

DB_PATH = "database.db"


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                role TEXT DEFAULT 'player',
                room_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица персонажей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                race TEXT,
                class TEXT,
                level INTEGER DEFAULT 1,
                
                -- Характеристики
                strength INTEGER DEFAULT 10,
                dexterity INTEGER DEFAULT 10,
                constitution INTEGER DEFAULT 10,
                intelligence INTEGER DEFAULT 10,
                wisdom INTEGER DEFAULT 10,
                charisma INTEGER DEFAULT 10,
                
                -- Боевые характеристики
                max_hp INTEGER DEFAULT 10,
                current_hp INTEGER DEFAULT 10,
                armor_class INTEGER DEFAULT 10,
                initiative_bonus INTEGER DEFAULT 0,
                speed INTEGER DEFAULT 30,
                
                -- Навыки и восприятие
                passive_perception INTEGER DEFAULT 10,
                proficiency_bonus INTEGER DEFAULT 2,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Таблица комнат (для Мастеров)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_code TEXT PRIMARY KEY,
                dm_user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (dm_user_id) REFERENCES users(user_id)
            )
        """)
        
        # Таблица особенностей персонажа
        await db.execute("""
            CREATE TABLE IF NOT EXISTS character_features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feature_name TEXT NOT NULL,
                feature_description TEXT,
                feature_type TEXT, -- 'racial', 'class', 'custom'
                source TEXT, -- откуда получена особенность
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)


async def get_user(user_id: int):
    """Получить пользователя по ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()


async def create_user(user_id: int, role: str = "player"):
    """Создать нового пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, role) VALUES (?, ?)",
            (user_id, role)
        )
        await db.commit()


async def get_character(user_id: int):
    """Получить персонажа пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM characters WHERE user_id = ? LIMIT 1",
            (user_id,)
        ) as cursor:
            return await cursor.fetchone()


async def create_character(user_id: int, char_data: dict):
    """Создать персонажа"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO characters (
                user_id, name, race, class, level,
                strength, dexterity, constitution, intelligence, wisdom, charisma,
                max_hp, current_hp, armor_class, initiative_bonus, speed,
                passive_perception, proficiency_bonus
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id, char_data['name'], char_data['race'], char_data['class'], char_data.get('level', 1),
                char_data.get('strength', 10), char_data.get('dexterity', 10), 
                char_data.get('constitution', 10), char_data.get('intelligence', 10),
                char_data.get('wisdom', 10), char_data.get('charisma', 10),
                char_data.get('max_hp', 10), char_data.get('current_hp', 10),
                char_data.get('armor_class', 10), char_data.get('initiative_bonus', 0),
                char_data.get('speed', 30), char_data.get('passive_perception', 10),
                char_data.get('proficiency_bonus', 2)
            )
        )
        await db.commit()


async def update_character(user_id: int, field: str, value):
    """Обновить поле персонажа"""
    allowed_fields = [
        "name", "race", "class", "level",
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
        "max_hp", "current_hp", "armor_class", "initiative_bonus", "speed",
        "passive_perception", "proficiency_bonus"
    ]
    if field not in allowed_fields:
        raise ValueError(f"Недопустимое поле: {field}")
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE characters SET {field} = ? WHERE user_id = ?",
            (value, user_id)
        )
        await db.commit()


async def delete_character(user_id: int):
    """Удалить персонажа"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM characters WHERE user_id = ?", (user_id,))
        await db.commit()


async def add_character_feature(user_id: int, name: str, description: str, feature_type: str, source: str):
    """Добавить особенность персонажу"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """INSERT INTO character_features (user_id, feature_name, feature_description, feature_type, source)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, name, description, feature_type, source)
        )
        await db.commit()


async def get_character_features(user_id: int):
    """Получить все особенности персонажа"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM character_features WHERE user_id = ? ORDER BY feature_type, feature_name",
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()


async def clear_character_features_by_type(user_id: int, feature_type: str):
    """Удалить особенности определенного типа"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM character_features WHERE user_id = ? AND feature_type = ?",
            (user_id, feature_type)
        )
        await db.commit()


async def clear_all_character_features(user_id: int):
    """Удалить все особенности персонажа"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM character_features WHERE user_id = ?", (user_id,))
        await db.commit()