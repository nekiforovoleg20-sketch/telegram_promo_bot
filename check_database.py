import sqlite3
import os

def check_database():
    db_path = os.path.join('database', 'promo_bot.db')
    print(f"🔍 Проверяем базу данных: {db_path}")
    print(f"📁 Файл существует: {os.path.exists(db_path)}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Проверяем таблицу promocodes
    cursor.execute("SELECT * FROM promocodes")
    promocodes = cursor.fetchall()
    print(f"🎁 Все промокоды в базе: {len(promocodes)}")
    for promo in promocodes:
        print(f"   - {promo}")
    
    # Проверяем активные промокоды
    cursor.execute('''
        SELECT * FROM promocodes 
        WHERE is_active = 1 AND (expires_at IS NULL OR expires_at > DATE('now'))
    ''')
    active_promocodes = cursor.fetchall()
    print(f"✅ Активные промокоды: {len(active_promocodes)}")
    for promo in active_promocodes:
        print(f"   - {promo}")
    
    conn.close()

if __name__ == '__main__':
    check_database()