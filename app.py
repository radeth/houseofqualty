from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Global variables to store form data
product_info = {}
customer_requirements = []
technical_parameters = []
requirement_parameter_matrix = []
parameter_dependency_matrix = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form1', methods=['GET', 'POST'])
def form1():
    if request.method == 'POST':
        product_info['name'] = request.form['product_name']
        product_info['description'] = request.form['product_description']
        return redirect(url_for('form2'))
    return render_template('form1.html')


@app.route('/form2', methods=['GET', 'POST'])
def form2():
    if request.method == 'POST':
        requirement_name = request.form['requirement_name']
        requirement_importance = request.form['requirement_importance']
        customer_requirements.append({'name': requirement_name, 'importance': requirement_importance})
        if 'add_more' in request.form:
            return redirect(url_for('form2'))
        return redirect(url_for('form3'))
    return render_template('form2.html', customer_requirements=customer_requirements)


@app.route('/form3', methods=['GET', 'POST'])
def form3():
    if request.method == 'POST':
        parameter_name = request.form['parameter_name']
        parameter_type = request.form['parameter_type']
        technical_parameters.append({'name': parameter_name, 'type': parameter_type})
        if 'add_more' in request.form:
            return redirect(url_for('form3'))
        return redirect(url_for('form4'))
    return render_template('form3.html', technical_parameters=technical_parameters)


@app.route('/form4', methods=['GET', 'POST'])
def form4():
    if request.method == 'POST':
        for req in customer_requirements:
            for param in technical_parameters:
                dependency = request.form[f'dependency_{req["name"]}_{param["name"]}']
                requirement_parameter_matrix.append(
                    {'requirement': req['name'], 'parameter': param['name'], 'dependency': dependency})
        return redirect(url_for('form5'))
    return render_template('form4.html', customer_requirements=customer_requirements,
                           technical_parameters=technical_parameters)


@app.route('/form5', methods=['GET', 'POST'])
def form5():
    if request.method == 'POST':
        for param1 in technical_parameters:
            for param2 in technical_parameters:
                if param1 != param2:
                    dependency = request.form[f'dependency_{param1["name"]}_{param2["name"]}']
                    parameter_dependency_matrix.append(
                        {'parameter1': param1['name'], 'parameter2': param2['name'], 'dependency': dependency})
        return redirect(url_for('result'))
    return render_template('form5.html', technical_parameters=technical_parameters)


@app.route('/result')
def result():
    # Calculate technical importance and generate QFD tree
    technical_importance = {}
    for param in technical_parameters:
        importance = sum(
            int(dep['dependency']) for dep in requirement_parameter_matrix if dep['parameter'] == param['name'])
        technical_importance[param['name']] = importance

    return render_template('result.html', product_info=product_info, customer_requirements=customer_requirements,
                           technical_parameters=technical_parameters,
                           requirement_parameter_matrix=requirement_parameter_matrix,
                           parameter_dependency_matrix=parameter_dependency_matrix,
                           technical_importance=technical_importance)


if __name__ == '__main__':
    app.run(debug=True)
