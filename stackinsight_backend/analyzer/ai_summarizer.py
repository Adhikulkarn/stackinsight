import os
import json
import google.generativeai as genai

CACHE_PATH = "summary_cache.json"

def save_full_cache(final_output):
    """Always rewrite the cache with the final complete JSON output."""
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=2, ensure_ascii=False)
    print(f"💾 Cache updated → {CACHE_PATH}")


def _generate_with_fallback(prompt, context="general"):
    """Generate text using available Gemini models with fallback and log progress."""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model_names = [
        "models/gemini-2.5-flash",
        "models/gemini-2.5-pro",
        "models/gemini-flash-latest",
        "models/gemini-pro-latest"
    ]

    print(f"⚙️ Generating summary for: {context}")
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            result = model.generate_content(prompt)
            print(f"✅ Success: {context} summarized with {model_name}")
            return result.text.strip(), model
        except Exception as e:
            print(f"⚠️ Model {model_name} failed for {context}: {e}")
            continue

    print(f"❌ Failed to generate summary for: {context}")
    return "Summary unavailable.", None


def summarize_file(filename, content, language="unknown", functions=None, classes=None):
    """
    Summarize a single file (file summary + function/class summaries).
    Logs each stage for visibility.
    """
    print(f"\n🧩 Summarizing file: {filename} [{language}]")

    # --- File summary ---
    prompt = (
        f"You are a senior {language} developer. "
        f"Summarize this file in one short, clear, and precise sentence for documentation:\n\n"
        f"{content[:2500]}"
    )
    file_summary, model = _generate_with_fallback(prompt, context=filename)

    # --- Function-level summaries ---
    function_summaries = []
    if functions and model:
        for func in functions:
            print(f"🔍 Summarizing function: {func} in {filename}")
            func_prompt = (
                f"Explain briefly what the function `{func}` likely does based on its name and surrounding code:\n\n"
                f"{content[:1500]}"
            )
            f_summary, _ = _generate_with_fallback(func_prompt, context=f"{filename}:{func}")
            function_summaries.append({"name": func, "summary": f_summary})

    # --- Class-level summaries ---
    class_summaries = []
    if classes and model:
        for cls in classes:
            print(f"🏗️ Summarizing class: {cls} in {filename}")
            cls_prompt = (
                f"Summarize the purpose and behavior of the class `{cls}` in this file:\n\n"
                f"{content[:1500]}"
            )
            c_summary, _ = _generate_with_fallback(cls_prompt, context=f"{filename}:{cls}")
            class_summaries.append({"name": cls, "summary": c_summary})

    print(f"🧠 Summary complete for {filename}")
    return {
        "name": filename,
        "summary": file_summary,
        "functions": function_summaries,
        "classes": class_summaries
    }


def summarize_repository(repo_path, parsed_structure, frontend_framework="Unknown", backend_framework="Unknown", frameworks=None):
    """
    Generate AI-based summaries for all files in a repo + final project summary + graph.
    Verbose logs for full traceability.
    """
    print(f"\n🚀 Starting repository summarization for: {repo_path}")
    files_data = []

    total_files = len(parsed_structure)
    print(f"📁 Files to summarize: {total_files}")

    for index, (file, data) in enumerate(parsed_structure.items(), start=1):
        file_path = os.path.join(repo_path, file)
        if not os.path.exists(file_path):
            print(f"⚠️ Skipping missing file: {file}")
            continue

        print(f"\n[{index}/{total_files}] 🧠 Processing {file}")
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            language = (
                "Python" if file.endswith(".py") else
                "JavaScript" if file.endswith((".js", ".jsx")) else
                "HTML" if file.endswith(".html") else
                "CSS" if file.endswith(".css") else
                "text"
            )

            file_summary = summarize_file(
                file,
                content,
                language,
                functions=data.get("functions", []),
                classes=data.get("classes", [])
            )
            files_data.append(file_summary)

        except Exception as e:
            print(f"❌ Error summarizing {file}: {e}")
            files_data.append({
                "name": file,
                "summary": f"Error summarizing file: {e}",
                "functions": [],
                "classes": []
            })

    print("\n🧩 Generating overall project summary...")
    combined_text = "\n".join([f"{f['name']}: {f['summary']}" for f in files_data])
    project_prompt = (
        "You are an experienced software architect. "
        "Based on the following file summaries, provide a single, cohesive overview "
        "of the entire project's purpose, architecture, and main components:\n\n"
        f"{combined_text[:8000]}"
    )
    project_summary, _ = _generate_with_fallback(project_prompt, context="project_overview")

    # --- Build Graph ---
    repo_label = os.path.basename(repo_path.rstrip("/"))
    nodes = [{"id": "repository", "label": repo_label}]
    links = []

    for f in files_data:
        nodes.append({"id": f["name"], "label": f["name"]})
        links.append({"source": "repository", "target": f["name"]})

        for func in f["functions"]:
            nodes.append({"id": func["name"], "label": func["name"]})
            links.append({"source": f["name"], "target": func["name"]})

        for cls in f["classes"]:
            nodes.append({"id": cls["name"], "label": cls["name"]})
            links.append({"source": f["name"], "target": cls["name"]})

    # --- Final Output ---
    final_output = {
        "frontend_framework": frontend_framework or "Unknown",
        "backend_framework": backend_framework or "Unknown",
        "frameworks": frameworks or [],
        "project_summary": project_summary,
        "repository_graph": {
            "name": "repository",
            "summary": project_summary,
            "files": files_data
        },
        "nodes": nodes,
        "links": links
    }

    save_full_cache(final_output)
    print(f"\n✅ Repository summarized successfully → {len(files_data)} files processed.")
    return final_output
