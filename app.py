from flask import Flask, render_template, request, redirect, url_for
import openai
import os

app = Flask(__name__)

# Ustaw swój klucz OpenAI
openai.api_key = "TWOJ_OPENAI_API_KEY"

# Zmienne globalne przechowujące dane w pamięci
product_info = {"name": "", "description": ""}
client_requirements = []  # lista słowników: {"name": "", "importance": int}
technical_parameters = []  # lista słowników: {"name": "", "category": "Maksymalna/Minimalna/Nominanta"}

# Macierz wymagań vs parametry: wartości 1,3,9
# Będzie to lista list o wymiarach [len(client_requirements)][len(technical_parameters)]
requirements_matrix = []

# Macierz parametry vs parametry: wartości brak, +, -
# Będzie to lista list o wymiarach [len(technical_parameters)][len(technical_parameters)]
parameters_matrix = []

def compute_technical_significance():
    """
    Wylicza znaczenie techniczne poszczególnych parametrów na podstawie
    macierzy wymagań. Znaczenie = suma(ocena ważności wymagania * zależność).
    Zwraca listę wartości znaczeń technicznych w kolejności parametrów.
    """
    global client_requirements, technical_parameters, requirements_matrix
    if not client_requirements or not technical_parameters or not requirements_matrix:
        return []
    significance = [0]*len(technical_parameters)
    for i, req in enumerate(client_requirements):
        imp = int(req["importance"])
        for j, val in enumerate(requirements_matrix[i]):
            # val to '1', '3', lub '9' -> konwersja na int
            significance[j] += imp * int(val)
    return significance

def generate_development_suggestions(significance, parameters_matrix):
    """
    Generuje sugestie rozwojowe wykorzystując OpenAI,
    opierając się na nazwie i opisie produktu oraz obliczonych znaczeniach i korelacjach.
    """
    global product_info, technical_parameters
    # Przygotowanie promptu
    prompt = f"""
Analizujesz produkt: {product_info['name']}.
Opis: {product_info['description']}.

Posiadasz listę parametrów technicznych i ich znaczenie:
{[p['name'] for p in technical_parameters]} z odpowiadającymi znaczeniami: {significance}.

Posiadasz też macierz zależności pomiędzy parametrami technicznymi (brak, +, -):
{parameters_matrix}

Zaproponuj proces rozwoju produktu w oparciu o powyższe dane.
Podaj wskazówki rozwojowe, priorytety i optymalną ścieżkę z uwzględnieniem korelacji parametrów.
Odpowiedź przedstaw w klarownej formie, najlepiej w formie wypunktowanej listy.
"""
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].text.strip()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/form1", methods=["GET", "POST"])
def form1():
    if request.method == "POST":
        product_info["name"] = request.form["name"].strip()
        product_info["description"] = request.form["description"].strip()
        return redirect(url_for("form2"))
    return render_template("form1.html")

@app.route("/form2", methods=["GET", "POST"])
def form2():
    if request.method == "POST":
        # Dodawanie wymagań klientów
        name = request.form.get("name", "").strip()
        importance = request.form.get("importance", "5").strip()
        if name:
            client_requirements.append({"name": name, "importance": importance})
    return render_template("form2.html", requirements=client_requirements)

@app.route("/delete_requirement/<int:index>")
def delete_requirement(index):
    if 0 <= index < len(client_requirements):
        del client_requirements[index]
    return redirect(url_for("form2"))

@app.route("/form3", methods=["GET", "POST"])
def form3():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "")
        if name:
            technical_parameters.append({"name": name, "category": category})
    return render_template("form3.html", parameters=technical_parameters)

@app.route("/delete_parameter/<int:index>")
def delete_parameter(index):
    if 0 <= index < len(technical_parameters):
        del technical_parameters[index]
    return redirect(url_for("form3"))

@app.route("/form4", methods=["GET", "POST"])
def form4():
    global requirements_matrix
    # Inicjalizacja lub reset macierzy, jeśli zmieniono dane
    if len(requirements_matrix) != len(client_requirements):
        requirements_matrix = [[0]*len(technical_parameters) for _ in range(len(client_requirements))]
    if request.method == "POST":
        # Zapis danych z formularza
        for i in range(len(client_requirements)):
            for j in range(len(technical_parameters)):
                key = f"relation_{i}_{j}"
                val = request.form.get(key, "0")
                requirements_matrix[i][j] = val
        return redirect(url_for("form5"))

    if request.args.get("ai_fill") == "1":
        # Uzupełnienie za pomocą AI
        # Przygotowanie promptu do OpenAI
        prompt = f"""
Posiadasz produkt: {product_info['name']}.
Opis produktu: {product_info['description']}

Lista wymagań klientów:
{[r['name'] for r in client_requirements]}

Lista parametrów technicznych:
{[p['name'] for p in technical_parameters]}

Stwórz macierz zależności pomiędzy wymaganiami klientów a parametrami technicznymi.
Użyj wartości 1, 3, lub 9. 
Przedstaw wynik w formacie Pythonowej listy list, np. [[1,3],[9,1]] tak, aby można było zrobić eval().
"""
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        try:
            ai_result = response.choices[0].text.strip()
            # Próba zinterpretowania wyniku jako listy list
            new_matrix = eval(ai_result)
            # Sprawdzenie rozmiarów
            if len(new_matrix) == len(client_requirements) and all(len(row) == len(technical_parameters) for row in new_matrix):
                requirements_matrix = new_matrix
        except:
            pass

    return render_template("form4.html",
                           requirements=client_requirements,
                           parameters=technical_parameters,
                           matrix=requirements_matrix)

@app.route("/form5", methods=["GET", "POST"])
def form5():
    global parameters_matrix
    if len(parameters_matrix) != len(technical_parameters):
        parameters_matrix = [["brak"]*len(technical_parameters) for _ in range(len(technical_parameters))]

    if request.method == "POST":
        for i in range(len(technical_parameters)):
            for j in range(len(technical_parameters)):
                key = f"relation_{i}_{j}"
                val = request.form.get(key, "brak")
                parameters_matrix[i][j] = val
        return redirect(url_for("result"))

    if request.args.get("ai_fill") == "1":
        # Uzupełnienie za pomocą AI
        prompt = f"""
Posiadasz produkt: {product_info['name']}.
Opis produktu: {product_info['description']}

Lista parametrów technicznych:
{[p['name'] for p in technical_parameters]}

Stwórz macierz zależności pomiędzy parametrami technicznymi.
Użyj wartości: "brak", "+", lub "-".
Przedstaw wynik w formacie Pythonowej listy list np. [["brak","+"],["-","brak"]].
"""
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        try:
            ai_result = response.choices[0].text.strip()
            new_matrix = eval(ai_result)
            if len(new_matrix) == len(technical_parameters) and all(len(row) == len(technical_parameters) for row in new_matrix):
                parameters_matrix = new_matrix
        except:
            pass

    return render_template("form5.html",
                           parameters=technical_parameters,
                           matrix=parameters_matrix)

@app.route("/result")
def result():
    significance = compute_technical_significance()
    suggestions = generate_development_suggestions(significance, parameters_matrix)
    return render_template("result.html",
                           product=product_info,
                           requirements=client_requirements,
                           parameters=technical_parameters,
                           requirements_matrix=requirements_matrix,
                           parameters_matrix=parameters_matrix,
                           significance=significance,
                           suggestions=suggestions)

if __name__ == "__main__":
    app.run(debug=True)
