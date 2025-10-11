import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'promo_bot.db')

def init_db():
    """Создаём таблицы в базе данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица промокодов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            store TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT,
            expires_at DATE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица каналов для подписки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            is_required BOOLEAN DEFAULT TRUE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

def add_sample_data():
    """Добавляем тестовые данные (20 промокодов)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Очищаем старые данные
    cursor.execute("DELETE FROM promocodes")
    cursor.execute("DELETE FROM channels")
    
    # Добавляем тестовые каналы
    channels = [
        ("Выгодные предложения", "promo_channel_1", True),
        ("Промокоды дня", "promo_channel_2", True),
        ("Скидки и акции", "promo_channel_3", True)
    ]
    
    cursor.executemany('''
        INSERT INTO channels (name, username, is_required)
        VALUES (?, ?, ?)
    ''', channels)
    
    # Добавляем 20 тестовых промокодов
    promocodes = [
        ("Wildberries", "WBNEW25", "Скидка 25% на первый заказ", "2026-01-31"),
    ("Ozon", "OZONFRESH10", "10% на товары для дома", "2025-12-20"),
    ("AliExpress", "ALIWOW5", "5% скидка на всё", "2026-02-15"),
    ("Lamoda", "STYLE20", "20% на одежду и обувь", "2025-11-30"),
    ("Яндекс.Маркет", "MARKET300", "−300₽ при заказе от 2000₽", "2025-12-31"),
    ("СберМегаМаркет", "SBERFEST", "15% скидка на электронику", "2026-01-10"),
    ("KFC", "CRISPY50", "50% на второе комбо", "2025-10-30"),
    ("Burger King", "BKFREE", "Бесплатный напиток при заказе бургера", "2025-12-01"),
    ("McDonald's", "MCBONUS", "Бесплатный десерт к завтраку", "2025-11-10"),
    ("Пятёрочка", "PYATA5", "5% на продукты недели", "2025-10-25"),
    ("Лента", "LENTA200", "200₽ при покупке от 1500₽", "2026-01-15"),
    ("Магнит", "MAGNIT2025", "−10% на бакалею", "2025-12-05"),
    ("Додо Пицца", "DODO2025", "−25% на большую пиццу", "2025-11-15"),
    ("Subway", "EATFRESH", "2 по цене 1", "2025-12-31"),
    ("Starbucks", "COFFEELOVE", "Бесплатный допинг к любому кофе", "2025-11-20"),
    ("Adidas", "SPORT25", "25% скидка на новые коллекции", "2026-03-01"),
    ("Nike", "JUSTDO10", "10% на всё", "2025-12-10"),
    ("Reebok", "FITNESS15", "15% на спортивную обувь", "2025-12-25"),
    ("Rive Gauche", "BEAUTY20", "20% на косметику", "2025-11-30"),
    ("Л’Этуаль", "PARFUM25", "25% на ароматы", "2025-12-31")
    ]
    
    cursor.executemany('''
        INSERT INTO promocodes (store, code, description, expires_at, is_active)
        VALUES (?, ?, ?, ?, 1)
    ''', promocodes)
    
    conn.commit()
    conn.close()
    print("✅ Тестовые данные добавлены (20 промокодов)")

def get_active_promocodes():
    """Получаем активные промокоды"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM promocodes 
        WHERE is_active = TRUE AND (expires_at IS NULL OR expires_at > DATE('now'))
        ORDER BY created_at DESC
    ''')
    promocodes = cursor.fetchall()
    conn.close()
    return promocodes

def get_required_channels():
    """Получаем обязательные каналы для подписки"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM channels WHERE is_required = TRUE')
    channels = cursor.fetchall()
    conn.close()
    return channels

# Инициализируем базу при импорте
init_db()
add_sample_data()