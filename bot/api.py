from flask import Flask, request, jsonify
from database.db import get_active_promocodes, get_required_channels
import sqlite3
import os
from telegram import Bot
import asyncio

app = Flask(__name__)
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Функция для проверки подписки пользователя на канал
async def check_user_subscription(user_id, channel_username):
    try:
        bot = Bot(token=BOT_TOKEN)
        chat_member = await bot.get_chat_member(f"@{channel_username}", user_id)
        return chat_member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

# API endpoint для получения промокодов
@app.route('/api/promocodes', methods=['GET'])
def api_promocodes():
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    # Получаем обязательные каналы
    required_channels = get_required_channels()
    
    # Проверяем подписки (пока заглушка - всегда True)
    # В реальности нужно асинхронно проверять каждый канал
    all_subscribed = True
    
    promocodes = get_active_promocodes()
    
    # Форматируем промокоды для JSON
    promocodes_list = []
    for promo in promocodes:
        promocodes_list.append({
            'id': promo[0],
            'store': promo[1],
            'code': promo[2],
            'description': promo[3],
            'expires_at': promo[4]
        })
    
    # Форматируем каналы для JSON
    channels_list = []
    for channel in required_channels:
        channels_list.append({
            'id': channel[0],
            'name': channel[1],
            'username': channel[2]
        })
    
    return jsonify({
        'access': all_subscribed,
        'promocodes': promocodes_list if all_subscribed else [],
        'channels': channels_list
    })

# API endpoint для проверки подписок
@app.route('/api/check_subscriptions', methods=['POST'])
def api_check_subscriptions():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    required_channels = get_required_channels()
    
    # Здесь будет реальная проверка подписок
    # Пока возвращаем успех для теста
    return jsonify({
        'subscribed': True,
        'message': 'Все подписки подтверждены!'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)