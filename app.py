from flask import Flask, render_template, request, redirect, url_for, session
# from flask import Markup
from openai import OpenAI

from ai_connector import get_req_parm_matrix_from_ai

client = OpenAI()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Sekretny klucz do sesji
app.jinja_env.globals.update(enumerate=enumerate, zip=zip)


@app.route('/')
def index():
    # Strona główna
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
            session['technical_relations_matrix'] = []
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
            param_type = request.form.get('param_type', '').strip()
            if param_name and param_type:
                tech_params = session['technical_params']
                tech_params.append({'name': param_name, 'type': param_type})
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
            # Fill the matrix with 1
            # relations_matrix = get_req_parm_matrix_from_ai(product_name, product_desc, cr, tp)
            # for i in range(len(cr)):
            #     for j in range(len(tp)):
            #         relations_matrix[i][j] = '1'
            relations_matrix_from_ai = get_req_parm_matrix_from_ai(product_name, product_desc, cr, tp)
            session['relations_matrix'] = relations_matrix_from_ai
        elif action == 'save':
            # Zapisz dane z formularza
            all_filled = True
            for i in range(len(cr)):
                for j in range(len(tp)):
                    field_name = f"relation_{i}_{j}"
                    value = request.form.get(field_name)
                    if value is None or value not in ['1', '3', '9']:
                        all_filled = False
                    else:
                        relations_matrix[i][j] = value

            if all_filled:
                session['relations_matrix'] = relations_matrix
                # Przejdź dalej do form5
                # Przygotuj macierz relacji parametrów technicznych do siebie
                count_tp = len(tp)
                technical_relations_matrix = [[None for _ in range(count_tp)] for _ in range(count_tp)]
                session['technical_relations_matrix'] = technical_relations_matrix
                return redirect(url_for('form5'))
            else:
                # Nie wszystkie pola uzupełnione
                pass

    return render_template('form4.html', client_requirements=cr, technical_params=tp, relations_matrix=relations_matrix)


@app.route('/form5', methods=['GET', 'POST'])
def form5():
    # Macierz relacji parametrów technicznych między sobą
    if 'technical_params' not in session:
        return redirect(url_for('index'))

    tp = session['technical_params']
    technical_relations_matrix = session.get('technical_relations_matrix', [])

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'fill_ai':
            # Uzupełnij wszystkie pola wartością 'brak'
            for i in range(len(tp)):
                for j in range(len(tp)):
                    if i == j:
                        technical_relations_matrix[i][j] = 'brak'  # na przekątnej może być zawsze brak?
                    else:
                        technical_relations_matrix[i][j] = 'brak'
            session['technical_relations_matrix'] = technical_relations_matrix
        elif action == 'save':
            # Zapisz dane z formularza
            all_filled = True
            for i in range(len(tp)):
                for j in range(len(tp)):
                    field_name = f"tech_relation_{i}_{j}"
                    # Nieco logiczne - pole relacji dla (i,i) może być brak z definicji
                    if i == j:
                        value = 'brak'
                    else:
                        value = request.form.get(field_name)
                    if value not in ['brak', 'pozytywna', 'negatywna']:
                        all_filled = False
                    else:
                        technical_relations_matrix[i][j] = value
            if all_filled:
                session['technical_relations_matrix'] = technical_relations_matrix
                return redirect(url_for('result'))
            else:
                # Nie wszystkie pola uzupełnione
                pass

    return render_template('form5.html', technical_params=tp, technical_relations_matrix=technical_relations_matrix)


@app.route('/result', methods=['GET'])
def result():
    # Wyświetlenie drzewa QFD i wyliczeń
    product_name = session.get('product_name', '')
    product_desc = session.get('product_desc', '')
    cr = session.get('client_requirements', [])
    tp = session.get('technical_params', [])
    relations_matrix = session.get('relations_matrix', [])
    technical_relations_matrix = session.get('technical_relations_matrix', [])

    # Oblicz znaczenie techniczne parametrów:
    # Dla każdego parametru technicznego sumujemy: (ocena ważności wymagania * relacja)
    # relacja jest w {1,3,9}, waga wymagania w {1..10}
    tech_scores = [0] * len(tp)

    for i, req in enumerate(cr):
        for j, param in enumerate(tp):
            val = relations_matrix[i][j]
            if val is not None:
                val_int = int(val)
                importance = req['importance']
                tech_scores[j] += val_int * importance

    # Propozycja rozwoju produktu - przykładowo:
    # Wybierz parametry z najwyższą sumą punktów technicznych do wzmocnienia/usprawnienia
    sorted_params = sorted(zip(tp, tech_scores), key=lambda x: x[1], reverse=True)
    # top_3 do rozwoju
    top_3 = sorted_params[:3] if len(sorted_params) >= 3 else sorted_params

    return render_template('result.html',
                           product_name=product_name,
                           product_desc=product_desc,
                           client_requirements=cr,
                           technical_params=tp,
                           relations_matrix=relations_matrix,
                           technical_relations_matrix=technical_relations_matrix,
                           tech_scores=tech_scores,
                           top_3=top_3)


if __name__ == '__main__':
    app.run(debug=True)
