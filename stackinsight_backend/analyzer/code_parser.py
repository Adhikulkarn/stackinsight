import os
from analyzer.parser_py import parse_python_code
from analyzer.parser_js import parse_js_code
from analyzer.parser_html import parse_html_code
from analyzer.parser_css import parse_css_code

def analyze_code_structure(repo_path):
    parsed_data = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith((".py", ".js", ".jsx", ".html", ".css")):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                if file.endswith(".py"):
                    parsed_data[file] = parse_python_code(content)
                elif file.endswith((".js", ".jsx")):
                    parsed_data[file] = parse_js_code(content)
                elif file.endswith(".html"):
                    parsed_data[file] = parse_html_code(content)
                elif file.endswith(".css"):
                    parsed_data[file] = parse_css_code(content)
    return parsed_data
