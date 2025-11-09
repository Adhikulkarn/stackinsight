from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import os, tempfile, zipfile, io, requests, shutil

from analyzer.framework_detector import detect_frameworks, classify_frameworks
from analyzer.code_parser import analyze_code_structure
from analyzer.ai_summarizer import summarize_repository


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def analyze_github(request):
    """
    Analyze a GitHub repo (by URL) or a ZIP upload.
    Detect frameworks, parse structure, and generate AI summaries with function/class insights.
    """

    temp_dir = tempfile.mkdtemp(prefix="stackinsight_")

    try:
        extracted = None

        # --- CASE 1: GitHub Repository URL ---
        repo_url = request.data.get("repo_url", None)
        if repo_url:
            parts = repo_url.strip("/").split("/")
            if len(parts) < 2:
                return Response({"error": "Invalid GitHub URL"}, status=400)

            owner, repo = parts[-2], parts[-1]
            archive_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"

            print(f"📦 Fetching repo archive from: {archive_url}")
            r = requests.get(archive_url, stream=True, timeout=30)
            if r.status_code != 200:
                return Response({"error": f"Failed to fetch repo: {r.status_code}"}, status=400)

            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(temp_dir)
            base_path = os.path.join(temp_dir, f"{repo}-main")

            # ✅ Detect nested code folder (common for frameworks)
            extracted = base_path
            subdirs = [
                os.path.join(base_path, d)
                for d in os.listdir(base_path)
                if os.path.isdir(os.path.join(base_path, d))
            ]
            for subdir in subdirs:
                if any(
                    os.path.exists(os.path.join(subdir, f))
                    for f in ["manage.py", "package.json", "index.html"]
                ):
                    extracted = subdir
                    break

        # --- CASE 2: Local ZIP Upload ---
        elif "file" in request.FILES:
            uploaded_file = request.FILES["file"]
            if not uploaded_file.name.endswith(".zip"):
                return Response({"error": "Only ZIP files are allowed"}, status=400)

            zip_path = os.path.join(temp_dir, uploaded_file.name)
            with open(zip_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(temp_dir)
            extracted = temp_dir

        else:
            return Response({"error": "Provide either a repo_url or upload a zip file."}, status=400)

        # --- STAGE 3: FRAMEWORK DETECTION ---
        frameworks = detect_frameworks(extracted)
        classification = classify_frameworks(frameworks)

        # --- STAGE 4: CODE PARSING ---
        parsed_structure = analyze_code_structure(extracted)

        # --- STAGE 5: AI SUMMARIZATION ---
        repo_summary = {}
        try:
            # Pass detected frameworks into the summarizer so final cache output includes them
            repo_summary = summarize_repository(
                extracted,
                parsed_structure,
                frontend_framework=classification.get("frontend_framework"),
                backend_framework=classification.get("backend_framework"),
                frameworks=frameworks
            )
        except Exception as e:
            repo_summary = {"error": f"AI summarization failed: {str(e)}"}

        # --- BUILD FINAL RESPONSE ---
        result = {
            "frontend_framework": classification["frontend_framework"],
            "backend_framework": classification["backend_framework"],
            "frameworks": frameworks or ["Unknown"],
            "structure": parsed_structure,
            "project_summary": repo_summary.get("project_summary", "Summary unavailable."),
            "repository_graph": repo_summary.get("repository_graph", {}),
            "nodes": repo_summary.get("nodes", []),
            "links": repo_summary.get("links", [])
        }

        # --- CLEANUP ---
        shutil.rmtree(temp_dir, ignore_errors=True)
        return Response(result, status=200)

    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return Response({"error": str(e)}, status=500)
