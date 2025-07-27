# app.py
from flask import Flask, request, jsonify
import dns.resolver
import re

app = Flask(__name__)

TEMP_DOMAINS = ["mailinator.com", "tempmail.com", "10minutemail.com"]  # Полный список добавим позже

def is_valid_email(email):
    # Проверка синтаксиса
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False
    
    # Проверка временных доменов
    domain = email.split('@')[1]
    if domain in TEMP_DOMAINS:
        return False
    
    # Проверка MX-записей
    try:
        dns.resolver.resolve(domain, 'MX')
        return True
    except:
        return False

@app.route('/validate', methods=['GET'])
def validate():
    email = request.args.get('email')
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    is_valid = is_valid_email(email)
    return jsonify({
        "email": email,
        "is_valid": is_valid,
        "reason": "Valid email" if is_valid else "Invalid syntax, disposable domain or no MX records"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
