from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import os, tempfile, zipfile, io, requests, shutil
from analyzer.framework_detector import detect_frameworks

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def analyze_github(request):
    """
    Analyze a GitHub repo (by URL) or a ZIP file upload.
    Returns a placeholder graph JSON for now.
    """

    temp_dir = tempfile.mkdtemp(prefix="stackinsight_")

    try:
        # Case 1: Handle GitHub Repo URL
        repo_url = request.data.get('repo_url', None)
        if repo_url:
            parts = repo_url.strip('/').split('/')
            if len(parts) < 2:
                return Response({"error": "Invalid GitHub URL"}, status=400)

            owner, repo = parts[-2], parts[-1]
            archive_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"
            r = requests.get(archive_url, stream=True, timeout=30)
            r.raise_for_status()

            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(temp_dir)
            extracted = os.path.join(temp_dir, f"{repo}-main")

            

        # Case 2: Handle ZIP File Upload
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
            
            extracted = temp_dir  # Root dir of extracted content

        else:
            return Response({"error": "Provide either a repo_url or upload a zip file."}, status=400)

        frameworks = detect_frameworks(extracted)
        demo_graph = {
            "frameworks": frameworks or ["Unknown"],
            "nodes": [{"id": "main.py", "language": "Python", "desc": "Sample file"}],
            "links": []
        }

        # Optional: Clean up temp dir after analysis
        shutil.rmtree(temp_dir, ignore_errors=True)

        return Response(demo_graph)

    except Exception as e:
        # Ensure cleanup on errors too
        shutil.rmtree(temp_dir, ignore_errors=True)
        return Response({"error": str(e)}, status=500)
