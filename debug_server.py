#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simplified debug version of main app
"""

import os
from flask import Flask, render_template_string

# Jednoduchá Flask aplikace pro debugging
app = Flask(__name__)
app.config['SECRET_KEY'] = 'debug-secret-key-123'

@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>European Transport CZ - Debug</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; background: #f4f4f4; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            h1 { color: #2c5aa0; }
            .status { background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .login-box { background: #e3f2fd; padding: 20px; border-radius: 5px; margin: 20px 0; }
            a { color: #2c5aa0; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 European Transport CZ - Aplikační Server</h1>
            
            <div class="status">
                <strong>✅ Status:</strong> Debug verze běží správně!
            </div>
            
            <div class="login-box">
                <h3>🔐 Přihlašovací údaje:</h3>
                <p><strong>Admin:</strong> admin@europeantransport.cz / admin123</p>
                <p><strong>User:</strong> user@europeantransport.cz / user123</p>
            </div>
            
            <h3>🔗 Dostupné odkazy:</h3>
            <ul>
                <li><a href="/test">Test endpoint</a></li>
                <li><a href="/full">Spustit plnou aplikaci</a></li>
            </ul>
            
            <p><small>Debug server - European Transport CZ s.r.o.</small></p>
        </div>
    </body>
    </html>
    """)

@app.route('/test')
def test():
    return {"status": "OK", "message": "Debug endpoint funguje!", "app": "European Transport CZ"}

@app.route('/full')
def full_app():
    try:
        from app import create_app
        return render_template_string("""
        <div style="font-family: Arial; padding: 50px; background: #f4f4f4;">
            <div style="background: white; padding: 30px; border-radius: 10px;">
                <h2>✅ Plná aplikace je připravena!</h2>
                <p>Import hlavní aplikace proběhl úspěšně.</p>
                <p><a href="/">Zpět na debug stránku</a></p>
                <p><em>Pro spuštění plné aplikace použijte: python run.py</em></p>
            </div>
        </div>
        """)
    except Exception as e:
        return render_template_string(f"""
        <div style="font-family: Arial; padding: 50px; background: #f4f4f4;">
            <div style="background: #f8d7da; padding: 30px; border-radius: 10px; color: #721c24;">
                <h2>❌ Chyba při importu:</h2>
                <p><strong>{str(e)}</strong></p>
                <p><a href="/">Zpět na debug stránku</a></p>
            </div>
        </div>
        """)

if __name__ == '__main__':
    print("="*50)
    print("🔧 European Transport CZ - DEBUG SERVER")
    print("="*50)
    print("📍 URL: http://127.0.0.1:5002")
    print("🎯 Účel: Debugging hlavní aplikace")
    print("="*50)
    
    app.run(debug=True, host='127.0.0.1', port=5002)