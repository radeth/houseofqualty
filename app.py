import json
import os

from flask import Flask, render_template, request, redirect, url_for, session
from openai import OpenAI

from ai_connector import get_req_parm_matrix_from_ai

client = OpenAI()
app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET')
app.jinja_env.globals.update(enumerate=enumerate, zip=zip)


@app.route('/back_to_form1', methods=['POST'])
def back_to_form1():
    return redirect(url_for('form1'))


@app.route('/back_to_form2', methods=['POST'])
def back_to_form2():
    return redirect(url_for('form2'))


@app.route('/back_to_form3', methods=['POST'])
def back_to_form3():
    return redirect(url_for('form3'))


@app.route('/back_to_form4', methods=['POST'])
def back_to_form4():
    return redirect(url_for('form4'))


@app.route('/', methods=['GET', 'POST'])
def index():
    # Strona główna
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and file.filename.endswith('.json'):
            try:
                content = json.load(file)
                session['product_name'] = content["product_name"]
                session['product_desc'] = content["product_desc"]
                cr = content["client_requirements"]
                session['client_requirements'] = cr
                tp = content["technical_params"]
                session['technical_params'] = tp
                session['relations_matrix'] = [[0 for j in range(len(cr))] for i in range(len(tp))]
                return redirect(url_for('form4'))
            except json.JSONDecodeError:
                return "Niepoprawny format pliku JSON", 400
    return render_template('index.html')


@app.route('/form1', methods=['GET', 'POST'])
def form1():
    # Formularz: Nazwa produktu i Opis produktu
    if request.method == 'POST':
        product_name = request.form.get('product_name', '').strip()
        product_desc = request.form.get('product_desc', '').strip()
        if product_name and product_desc:
            session['product_name'] = product_name
            session['product_desc'] = product_desc
            # Inicjalizacja struktur danych w sesji
            session['client_requirements'] = []
            session['technical_params'] = []
            session['relations_matrix'] = []
            return redirect(url_for('form2'))
    return render_template('form1.html')


@app.route('/form2', methods=['GET', 'POST'])
def form2():
    # Formularz dodawania wymagań klienta
    # Wymagania: nazwa + ocena ważności (1-10)
    if 'client_requirements' not in session:
        session['client_requirements'] = []

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            req_name = request.form.get('req_name', '').strip()
            req_importance = request.form.get('req_importance', '').strip()
            if req_name and req_importance:
                client_req = session['client_requirements']
                client_req.append({'name': req_name, 'importance': int(req_importance)})
                session['client_requirements'] = client_req
        elif action == 'delete':
            index_to_delete = request.form.get('delete_index')
            if index_to_delete is not None:
                index_to_delete = int(index_to_delete)
                client_req = session['client_requirements']
                if 0 <= index_to_delete < len(client_req):
                    del client_req[index_to_delete]
                    session['client_requirements'] = client_req
        elif action == 'next':
            # Przejdź do kolejnego formularza, jeśli jest przynajmniej 1 wymaganie
            if len(session['client_requirements']) > 0:
                return redirect(url_for('form3'))

    return render_template('form2.html', client_requirements=session['client_requirements'])


@app.route('/form3', methods=['GET', 'POST'])
def form3():
    # Formularz dodawania parametrów technicznych
    # param: nazwa, typ (Maksymalna, Minimalna, Nominanta)
    if 'technical_params' not in session:
        session['technical_params'] = []

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            param_name = request.form.get('param_name', '').strip()
            if param_name:
                tech_params = session['technical_params']
                tech_params.append({'name': param_name})
                session['technical_params'] = tech_params
        elif action == 'delete':
            index_to_delete = request.form.get('delete_index')
            if index_to_delete is not None:
                index_to_delete = int(index_to_delete)
                tech_params = session['technical_params']
                if 0 <= index_to_delete < len(tech_params):
                    del tech_params[index_to_delete]
                    session['technical_params'] = tech_params
        elif action == 'next':
            if len(session['technical_params']) > 0:
                # Przygotuj macierz relacji dla kolejnego formularza
                # Liczba wymagań x liczba parametrów technicznych
                cr = session['client_requirements']
                tp = session['technical_params']
                relations_matrix = [[None for _ in tp] for _ in cr]
                session['relations_matrix'] = relations_matrix
                return redirect(url_for('form4'))

    return render_template('form3.html', technical_params=session['technical_params'])


@app.route('/form4', methods=['GET', 'POST'])
def form4():
    # Macierz relacji wymagań klienta do parametrów technicznych
    if 'client_requirements' not in session or 'technical_params' not in session:
        return redirect(url_for('index'))

    cr = session['client_requirements']
    tp = session['technical_params']
    relations_matrix = session.get('relations_matrix', [])
    product_name = session.get('product_name', '')
    product_desc = session.get('product_desc', '')

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'fill_ai':
            session['relations_matrix'] = get_req_parm_matrix_from_ai(product_name, product_desc, cr, tp)
        elif action == 'save':
            return redirect(url_for('result'))

    return render_template('form4.html', client_requirements=cr, technical_params=tp, relations_matrix=relations_matrix)


@app.route('/result', methods=['GET'])
def result():
    product_name = session.get('product_name', '')
    product_desc = session.get('product_desc', '')
    cr = session.get('client_requirements', [])
    tp = session.get('technical_params', [])
    relations_matrix = session.get('relations_matrix', [])

    tech_scores = [0] * len(tp)
    for i, req in enumerate(cr):
        for j, param in enumerate(tp):
            val = relations_matrix[i][j]
            if val is not None:
                val_int = int(val)
                importance = req['importance']
                tech_scores[j] += val_int * importance

    sorted_params = sorted(zip(tp, tech_scores), key=lambda x: x[1], reverse=True)
    top_3 = sorted_params[:3] if len(sorted_params) >= 3 else sorted_params

    return render_template('result.html',
                           product_name=product_name,
                           product_desc=product_desc,
                           client_requirements=cr,
                           technical_params=tp,
                           relations_matrix=relations_matrix,
                           tech_scores=tech_scores,
                           top_3=top_3,
                           )


if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
