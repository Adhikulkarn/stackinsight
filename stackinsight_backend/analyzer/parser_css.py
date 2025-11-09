import tinycss2

def parse_css_code(content):
    selectors = []
    try:
        rules = tinycss2.parse_stylesheet(content)
        for rule in rules:
            if hasattr(rule, "prelude"):
                selectors.append("".join([t.value for t in rule.prelude if hasattr(t, 'value')]))
    except Exception as e:
        print(f"CSS parsing error: {e}")
    return {"selectors": selectors[:10]}  # Limit for simplicity
