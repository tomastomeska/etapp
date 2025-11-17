#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Jednoduchý test server pro ověření funkčnosti Flask aplikace
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <h1>🚀 Test Server Running!</h1>
    <p>European Transport CZ - Test</p>
    <p><a href="http://localhost:5000">Přejít na hlavní aplikaci</a></p>
    """

@app.route('/test')
def test():
    return {"status": "OK", "message": "Test endpoint funguje!"}

if __name__ == '__main__':
    print("🧪 Spouštím test server na http://localhost:5001")
    app.run(debug=True, host='127.0.0.1', port=5001)