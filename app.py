# app.py
"""
Email Validation API
Проверяет: 
1. Синтаксис email 
2. Временные домены (mailinator.com и др.)
3. Наличие MX-записей (может ли домен принимать почту)

Как использовать:
GET /validate?email=test@gmail.com
"""

from flask import Flask, request, jsonify
import dns.resolver
import re
import logging

# Настройка логирования (чтобы видеть запросы в Render)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Полный список временных доменов (актуальный на 2024)
TEMP_DOMAINS = [
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "yopmail.com", "disposable.com", "throwawaymail.com", "maildrop.cc",
    "getnada.com", "temp-mail.org", "mailtemp.net", "mailcatch.com"
]

# Кэш для MX-записей (ускоряет повторные проверки)
MX_CACHE = {}

def is_valid_email(email):
    """Проверяет email на валидность"""
    # 1. Проверка синтаксиса
    if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
        return False, "Invalid syntax"
    
    # 2. Проверка временных доменов
    domain = email.split('@')[1].lower()
    if domain in TEMP_DOMAINS:
        return False, f"Disposable domain ({domain})"
    
    # 3. Проверка MX-записей (с кэшированием)
    if domain in MX_CACHE:
        return MX_CACHE[domain]
    
    try:
        dns.resolver.resolve(domain, 'MX')
        MX_CACHE[domain] = (True, "Valid MX records")
        return True, "Valid email"
    except dns.resolver.NXDOMAIN:
        MX_CACHE[domain] = (False, "Domain does not exist")
        return False, "Domain does not exist"
    except dns.resolver.NoAnswer:
        MX_CACHE[domain] = (False, "No MX records")
        return False, "No MX records"
    except Exception as e:
        logger.error(f"DNS error for {domain}: {str(e)}")
        MX_CACHE[domain] = (False, "DNS lookup failed")
        return False, "DNS lookup failed"

@app.route('/validate', methods=['GET'])
def validate():
    """Основной эндпоинт API"""
    email = request.args.get('email')
    
    if not email:
        return jsonify({
            "error": "Email parameter is required",
            "example": "/validate?email=test@gmail.com"
        }), 400
    
    logger.info(f"Validation request: {email}")
    
    is_valid, reason = is_valid_email(email)
    
    return jsonify({
        "email": email,
        "is_valid": is_valid,
        "reason": reason
    })

@app.route('/health', methods=['GET'])
def health():
    """Эндпоинт для UptimeRobot"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Render требует запуск на 0.0.0.0 и порту из переменной среды
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
