import os, json

def detect_frameworks(repo_path):
    detected = []

    # --- FRONTEND FRAMEWORKS ---
    package_json_path = os.path.join(repo_path, "package.json")
    if os.path.exists(package_json_path):
        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                deps = list(data.get("dependencies", {}).keys()) + list(data.get("devDependencies", {}).keys())

                if "react" in deps:
                    detected.append("React")
                if "next" in deps or os.path.exists(os.path.join(repo_path, "next.config.js")):
                    detected.append("Next.js")
                if "vue" in deps:
                    detected.append("Vue.js")
                if "@angular/core" in deps or os.path.exists(os.path.join(repo_path, "angular.json")):
                    detected.append("Angular")
        except Exception:
            pass

    # Svelte
    if os.path.exists(os.path.join(repo_path, "svelte.config.js")):
        detected.append("Svelte")

    # --- BACKEND FRAMEWORKS ---
    if os.path.exists(os.path.join(repo_path, "manage.py")):
        detected.append("Django")

    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Python frameworks
            if file.endswith(".py"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        if "flask" in content:
                            detected.append("Flask")
                        if "fastapi" in content:
                            detected.append("FastAPI")
                except Exception:
                    pass

            # Node.js frameworks
            if file == "package.json":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        deps = list(data.get("dependencies", {}).keys())
                        if "express" in deps:
                            detected.append("Express.js")
                except Exception:
                    pass

    # ORM / CMS
    if os.path.exists(os.path.join(repo_path, "prisma")):
        detected.append("Prisma ORM")
    if os.path.exists(os.path.join(repo_path, "strapi")):
        detected.append("Strapi CMS")

    # --- STATIC / VANILLA WEBSITE DETECTION ---
    html_files = []
    js_files = []
    css_files = []
    has_bootstrap = False
    has_tailwind = False
    has_jquery = False

    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(".html"):
                html_files.append(file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        if "bootstrap" in content:
                            has_bootstrap = True
                        if "tailwind" in content:
                            has_tailwind = True
                        if "jquery" in content:
                            has_jquery = True
                except Exception:
                    pass

            elif file.endswith(".js"):
                js_files.append(file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        if "jquery" in content:
                            has_jquery = True
                except Exception:
                    pass

            elif file.endswith(".css"):
                css_files.append(file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        if "bootstrap" in content:
                            has_bootstrap = True
                        if "tailwind" in content:
                            has_tailwind = True
                except Exception:
                    pass

    # If plain HTML/CSS/JS without framework
    if html_files and (js_files or css_files) and not detected:
        detected.append("Vanilla HTML/CSS/JS")

        # Add optional libraries
        if has_bootstrap:
            detected.append("Bootstrap")
        if has_tailwind:
            detected.append("Tailwind CSS")
        if has_jquery:
            detected.append("jQuery")

    return list(sorted(set(detected)))
