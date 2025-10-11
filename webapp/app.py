from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

@app.route('/<path:filename>')
def serve_file(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    print("🚀 Запускаю веб-сервер для мини-аппы...")
    print("📱 Мини-аппа доступна по адресу: http://localhost:5000")
    print("🖼️  Папка assets доступна по адресу: http://localhost:5000/assets/")
    print("⏹️  Чтобы остановить сервер, нажми Ctrl+C")
    app.run(host='0.0.0.0', port=5000, debug=True)