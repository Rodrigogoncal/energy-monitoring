from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'segredo'

DEMO_MODE = True


def conectar():
    return sqlite3.connect('database.db')


def criar_tabela():
    conn = conectar()

    conn.execute('''
        CREATE TABLE IF NOT EXISTS consumo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            consumo REAL
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            senha TEXT
        )
    ''')

    usuario = conn.execute("SELECT * FROM usuarios WHERE username='admin'").fetchone()

    if not usuario:
        conn.execute("INSERT INTO usuarios (username, senha) VALUES ('admin', '123')")

    conn.commit()
    conn.close()


# 👇 AGORA sim chama depois de criar
criar_tabela()


@app.route('/')
def index():
    session['usuario'] = 'demo'  # login automático

    conn = conectar()
    dados = conn.execute('SELECT * FROM consumo').fetchall()
    conn.close()

    alertas = []
    for d in dados:
        if d[2] > 50:
            alertas.append(f"⚠️ Consumo alto: {d[2]} kWh em {d[1]}")

    return render_template('index.html', dados=dados, alertas=alertas)


@app.route('/adicionar', methods=['POST'])
def adicionar():
    if DEMO_MODE:
        return redirect('/')

    consumo = request.form['consumo']
    data = datetime.now().strftime('%Y-%m-%d %H:%M')

    conn = conectar()
    conn.execute('INSERT INTO consumo (data, consumo) VALUES (?, ?)', (data, consumo))
    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/excluir/<int:id>')
def excluir(id):
    if DEMO_MODE:
        return redirect('/')

    conn = conectar()
    conn.execute('DELETE FROM consumo WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return redirect('/')  # ignora login no modo demo


@app.route('/logout')
def logout():
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
