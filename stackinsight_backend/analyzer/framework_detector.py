import os, re, json

def detect_frameworks(repo_path):
    """
    Detects frontend and backend frameworks used in a project by scanning files and dependencies.
    Returns a list of all detected frameworks.
    """

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

    if os.path.exists(os.path.join(repo_path, "svelte.config.js")):
        detected.append("Svelte")

    # --- BACKEND FRAMEWORKS ---
    found_django, found_flask, found_fastapi = False, False, False

    # Check requirements.txt for backend frameworks
    requirements_path = os.path.join(repo_path, "requirements.txt")
    if os.path.exists(requirements_path):
        try:
            with open(requirements_path, "r", encoding="utf-8") as f:
                reqs = f.read().lower()
                if "django" in reqs:
                    detected.append("Django")
                    if "rest_framework" in reqs or "djangorestframework" in reqs:
                        detected.append("Django REST Framework")
                    found_django = True
                if not found_flask and "flask" in reqs:
                    detected.append("Flask")
                    found_flask = True
                if not found_fastapi and "fastapi" in reqs:
                    detected.append("FastAPI")
                    found_fastapi = True
        except Exception:
            pass

    # Walk through files for import-based detection
    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Django hints
            if file in ["manage.py", "settings.py"]:
                detected.append("Django")
                found_django = True
                continue

            # Python files scan
            if file.endswith(".py"):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip().lower()
                            if line.startswith("#") or line.startswith('"""') or line.startswith("'''"):
                                continue

                            # Django
                            if not found_django and re.search(r'\b(from|import)\s+django\b', line):
                                detected.append("Django")
                                found_django = True

                            # Flask
                            elif not found_flask and re.search(r'\b(from|import)\s+flask\b', line):
                                detected.append("Flask")
                                found_flask = True

                            # FastAPI
                            elif not found_fastapi and re.search(r'\b(from|import)\s+fastapi\b', line):
                                detected.append("FastAPI")
                                found_fastapi = True
                except Exception:
                    pass

    # Prioritize Django over Flask/FastAPI
    if "Django" in detected:
        detected = [fw for fw in detected if fw not in ("Flask", "FastAPI")]

    # ORM / CMS
    if os.path.exists(os.path.join(repo_path, "prisma")):
        detected.append("Prisma ORM")
    if os.path.exists(os.path.join(repo_path, "strapi")):
        detected.append("Strapi CMS")

    # --- STATIC / VANILLA WEBSITE DETECTION ---
    html_files, js_files, css_files = [], [], []
    has_bootstrap, has_tailwind, has_jquery = False, False, False

    for root, _, files in os.walk(repo_path):
        for file in files:
            file_path = os.path.join(root, file)

            if file.endswith(".html"):
                html_files.append(file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        has_bootstrap |= "bootstrap" in content
                        has_tailwind |= "tailwind" in content
                        has_jquery |= "jquery" in content
                except Exception:
                    pass

            elif file.endswith(".js"):
                js_files.append(file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        has_jquery |= "jquery" in content
                except Exception:
                    pass

            elif file.endswith(".css"):
                css_files.append(file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().lower()
                        has_bootstrap |= "bootstrap" in content
                        has_tailwind |= "tailwind" in content
                except Exception:
                    pass

    # Simple static project detection
    if html_files and (js_files or css_files) and not detected:
        detected.append("Vanilla HTML/CSS/JS")
        if has_bootstrap:
            detected.append("Bootstrap")
        if has_tailwind:
            detected.append("Tailwind CSS")
        if has_jquery:
            detected.append("jQuery")

    return list(sorted(set(detected)))


def classify_frameworks(frameworks):
    """
    Splits detected frameworks into frontend and backend categories.
    Returns a dict with frontend_framework and backend_framework keys.
    """
    frontend_keywords = ["react", "next", "vue", "angular", "svelte", "tailwind", "bootstrap", "jquery", "vanilla"]
    backend_keywords = ["django", "flask", "fastapi", "express", "prisma", "strapi"]

    frontend = [fw for fw in frameworks if any(k in fw.lower() for k in frontend_keywords)]
    backend = [fw for fw in frameworks if any(k in fw.lower() for k in backend_keywords)]

    frontend_framework = ", ".join(frontend) if frontend else "None"
    backend_framework = ", ".join(backend) if backend else "None"

    return {
        "frontend_framework": frontend_framework,
        "backend_framework": backend_framework
    }
