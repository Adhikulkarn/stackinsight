import re

def parse_js_code(content):
    functions = re.findall(r'function\s+(\w+)', content)
    arrow_funcs = re.findall(r'const\s+(\w+)\s*=\s*\(', content)
    imports = re.findall(r'import\s+(?:.*from\s+)?[\'"](.+?)[\'"]', content)
    return {
        "functions": list(set(functions + arrow_funcs)),
        "imports": imports
    }
