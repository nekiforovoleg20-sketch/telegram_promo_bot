import sqlite3
import os

def fix_dates():
    db_path = os.path.join(os.path.dirname(__file__), 'promo_bot.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Обновляем все даты на 2025 год
    cursor.execute("UPDATE promocodes SET expires_at = '2025-12-31'")
    
    # Проверяем обновление
    cursor.execute("SELECT COUNT(*) FROM promocodes WHERE expires_at = '2025-12-31'")
    updated_count = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    print(f"✅ Обновлено {updated_count} промокодов. Новые даты: 2025-12-31")

if __name__ == '__main__':
    fix_dates()