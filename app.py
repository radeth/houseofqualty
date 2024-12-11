import re

from flask import Flask, render_template, request, redirect, url_for, session
from openai import OpenAI

client = OpenAI()
app = Flask(__name__)


app.secret_key = "supersecretkey"

# # Ustaw swój klucz OpenAI
# openai.api_key = "TUTAJ_WSTAW_SWÓJ_KLUCZ_OPENAI"


@app.route("/")
def index():
    # Strona startowa z linkiem do rozpoczęcia procesu
    return render_template("index.html")


@app.route("/form1", methods=["GET", "POST"])
def form1():
    # Formularz 1: Nazwa i opis produktu
    if request.method == "POST":
        product_name = request.form.get("product_name")
        product_description = request.form.get("product_description")
        if product_name and product_description:
            session["product_name"] = product_name
            session["product_description"] = product_description
            # Inicjujemy struktury danych w sesji
            session["customer_requirements"] = []
            session["technical_params"] = []
            session["requirements_params_matrix"] = {}
            session["tech_params_matrix"] = {}
            return redirect(url_for("form2"))
    return render_template("form1.html")


@app.route("/form2", methods=["GET", "POST"])
def form2():
    # Formularz 2: Dodawanie wymagań klientów
    if request.method == "POST":
        # Dodawanie nowego wymagania
        if "add_requirement" in request.form:
            req_name = request.form.get("req_name")
            req_importance = request.form.get("req_importance")
            if req_name and req_importance:
                requirements = session.get("customer_requirements", [])
                requirements.append({"name": req_name, "importance": req_importance})
                session["customer_requirements"] = requirements

        # Usuwanie wymagania
        if "delete_requirement" in request.form:
            index = int(request.form.get("delete_requirement"))
            requirements = session.get("customer_requirements", [])
            if 0 <= index < len(requirements):
                del requirements[index]
                session["customer_requirements"] = requirements

        # Przejście dalej
        if "next_step" in request.form:
            requirements = session.get("customer_requirements", [])
            if len(requirements) > 0:
                return redirect(url_for("form3"))

    return render_template("form2.html",
                           requirements=session.get("customer_requirements", []))


@app.route("/form3", methods=["GET", "POST"])
def form3():
    # Formularz 3: Dodawanie parametrów technicznych
    if request.method == "POST":
        # Dodawanie parametru
        if "add_param" in request.form:
            param_name = request.form.get("param_name")
            param_type = request.form.get("param_type")  # max, min, nom
            if param_name and param_type:
                params = session.get("technical_params", [])
                params.append({"name": param_name, "type": param_type})
                session["technical_params"] = params

        # Usuwanie parametru
        if "delete_param" in request.form:
            index = int(request.form.get("delete_param"))
            params = session.get("technical_params", [])
            if 0 <= index < len(params):
                del params[index]
                session["technical_params"] = params

        # Przejście dalej
        if "next_step" in request.form:
            params = session.get("technical_params", [])
            if len(params) > 0:
                return redirect(url_for("form4"))

    return render_template("form3.html",
                           technical_params=session.get("technical_params", []))


@app.route("/form4", methods=["GET", "POST"])
def form4():
    # Formularz 4: Macierz wymagań vs parametry techniczne
    requirements = session.get("customer_requirements", [])
    params = session.get("technical_params", [])
    matrix = session.get("requirements_params_matrix", {})

    # Uzupełnianie macierzy jeśli brak
    for r in requirements:
        for p in params:
            key = (r["name"], p["name"])
            if key not in matrix:
                matrix[key] = ""

    if request.method == "POST":
        # Zapis wyborów usera
        for r in requirements:
            for p in params:
                key = (r["name"], p["name"])
                val = request.form.get(f"relation_{r['name']}_{p['name']}")
                if val is not None:
                    matrix[key] = val

        # Uzupełnienie za pomocą AI
        if "fill_ai" in request.form:
            product_name = session.get("product_name", "")
            product_description = session.get("product_description", "")

            prompt = f"""
Mam produkt: {product_name}.
Opis produktu: {product_description}.
Wymagania klientów:
{', '.join([f"{r['name']} (ważność: {r['importance']})" for r in requirements])}.

Parametry techniczne:
{', '.join([f"{p['name']} (typ: {p['type']})" for p in params])}.

Określ zależności pomiędzy każdym wymaganiem a każdym parametrem technicznym (1,3,9).
Podaj w formie: (wymaganie, parametr, wartość).
"""
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            ai_response = response.choices[0].message.content.strip()

            pattern = r"\(([^,]+),\s*([^,]+),\s*([139])\)"
            matches = re.findall(pattern, ai_response)
            for (req_name, param_name, val) in matches:
                req_name = req_name.strip()
                param_name = param_name.strip()
                for r in requirements:
                    for p in params:
                        key = (r["name"], p["name"])
                        if r["name"] == req_name and p["name"] == param_name:
                            matrix[key] = val

        session["requirements_params_matrix"] = matrix

        # Przejście dalej
        if "next_step" in request.form:
            return redirect(url_for("form5"))

    return render_template("form4.html",
                           requirements=requirements,
                           technical_params=params,
                           matrix=matrix)


@app.route("/form5", methods=["GET", "POST"])
def form5():
    # Formularz 5: Macierz parametrów technicznych vs parametrów technicznych
    params = session.get("technical_params", [])
    matrix = session.get("tech_params_matrix", {})

    # Uzupełnij macierz jeśli nie istnieje
    for i in range(len(params)):
        for j in range(len(params)):
            if i != j:
                key = (params[i]["name"], params[j]["name"])
                if key not in matrix:
                    matrix[key] = ""

    if request.method == "POST":
        # Zapis wyborów usera
        for i in range(len(params)):
            for j in range(len(params)):
                if i != j:
                    key = (params[i]["name"], params[j]["name"])
                    val = request.form.get(f"relation_{params[i]['name']}_{params[j]['name']}")
                    if val is not None:
                        matrix[key] = val

        # Uzupełnij za pomocą AI
        if "fill_ai" in request.form:
            product_name = session.get("product_name", "")
            product_description = session.get("product_description", "")

            prompt = f"""
Mam produkt: {product_name}.
Opis produktu: {product_description}.
Parametry techniczne: {', '.join([p['name'] for p in params])}.
Określ zależności pomiędzy parametrami technicznymi w formie (parametr1, parametr2, relacja)
gdzie relacja to '+', '-' lub 'brak'.
"""
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            ai_response = response.choices[0].message.content.strip()

            pattern = r"\(([^,]+),\s*([^,]+),\s*(\+|\-|\brak\b)\)"
            matches = re.findall(pattern, ai_response)
            for (p1, p2, val) in matches:
                p1 = p1.strip()
                p2 = p2.strip()
                for p_first in params:
                    for p_second in params:
                        if p_first["name"] == p1 and p_second["name"] == p2:
                            key = (p1, p2)
                            matrix[key] = val

        session["tech_params_matrix"] = matrix

        # Przejście dalej
        if "next_step" in request.form:
            return redirect(url_for("result"))

    return render_template("form5.html",
                           technical_params=params,
                           matrix=matrix)


@app.route("/result", methods=["GET"])
def result():
    # Wynik: Drzewo QFD, wyliczenia i rekomendacje
    requirements = session.get("customer_requirements", [])
    tech_params = session.get("technical_params", [])
    req_param_matrix = session.get("requirements_params_matrix", {})
    tech_param_matrix = session.get("tech_params_matrix", {})

    importance_map = {r["name"]: float(r["importance"]) for r in requirements}

    technical_importance = {}
    for p in tech_params:
        sum_val = 0
        for r in requirements:
            key = (r["name"], p["name"])
            val = req_param_matrix.get(key, "")
            if val.isdigit():
                sum_val += importance_map[r["name"]] * int(val)
        technical_importance[p["name"]] = sum_val

    product_name = session.get("product_name", "")
    product_description = session.get("product_description", "")

    # Zapytanie do AI o sugestie rozwoju produktu
    prompt = f"""
Mam produkt: {product_name}.
Opis: {product_description}.

Znaczenia techniczne parametrów:
{', '.join([f'{p["name"]}: {technical_importance[p["name"]]}' for p in tech_params])}.

Zależności pomiędzy parametrami technicznymi:
{', '.join([f'({k[0]},{k[1]}): {v}' for k, v in tech_param_matrix.items()])}.

Zaproponuj strategię rozwoju produktu, wybierz parametry kluczowe i uzasadnij wybór.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    ai_suggestion = response.choices[0].message.content.strip()

    return render_template("result.html",
                           product_name=product_name,
                           product_description=product_description,
                           technical_importance=technical_importance,
                           tech_params=tech_params,
                           requirements=requirements,
                           req_param_matrix=req_param_matrix,
                           tech_param_matrix=tech_param_matrix,
                           ai_suggestion=ai_suggestion)


if __name__ == "__main__":
    app.run(debug=True)
