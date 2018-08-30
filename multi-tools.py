from flask import Flask, render_template, request
from src.json_formatter import format_json
from src.asn1_codec import Asn1Codec
from src.users import Users
import json
import os

app = Flask(__name__)
users = Users(os.path.join(os.getcwd(), "users"))
global asn1_codec_user

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


@app.route('/asn1_codec')
def asn1_codec_page():
    return render_template('asn1_codec.html')


@app.route('/asn1_codec', methods=['POST'])
def asn1_codec():
    global asn1_codec_user
    req = request.get_json()
    if req['type'] == 'compile':
        asn1_codec_user = Asn1Codec(None, req['content'])
        asn1_codec_user.compile()
        status, log, msgs = asn1_codec_user.is_compile_success(), asn1_codec_user.get_compile_log(), asn1_codec_user.get_supported_msgs()
        return json.dumps({'status': status, 'msgs': msgs, 'log': log})
    elif req['type'] == 'encode':
        if asn1_codec_user is not None:
            status, output = asn1_codec_user.encode(req['protocol'], req["msg_name"], req['content'])
            return json.dumps({'status': status, 'output': output})
    elif req['type'] == 'decode':
        if asn1_codec_user is not None:
            status, output = asn1_codec_user.decode(req['protocol'], req["msg_name"], req['content'])
            return json.dumps({'status': status, 'output': output})
    else:
        pass


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
