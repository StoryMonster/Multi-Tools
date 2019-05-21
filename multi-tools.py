from flask import Flask, render_template, request
from src.json_formatter import format_json
from src.asn1_codec import Asn1Codec
from src.users import Users
from src.file_selector import FileSelector
import json
import os

app = Flask(__name__)
users = Users(os.path.join(os.getcwd(), "users"))


def get_user(ip_addr):
    user = users.get_user_by_ip(request.remote_addr)
    return users.add_user(request.remote_addr) if user is None else user


def get_asn1codec(user):
    if user.asn1codec is None:
        user.create_asn1codec_data_dir()
        user.asn1codec = Asn1Codec(user.asn1codec_files['py_file'])
    return user.asn1codec


def get_file_selector(user):
    if user.file_selector is None:
        user.file_selector = FileSelector()
    return user.file_selector


@app.route('/')
def index():
    user = get_user(request.remote_addr)
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
    user = get_user(request.remote_addr)
    asn1codec = get_asn1codec(user)
    return render_template('asn1_codec.html')


@app.route('/asn1_codec', methods=['POST'])
def asn1_codec():
    user = get_user(request.remote_addr)
    asn1codec = get_asn1codec(user)
    req = request.get_json()
    if req['type'] == 'compile':
        status, log, msgs = asn1codec.compile(req['content'])
        return json.dumps({'status': status, 'output': msgs, 'log': log})
    elif req['type'] == 'encode':
        status, output = asn1codec.encode(req['protocol'], req['format'], req["msg_name"], req['content'])
        return json.dumps({'status': status, 'output': output, 'log': ""})
    elif req['type'] == 'decode':
        status, output = asn1codec.decode(req['protocol'], req['format'], req["msg_name"], req['content'])
        return json.dumps({'status': status, 'output': output, 'log': ""})
    elif req['type'] == 'get_msg_definition':
        definition = asn1codec.asn_mgmt.get_message_definition(req["msg_name"])
        return json.dumps({"status": True, "output": definition, 'log': ""})
    else:
        pass


@app.route('/file_selector')
def file_selector_page():
    return render_template('file_selector.html')


@app.route('/file_selector', methods=['POST'])
def handle_file_selector_web_requests():
    user = get_user(request.remote_addr)
    file_selector = get_file_selector(user)
    file_selector.handle_post_request(request.get_json())
    return json.dumps(file_selector.build_response())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
