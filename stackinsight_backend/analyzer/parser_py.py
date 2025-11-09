import ast

def parse_python_code(content):
    structure = {"functions": [], "classes": [], "imports": []}
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                structure["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                structure["classes"].append(node.name)
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    structure["imports"].append(alias.name)
    except Exception as e:
        print(f"Python parsing error: {e}")
    return structure
