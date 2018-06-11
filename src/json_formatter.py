

def sort_json(src):
    if isinstance(src, dict):
        keys = sorted(src)
        res = {}
        for key in keys:
            res[key] = sort_json(src[key])
        return res
    elif isinstance(src, list):
        res = []
        for item in src:
            res.append(sort_json(item))
        return res
    elif isinstance(src, tuple):
        return tuple(sort_json(list(src)))
    return src

def format_json(src):
    formatted = str(sort_json(src))
    tab_block = ' ' * 4
    indent = ''
    line = indent
    lines = []
    for ch in formatted:
        if ch in ('(', '[', '{'):
            lines.append(line + ch)
            indent += tab_block
            line = indent
        elif ch in (')', ']', '}'):
            lines.append(line)
            indent = indent[0 : len(indent) - len(tab_block)]
            lines.append(indent + ch)
            line = indent
        elif ch == ',':
            if len(line.strip()) == 0:
                lines[-1] += ch
            else:
                lines.append(line + ch)
            line = indent
        elif ch == ' ':
            if len(line.strip()) != 0:
                line += ch
        else:
            line += ch
    res = []
    for line in lines:
        if line.strip() != '':
            res.append(line)
    return '\n'.join(res)
