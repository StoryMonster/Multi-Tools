import sys
import re
import ast
import binascii
from pycrate_asn1c.proc import compile_text, generate_modules, PycrateGenerator


def _change_variable_to_asn_style(variable):
    return re.sub("_", "-", variable)


def _change_variable_to_python_style(variable):
    return re.sub("-", "_", variable)


def _get_supported_messages_in_modules(file):
    supported_msgs_in_modules = {}
    lines = []
    with open(file, "r") as fd:
        for line in fd.readlines():
            if len(line.strip()) == 0: continue
            lines.append(line)
    for module in re.findall(r"[\w\_]+", lines[-1])[1:]:
        supported_msgs_in_modules[_change_variable_to_asn_style(module)] = []
    
    patterns = ((r"class\s([\w\_]+)\:", "class"),
                (r"\s+([\w\_]+)\s*=\s*SEQ\(name=\'\S+\',\smode=MODE_TYPE\)", "sequence"))
    current_module = ''
    for line in lines:
        for pattern in patterns:
            matched = re.match(pattern[0], line)
            if matched:
                if pattern[1] == 'class':
                    current_module = _change_variable_to_asn_style(matched.group(1))
                elif pattern[1] == 'sequence':
                    supported_msgs_in_modules[current_module].append(_change_variable_to_asn_style(matched.group(1)))
                else: pass
                break
    return supported_msgs_in_modules


class Asn1Codec(object):
    def __init__(self, py_file, log_file):
        self.py_file = py_file
        self.log_file = log_file
        self.msgs_in_modules = {}
    
    def compile(self, data):
        ckw = {'autotags': True, 'extimpl': True, 'verifwarn': True}
        _stdout_, _stderr_ = sys.stdout, sys.stderr
        with open(self.log_file, "w") as fd:
            sys.stdout, sys.stderr = fd, fd
            compile_text(data, **ckw)
            generate_modules(PycrateGenerator, self.py_file)
            sys.stdout, sys.stderr = _stdout_, _stderr_
        self.msgs_in_modules = _get_supported_messages_in_modules(self.py_file)
    
    def encode(self, protocol, msg_name, msg_content):
        pdu_str = self._get_pdu_str(msg_name)
        if pdu_str is None:
            return False, "Unknow message!"
        modules = [_change_variable_to_python_style(module) for module in self.msgs_in_modules]
        target = __import__(self._get_target_module(), globals(), locals(), modules)
        pdu = eval("target." + pdu_str)
        msg = ast.literal_eval(msg_content)
        try:
            pdu.set_val(msg)
            payload = None
            if protocol == "per":
                payload = pdu.to_aper()
            elif protocol == "uper":
                payload = pdu.to_uper()
            elif protocol == "ber":
                payload = pdu.to_ber()
            elif protocol == "cer":
                payload = pdu.to_cer()
            elif protocol == "der":
                payload = pdu.to_der()
            else:
                return False, "Unkown protocol"
        except Exception as e:
            return False, str(e)
        return True, str(binascii.hexlify(payload))
    
    def decode(self, protocol, msg_name, payload):
        ## the length of payload must be even, and payload should be hex stream
        pdu_str = self._get_pdu_str(msg_name)
        if pdu_str is None:
            return False, "Unknow message!"
        modules = [_change_variable_to_python_style(module) for module in self.msgs_in_modules]
        target = __import__(self._get_target_module(), globals(), locals(), modules)
        pdu = eval("target." + pdu_str)
        try:
            if protocol == "per":
                pdu.from_aper(binascii.a2b_hex(payload))
            elif protocol == "uper":
                pdu.from_uper(binascii.a2b_hex(payload))
            elif protocol == "ber":
                pdu.from_ber(binascii.a2b_hex(payload))
            elif protocol == "cer":
                pdu.from_cer(binascii.a2b_hex(payload))
            elif protocol == "der":
                pdu.from_der(binascii.a2b_hex(payload))
            else:
                return False, "Unkown protocol"
        except Exception as e:
            return False, str(e)
        return True, str(pdu())
    
    def get_supported_msgs(self):
        supported_msgs = []
        for module in self.msgs_in_modules:
            supported_msgs.extend(self.msgs_in_modules[module])
        supported_msgs.sort()
        return supported_msgs
    
    def get_compile_log(self):
        logs = []
        with open(self.log_file, "r") as fd:
            lines = fd.readlines()
            for line in lines:
                if len(line.strip()) == 0: continue
                logs.append(line)
        return ''.join(logs)
    
    def is_compile_success(self):
        logs = self.get_compile_log()
        lines = logs.split('\n')
        return "[proc] done" == lines[-2].strip()   ## the last line is empty
    
    def _get_pdu_str(self, msg_name):
        for module in self.msgs_in_modules:
            for msg in self.msgs_in_modules[module]:
                if msg == msg_name:
                    return _change_variable_to_python_style(module) + "." + _change_variable_to_python_style(msg)
        return None
    
    def _get_target_module(self):
        if "win32" in sys.platform:
            matched = re.sub(r"\\", r".", self.py_file).split(".")[:-1]
        if "linux" in sys.platform:
            matched = re.sub(r"/", r".", self.py_file).split(".")[:-1]
        module = matched[-1]
        for i in range(len(matched)-2, 0, -1):
            module = matched[i] + "." + module
            if matched[i] == "users":
                return module
        return None
