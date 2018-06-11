from flask import Flask, render_template, request
from src.json_formatter import format_json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('tool_list.html')


@app.route('/json_formatter')
def json_formatter_page():
    return render_template('json_formatter.html')


@app.route('/json_formatter', methods=['POST'])
def json_formatter():
    input = request.form['input']
    try:
        import ast
        output = format_json(ast.literal_eval(r"{}".format(input)))
        return render_template('json_formatter.html', input=input, output=output)
    except:
        return render_template('json_formatter.html', input=input, output="Error: the json format error")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
