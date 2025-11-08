from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import os, tempfile, zipfile, io, requests, shutil

from analyzer.framework_detector import detect_frameworks, classify_frameworks


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def analyze_github(request):
    """
    Analyze a GitHub repo (by URL) or a ZIP file upload.
    Detects frameworks and provides frontend/backend classification.
    """

    temp_dir = tempfile.mkdtemp(prefix="stackinsight_")

    try:
        extracted = None

        # --- CASE 1: Handle GitHub Repo URL ---
        repo_url = request.data.get('repo_url', None)
        if repo_url:
            parts = repo_url.strip('/').split('/')
            if len(parts) < 2:
                return Response({"error": "Invalid GitHub URL"}, status=400)

            owner, repo = parts[-2], parts[-1]
            archive_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"

            r = requests.get(archive_url, stream=True, timeout=30)
            if r.status_code != 200:
                return Response({"error": f"Failed to fetch repo: {r.status_code}"}, status=400)

            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(temp_dir)
            extracted = os.path.join(temp_dir, f"{repo}-main")

        # --- CASE 2: Handle ZIP File Upload ---
        elif "file" in request.FILES:
            uploaded_file = request.FILES["file"]
            if not uploaded_file.name.endswith(".zip"):
                return Response({"error": "Only ZIP files are allowed"}, status=400)

            zip_path = os.path.join(temp_dir, uploaded_file.name)
            with open(zip_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(temp_dir)
            extracted = temp_dir

        else:
            return Response({"error": "Provide either a repo_url or upload a zip file."}, status=400)

        # --- FRAMEWORK DETECTION ---
        frameworks = detect_frameworks(extracted)
        classification = classify_frameworks(frameworks)

        # --- TEMP PLACEHOLDER UNTIL PARSER IS ADDED ---
        result = {
            "frontend_framework": classification["frontend_framework"],
            "backend_framework": classification["backend_framework"],
            "frameworks": frameworks or ["Unknown"],
            "nodes": [{"id": "main.py", "language": "Python", "desc": "Placeholder node"}],
            "links": []
        }

        # --- CLEANUP ---
        shutil.rmtree(temp_dir, ignore_errors=True)

        return Response(result, status=200)

    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        return Response({"error": str(e)}, status=500)
