from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
import os
import re
import tempfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = "enquetenum_secret_2025"

DB_PATH = os.path.join(tempfile.gettempdir(), "database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enquete(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        age INTEGER NOT NULL,
        sexe TEXT NOT NULL,
        smartphone TEXT NOT NULL,
        temps_tel REAL,
        internet TEXT,
        whatsapp TEXT NOT NULL,
        facebook TEXT NOT NULL,
        tiktok TEXT NOT NULL,
        niveau TEXT NOT NULL,
        date_soumission TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

def validate_form(form):
    errors = []
    nom = form.get('nom', '').strip()
    if not nom or len(nom) < 2:
        errors.append("Le nom doit contenir au moins 2 caractères.")
    if not re.match(r"^[A-Za-zÀ-ÿ\s\-']+$", nom):
        errors.append("Le nom ne doit contenir que des lettres.")
    try:
        age = int(form.get('age', 0))
        if age < 5 or age > 100:
            errors.append("L'âge doit être entre 5 et 100 ans.")
    except ValueError:
        errors.append("L'âge doit être un nombre valide.")
    if form.get('sexe') not in ['Masculin', 'Féminin', 'Autre']:
        errors.append("Veuillez sélectionner un sexe valide.")
    if form.get('smartphone') not in ['Oui', 'Non']:
        errors.append("Veuillez indiquer si vous avez un smartphone.")
    if form.get('smartphone') == 'Oui':
        try:
            temps = float(form.get('temps_tel', 0))
            if temps < 0 or temps > 24:
                errors.append("Le temps d'utilisation doit être entre 0 et 24 heures.")
        except ValueError:
            errors.append("Le temps d'utilisation doit être un nombre valide.")
    for app_name in ['whatsapp', 'facebook', 'tiktok']:
        if form.get(app_name) not in ['Oui', 'Non']:
            errors.append(f"Veuillez indiquer votre utilisation de {app_name.capitalize()}.")
    if form.get('niveau') not in ['Primaire', 'Secondaire', 'Universitaire', 'Aucun']:
        errors.append("Veuillez sélectionner un niveau d'éducation valide.")
    return errors

@app.route('/')
def index():
    return redirect(url_for('formulaire'))

@app.route('/formulaire')
def formulaire():
    return render_template('formulaire.html')

@app.route('/submit', methods=['POST'])
def submit():
    errors = validate_form(request.form)
    if errors:
        for e in errors:
            flash(e, 'error')
        return redirect(url_for('formulaire'))

    smartphone = request.form.get('smartphone')
    temps_tel = float(request.form.get('temps_tel', 0)) if smartphone == 'Oui' else 0.0
    internet = request.form.get('internet', 'Non') if smartphone == 'Oui' else 'Non'

    data = (
        request.form['nom'].strip(),
        int(request.form['age']),
        request.form['sexe'],
        smartphone,
        temps_tel,
        internet,
        request.form['whatsapp'],
        request.form['facebook'],
        request.form['tiktok'],
        request.form['niveau'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    conn = get_db()
    conn.execute("""
        INSERT INTO enquete (nom, age, sexe, smartphone, temps_tel, internet, whatsapp, facebook, tiktok, niveau, date_soumission)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

    flash("Votre réponse a été enregistrée avec succès !", 'success')
    return redirect(url_for('liste'))

@app.route('/liste')
def liste():
    search = request.args.get('search', '').strip()
    filtre_sexe = request.args.get('sexe', '')
    filtre_niveau = request.args.get('niveau', '')
    sort = request.args.get('sort', 'id')
    order = request.args.get('order', 'desc')

    allowed_sorts = ['id', 'nom', 'age', 'niveau', 'date_soumission']
    if sort not in allowed_sorts:
        sort = 'id'
    if order not in ['asc', 'desc']:
        order = 'desc'

    conn = get_db()
    query = "SELECT * FROM enquete WHERE 1=1"
    params = []

    if search:
        query += " AND nom LIKE ?"
        params.append(f"%{search}%")
    if filtre_sexe:
        query += " AND sexe = ?"
        params.append(filtre_sexe)
    if filtre_niveau:
        query += " AND niveau = ?"
        params.append(filtre_niveau)

    query += f" ORDER BY {sort} {order.upper()}"
    data = conn.execute(query, params).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM enquete").fetchone()[0]
    conn.close()

    return render_template('liste.html', data=data, total=total,
                           search=search, filtre_sexe=filtre_sexe,
                           filtre_niveau=filtre_niveau, sort=sort, order=order)

@app.route('/dashboard')
def dashboard():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM enquete").fetchone()[0]
    smartphone_oui = conn.execute("SELECT COUNT(*) FROM enquete WHERE smartphone='Oui'").fetchone()[0]
    avg_age = conn.execute("SELECT AVG(age) FROM enquete").fetchone()[0]
    avg_temps = conn.execute("SELECT AVG(temps_tel) FROM enquete WHERE smartphone='Oui'").fetchone()[0]

    sexe_data = conn.execute("SELECT sexe, COUNT(*) as cnt FROM enquete GROUP BY sexe").fetchall()
    niveau_data = conn.execute("SELECT niveau, COUNT(*) as cnt FROM enquete GROUP BY niveau").fetchall()
    apps_data = {
        'WhatsApp': conn.execute("SELECT COUNT(*) FROM enquete WHERE whatsapp='Oui'").fetchone()[0],
        'Facebook': conn.execute("SELECT COUNT(*) FROM enquete WHERE facebook='Oui'").fetchone()[0],
        'TikTok': conn.execute("SELECT COUNT(*) FROM enquete WHERE tiktok='Oui'").fetchone()[0],
    }
    age_tranches = conn.execute("""
        SELECT
            CASE
                WHEN age < 15 THEN 'Moins de 15'
                WHEN age BETWEEN 15 AND 24 THEN '15-24'
                WHEN age BETWEEN 25 AND 34 THEN '25-34'
                WHEN age BETWEEN 35 AND 49 THEN '35-49'
                ELSE '50 et +'
            END as tranche,
            COUNT(*) as cnt
        FROM enquete GROUP BY tranche ORDER BY tranche
    """).fetchall()
    conn.close()

    return render_template('dashboard.html',
        total=total,
        smartphone_oui=smartphone_oui,
        avg_age=round(avg_age, 1) if avg_age else 0,
        avg_temps=round(avg_temps, 1) if avg_temps else 0,
        sexe_data=[dict(r) for r in sexe_data],
        niveau_data=[dict(r) for r in niveau_data],
        apps_data=apps_data,
        age_tranches=[dict(r) for r in age_tranches]
    )

@app.route('/delete/<int:record_id>', methods=['POST'])
def delete(record_id):
    conn = get_db()
    conn.execute("DELETE FROM enquete WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    flash("Enregistrement supprimé.", 'info')
    return redirect(url_for('liste'))

@app.route('/api/stats')
def api_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM enquete").fetchone()[0]
    conn.close()
    return jsonify({"total_reponses": total, "status": "ok"})

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
