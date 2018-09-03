import sys
import re
import ast
import binascii
import src.json_formatter as json_formatter
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
        self.asn_mgmt = None
    
    def compile(self, data):
        ckw = {'autotags': True, 'extimpl': True, 'verifwarn': True}
        _stdout_, _stderr_ = sys.stdout, sys.stderr
        with open(self.log_file, "w") as fd:
            sys.stdout, sys.stderr = fd, fd
            compile_text(data, **ckw)
            generate_modules(PycrateGenerator, self.py_file)
            sys.stdout, sys.stderr = _stdout_, _stderr_
        self.msgs_in_modules = _get_supported_messages_in_modules(self.py_file)
        self.asn_mgmt = AsnCodeMgmt(data)
    
    def encode(self, protocol, format, msg_name, msg_content):
        pdu_str = self._get_pdu_str(msg_name)
        if pdu_str is None: return False, "Unknow message!"
        modules = [_change_variable_to_python_style(module) for module in self.msgs_in_modules]
        target = __import__(self._get_target_module(), globals(), locals(), modules)
        pdu = eval("target." + pdu_str)
        try:
            if format == "asn1": pdu.from_asn1(msg_content)
            else:
                msg = ast.literal_eval(msg_content)
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
        return True, binascii.hexlify(payload).decode("utf-8")
    
    def decode(self, protocol, format, msg_name, payload):
        ## the length of payload must be even, and payload should be hex stream
        pdu_str = self._get_pdu_str(msg_name)
        if pdu_str is None: return False, "Unknow message!"
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
        res = pdu.to_asn1() if format == "asn1" else json_formatter.format_json(str(pdu()))
        return True, res
    
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
        ##TODO: need to do more reliable check
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


def _reformat_asn_line(line):
    words = re.findall(r"\([^\(\)]*\(.*?\)[^\(\)]*\)|\(.*?\)|[\w\-]+|[\:\=]+|\{|\}|,", line)
    new_lines = []
    indent = 0
    new_line = ' ' * indent
    for i in range(len(words)):
        if words[i] == "{":
            indent += 4
            new_line += words[i]
            new_lines.append(new_line)
            new_line = ' ' * indent
        elif words[i] == "}":
            if words[i-1] == "{":
                new_line += words[i]
            else:
                new_lines.append(new_line)
                indent -= 4
                new_line = (' ' * indent) + words[i] + " "
        else:
            if i > 0 and words[i-1] == ",":
                new_lines.append(new_line)
                new_line = (' ' * indent) + words[i] + " "
            else:
                new_line += (words[i] + " ")
    if new_line.strip() != '': new_lines.append(new_line)
    return "\n".join(new_lines)


class AsnCodeMgmt(object):
    def __init__(self, data):
        self.lines = data.split('\n')
        self.msgs_with_definition = {}
        self._remove_comments_and_blank_lines()
        self._replace_all_macros()
        self._put_one_type_one_line()    ## self.lines will be useless from this step, use self.msgs_with_definition instead

    def _remove_comments_and_blank_lines(self):
        regs = [r"(.*)--.*--(.*)", r"(.*)?--.*", ".*"]
        lines = []
        for line in self.lines:
            if line.strip() == "": continue
            for i in range(len(regs)):
                matched = re.match(regs[i], line)
                if matched:
                    if i == 0:
                        lines.append(matched.group(1) + matched.group(2))
                    elif i == 1:
                        lines.append(matched.group(1))
                    else:
                        lines.append(line)
                    break
        self.lines = lines

    def _replace_all_macros(self):
        macro_reg = re.compile(r"([\w\-]+)\s+\w+\s+::=\s*([\w\-]+)")
        macros = []
        lines = self.lines
        for i in range(len(lines)):
            matched = macro_reg.match(lines[i])
            if matched:
                macros.append((matched.group(1), matched.group(2)))
                lines[i] = ''
        for i in range(len(lines)):
            if lines[i] == '': continue
            for macro in macros:
                replace_pattern = r"([^\w\-\d]+)({})([^\w\-\d]+)".format(macro[0])
                lines[i] = re.sub(replace_pattern, r"\1 %s \3" % macro[1], lines[i])
        self.lines = []
        for line in lines:
            if line != '': self.lines.append(' '.join(line.split()))

    def _put_one_type_one_line(self):
        new_lines = []
        unmatched_bracket_amount = 0
        new_line = ''
        for line in self.lines:
            new_line += line.strip()
            unmatched_bracket_amount += (line.count('{') - line.count('}'))
            if unmatched_bracket_amount == 0:
                new_lines.append(new_line)
                new_line = ''
        self.lines = []
        for line in new_lines:
            name = line.split("::=")[0].strip()
            self.msgs_with_definition[name] = line

    def get_message_definition(self, msg_name):
        from queue import Queue
        msgs = Queue()
        msgs.put(msg_name)
        res = ''
        while not msgs.empty():
            msg = msgs.get()
            definition = self.msgs_with_definition[msg]
            res = res + "\n" + _reformat_asn_line(definition)
            types = self._get_member_types(msg)
            for item in types:
                msgs.put(item)
        return res
    
    def _get_member_types(self, msg_name):
        definition = self.msgs_with_definition[msg_name]
        asn_key_words = ["SEQUENCE", "OF", "CHOICE", "BOOLEAN", "BIT", "STRING", "OCTET", "CONTAINING", "NULL", "SIZE",
                         "SET", "INTEGER", "DEFINITIONS", "AUTOMATIC", "TAGS", "BEGIN", "END", "IMPORTS", "FROM"]
        types = []
        for typ in re.findall(r"[\w\-]+", definition)[1:]:
            if (typ not in asn_key_words) and (typ in self.msgs_with_definition):
                types.append(typ)
        return types



