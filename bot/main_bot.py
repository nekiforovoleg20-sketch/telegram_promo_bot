import os
import logging
import sys
import sqlite3
import telegram
from datetime import datetime
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

# Добавляем путь к корню проекта для импорта database
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Загружаем переменные из .env
load_dotenv()

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен из .env
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# ========== БАЗА ДАННЫХ ==========

def get_db_connection():
    """Создаем соединение с базой данных"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'promo_bot.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_active_promocodes():
    """Получаем активные промокоды из базы"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM promocodes 
            WHERE is_active = 1 AND (expires_at IS NULL OR expires_at > DATE('now'))
            ORDER BY created_at DESC
        ''')
        promocodes = cursor.fetchall()
        conn.close()
        
        result = []
        for promo in promocodes:
            result.append({
                'id': promo['id'],
                'store': promo['store'],
                'code': promo['code'],
                'description': promo['description'],
                'expires_at': promo['expires_at']
            })
        return result
    except Exception as e:
        print(f"❌ Ошибка при получении промокодов: {e}")
        return []

def get_referral_channels():
    """Получаем каналы для реферальных ссылок"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM channels WHERE is_required = TRUE')
        channels = cursor.fetchall()
        conn.close()
        
        result = []
        for channel in channels:
            result.append({
                'id': channel['id'],
                'name': channel['name'],
                'username': channel['username']
            })
        return result
    except Exception as e:
        print(f"❌ Ошибка при получении каналов: {e}")
        return []

# ========== ОСНОВНЫЕ КОМАНДЫ ==========

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Получаем каналы для реферальных ссылок
    channels = get_referral_channels()
    channels_text = "\n".join([f"📢 {ch['name']} - https://t.me/{ch['username']}" for ch in channels])
    
    # Создаем кнопку для открытия мини-аппы
    keyboard = [
        [InlineKeyboardButton("🎁 Получить промокоды", web_app=WebAppInfo(url="https://amazing-druid-78b178.netlify.app/"))]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_html(
        f"Привет, {user.mention_html()}! 👋\n"
        "Я - твой Приятель Промокод! 🤖\n\n"
        "🎁 <b>Получи лучшие промокоды БЕСПЛАТНО!</b>\n\n"
        "👇 Жми кнопку ниже чтобы открыть все промокоды!",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Функция для команды /help"""
    help_text = """
🤖 **Помощь по боту:**

/start - Начать работу с ботом  
/help - Показать это сообщение
/promo - Показать ваш персональный промокод
/myid - Узнать свой ID

🎁 **Как получить промокоды:**
1. Нажми кнопку «Получить промокоды»
2. Выбирай любые промокоды из списка
3. Копируй и используй!

📢 **Поддержи нас:** подпишись на наши каналы по ссылкам из /start
    """
    await update.message.reply_text(help_text)

async def promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /promo - показывает фиксированный промокод для пользователя"""
    user_id = update.effective_user.id
    
    # Получаем активные промокоды
    promocodes = get_active_promocodes()
    
    if not promocodes:
        await update.message.reply_text("😔 Промокоды временно отсутствуют. Попробуй позже!")
        return
    
    # Создаем фиксированный промокод для пользователя на основе его ID
    # Это гарантирует, что пользователь всегда будет видеть один и тот же промокод
    promo_index = user_id % len(promocodes)
    promo = promocodes[promo_index]
    
    await update.message.reply_text(
        f"🎁 **Ваш персональный промокод:**\n\n"
        f"🏪 **Магазин:** {promo['store']}\n"
        f"🔑 **Промокод:** `{promo['code']}`\n"
        f"📝 **Описание:** {promo['description']}\n"
        f"📅 **Действует до:** {promo['expires_at']}\n\n"
        f"✨ Больше промокодов в мини-приложении!"
    )

async def myid_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает ID пользователя"""
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 Твой ID: `{user_id}`", parse_mode='MarkdownV2')

# ========== АДМИН-ПАНЕЛЬ ==========

def is_admin(user_id):
    """Проверяем, является ли пользователь администратором"""
    return user_id == ADMIN_ID

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /admin - показывает админ-панель"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав администратора")
        return
    
    admin_text = """
🔧 **Админ-панель**

📊 Статистика:
/stats - Статистика бота
/promo_stats - Статистика промокодов

🎁 Управление промокодами:
/add_promo - Добавить промокод
/delete_promo - Удалить промокод  
/list_promos - Список всех промокодов

📢 Управление каналами:
/add_channel - Добавить канал
/delete_channel - Удалить канал
/list_channels - Список каналов
    """
    await update.message.reply_text(admin_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /stats - показывает статистику (только для админа)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав для этой команды")
        return
    
    promocodes = get_active_promocodes()
    channels = get_referral_channels()
    
    await update.message.reply_text(
        f"📊 **Статистика бота:**\n\n"
        f"🎁 Активных промокодов: {len(promocodes)}\n"
        f"📢 Реферальных каналов: {len(channels)}\n"
        f"🔄 База данных: ✅ Работает\n\n"
        f"Для доступа ко всем промокодам используй мини-приложение!"
    )

async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /channels - показывает каналы (только для админа)"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав для этой команды")
        return
    
    channels = get_referral_channels()
    
    if not channels:
        await update.message.reply_text("📭 Нет каналов в базе")
        return
    
    text = "📢 **Наши каналы:**\n\n"
    for channel in channels:
        text += f"🔹 {channel['name']}\n"
        text += f"🔗 https://t.me/{channel['username']}\n\n"
    
    text += "❤️ Подпишись и поддержи нас!"
    
    await update.message.reply_text(text, disable_web_page_preview=True)

async def add_promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Добавление промокода"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав администратора")
        return
    
    if not context.args or len(context.args) < 4:
        await update.message.reply_text(
            "📝 Формат команды:\n"
            "`/add_promo магазин код описание дата`\n\n"
            "Пример:\n"
            "`/add_promo Wildberries SUMMER100 \"100 рублей скидка\" 2025-12-31`\n\n"
            "📌 Описание в кавычках если содержит пробелы!\n"
            "📅 Дата в формате: ГГГГ-ММ-ДД"
        )
        return
    
    try:
        store = context.args[0]
        code = context.args[1]
        description_parts = context.args[2:-1]
        description = ' '.join(description_parts)
        expires_at = context.args[-1]
        
        # Проверяем дату
        try:
            datetime.strptime(expires_at, '%Y-%m-%d')
        except ValueError:
            await update.message.reply_text(
                "❌ Неправильный формат даты. Используй: ГГГГ-ММ-ДД\n"
                "Пример: 2025-12-31"
            )
            return
        
        # Добавляем в базу
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO promocodes (store, code, description, expires_at, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (store, code, description, expires_at))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ Промокод добавлен!\n\n"
            f"🏪 Магазин: {store}\n"
            f"🔑 Код: `{code}`\n"
            f"📝 Описание: {description}\n"
            f"📅 Действует до: {expires_at}"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при добавлении: {str(e)}")

async def list_promos_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает все промокоды"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав администратора")
        return
    
    promocodes = get_active_promocodes()
    
    if not promocodes:
        await update.message.reply_text("📭 Нет активных промокодов")
        return
    
    text = "📋 **Все активные промокоды:**\n\n"
    for i, promo in enumerate(promocodes, 1):
        text += f"{i}. **{promo['store']}** (ID: {promo['id']})\n"
        text += f"   Код: `{promo['code']}`\n"
        text += f"   Описание: {promo['description']}\n"
        text += f"   Действует до: {promo['expires_at']}\n\n"
    
    if len(text) > 4000:
        parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for part in parts:
            await update.message.reply_text(part, parse_mode='Markdown')
    else:
        await update.message.reply_text(text, parse_mode='Markdown')

async def promo_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Статистика промокодов"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав администратора")
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM promocodes")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM promocodes WHERE is_active = 1")
    active = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM promocodes WHERE expires_at < DATE('now')")
    expired = cursor.fetchone()[0]
    
    cursor.execute('SELECT store, COUNT(*) as count FROM promocodes WHERE is_active = 1 GROUP BY store')
    by_store = cursor.fetchall()
    
    conn.close()
    
    text = f"""
📊 **Статистика промокодов:**

🎁 Всего промокодов: {total}
✅ Активных: {active}
❌ Просроченных: {expired}

🏪 По магазинам:
"""
    
    for store in by_store:
        text += f"   • {store['store']}: {store['count']}\n"
    
    await update.message.reply_text(text)

async def delete_promo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удаление промокода"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав администратора")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🗑 Формат команды:\n"
            "`/delete_promo ID_промокода`\n\n"
            "Чтобы узнать ID, используй /list_promos"
        )
        return
    
    try:
        promo_id = int(context.args[0])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM promocodes WHERE id = ?", (promo_id,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            await update.message.reply_text(f"✅ Промокод #{promo_id} удалён")
        else:
            await update.message.reply_text(f"❌ Промокод #{promo_id} не найден")
            
    except ValueError:
        await update.message.reply_text("❌ ID должен быть числом")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при удалении: {str(e)}")

async def add_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Добавление канала"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав администратора")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "📝 Формат команды:\n"
            "`/add_channel \"Название канала\" username`\n\n"
            "Пример:\n"
            "`/add_channel \"Мой канал\" mychannel`\n\n"
            "📌 Название в кавычках если содержит пробелы!\n"
            "🔗 Username без @"
        )
        return
    
    try:
        name = context.args[0].strip('"')
        username = context.args[1].lower().replace('@', '')
        
        # Добавляем в базу
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO channels (name, username, is_required)
            VALUES (?, ?, 1)
        ''', (name, username))
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"✅ Канал добавлен!\n\n"
            f"📢 Название: {name}\n"
            f"🔗 Username: @{username}\n"
            f"🌐 Ссылка: https://t.me/{username}"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при добавлении: {str(e)}")

async def delete_channel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Удаление канала"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав администратора")
        return
    
    if not context.args:
        await update.message.reply_text(
            "🗑 Формат команды:\n"
            "`/delete_channel ID_канала`\n\n"
            "Чтобы узнать ID, используй /list_channels"
        )
        return
    
    try:
        channel_id = int(context.args[0])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM channels WHERE id = ?", (channel_id,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            await update.message.reply_text(f"✅ Канал #{channel_id} удалён")
        else:
            await update.message.reply_text(f"❌ Канал #{channel_id} не найден")
            
    except ValueError:
        await update.message.reply_text("❌ ID должен быть числом")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при удалении: {str(e)}")

async def list_channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает все каналы"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("❌ У тебя нет прав администратора")
        return
    
    channels = get_referral_channels()
    
    if not channels:
        await update.message.reply_text("📭 Нет каналов в базе")
        return
    
    text = "📢 **Реферальные каналы:**\n\n"
    for i, channel in enumerate(channels, 1):
        text += f"{i}. **{channel['name']}** (ID: {channel['id']})\n"
        text += f"   Username: @{channel['username']}\n"
        text += f"   Ссылка: https://t.me/{channel['username']}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown', disable_web_page_preview=True)

# ========== МЕНЮ КОМАНД ==========

async def set_bot_commands(application: Application) -> None:
    """Устанавливаем меню команд для бота"""
    # Базовые команды для всех пользователей
    commands = [
        ("start", "Начать работу с ботом"),
        ("help", "Помощь по командам"),
        ("promo", "Получить промокод"),
        ("myid", "Узнать свой ID")
    ]
    
    await application.bot.set_my_commands(
        [telegram.BotCommand(command, description) for command, description in commands]
    )

# ========== ЗАПУСК БОТА ==========

def main() -> None:
    """Основная функция для запуска бота"""
    print("🔄 Запускаю бота...")
    
    # Проверяем подключение к базе
    print("🔍 Проверяем базу данных...")
    promocodes = get_active_promocodes()
    channels = get_referral_channels()
    
    print(f"✅ Найдено промокодов: {len(promocodes)}")
    print(f"✅ Найдено каналов: {len(channels)}")
    print(f"👑 Админ ID: {ADMIN_ID}")
    
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Устанавливаем меню команд
    application.post_init = lambda app: set_bot_commands(app)
    
    # Добавляем обработчики команд для всех пользователей
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("promo", promo_command))
    application.add_handler(CommandHandler("myid", myid_command))
    
    # Админ-команды (доступны только админу)
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("channels", channels_command))
    application.add_handler(CommandHandler("add_promo", add_promo_command))
    application.add_handler(CommandHandler("list_promos", list_promos_command))
    application.add_handler(CommandHandler("promo_stats", promo_stats_command))
    application.add_handler(CommandHandler("delete_promo", delete_promo_command))
    application.add_handler(CommandHandler("add_channel", add_channel_command))
    application.add_handler(CommandHandler("delete_channel", delete_channel_command))
    application.add_handler(CommandHandler("list_channels", list_channels_command))
    
    # Запускаем бота
    print("✅ Бот запущен! Проверяй в Telegram")
    print("📱 Меню команд должно появиться рядом с полем ввода")
    application.run_polling()

if __name__ == '__main__':
    main()