from flask import Flask, render_template, request
from src.json_formatter import format_json
from src.asn1_codec import Asn1Codec
from src.users import Users
import json
import os

app = Flask(__name__)
users = Users(os.path.join(os.getcwd(), "users"))


@app.route('/')
def index():
    users.add_user(request.remote_addr)
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
    user = users.get_user_by_ip(request.remote_addr)
    if user is None: return 'You are not allowed to visit this page!'
    if user.asn1codec is None:
        user.create_asn1codec_data_dir()
        user.asn1codec = Asn1Codec(user.asn1codec_files['py_file'], user.asn1codec_files['log_file'])
    return render_template('asn1_codec.html')


@app.route('/asn1_codec', methods=['POST'])
def asn1_codec():
    user = users.get_user_by_ip(request.remote_addr)
    if user is None: return 'You are not allowed to visit this page!'
    if user.asn1codec is None:
        user.create_asn1codec_data_dir()
        user.asn1codec = Asn1Codec(user.asn1codec_files['py_file'], user.asn1codec_files['log_file'])
    req = request.get_json()
    if req['type'] == 'compile':
        user.asn1codec.compile(req['content'])
        status, log, msgs = user.asn1codec.is_compile_success(), user.asn1codec.get_compile_log(), user.asn1codec.get_supported_msgs()
        return json.dumps({'status': status, 'msgs': msgs, 'log': log})
    elif req['type'] == 'encode':
        status, output = user.asn1codec.encode(req['protocol'], req["msg_name"], req['content'])
        return json.dumps({'status': status, 'output': output})
    elif req['type'] == 'decode':
        status, output = user.asn1codec.decode(req['protocol'], req["msg_name"], req['content'])
        return json.dumps({'status': status, 'output': output})
    elif req['type'] == 'get_msg_definition':
        definition = user.asn1codec.asn_mgmt.get_message_definition(req["msg_name"])
        return json.dumps({"status": True, "defintion": definition})
    else:
        pass


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
