from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Función para conectar con la base de datos
def conectar_db():
    return sqlite3.connect('svag.db')

# Página de inicio
@app.route('/')
def index():
    return render_template('index.html')

# Ruta de inicio de sesión para maestros
@app.route('/login_maestro', methods=['GET', 'POST'])
def login_maestro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM maestros WHERE usuario = ? AND password = ?", (usuario, password))
        maestro = cursor.fetchone()
        conn.close()
        if maestro:
            session['maestro_id'] = maestro[0]
            return redirect(url_for('dashboard_maestro'))
        else:
            return 'Credenciales inválidas'
    return render_template('login_maestro.html')

# Panel del maestro
@app.route('/dashboard_maestro')
def dashboard_maestro():
    if 'maestro_id' not in session:
        return redirect(url_for('login_maestro'))
    return render_template('dashboard_maestro.html')

# Ruta para mostrar asistencias
@app.route('/asistencias')
def mostrar_asistencias():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT alumnos.matricula, asistencias.fecha, asistencias.hora, asistencias.estado
        FROM asistencias
        JOIN alumnos ON asistencias.alumno_id = alumnos.id
        ORDER BY asistencias.fecha DESC
    ''')
    registros = cursor.fetchall()
    conn.close()
    return render_template('asistencias.html', registros=registros)

# Ruta para ver justificantes
@app.route('/justificantes')
def ver_justificantes():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT justificantes.id, alumnos.matricula, justificantes.fecha, justificantes.motivo, justificantes.estado
        FROM justificantes
        JOIN alumnos ON justificantes.alumno_id = alumnos.id
        ORDER BY justificantes.fecha DESC
    ''')
    justificantes = cursor.fetchall()
    conn.close()
    return render_template('justificantes.html', justificantes=justificantes)

# Ruta para aprobar/rechazar justificantes
@app.route('/actualizar_justificante/<int:id>/<estado>')
def actualizar_justificante(id, estado):
    if estado not in ['aprobado', 'rechazado']:
        return 'Estado inválido'
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE justificantes SET estado = ? WHERE id = ?", (estado, id))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_justificantes'))

if __name__ == '__main__':
    app.run(debug=True)