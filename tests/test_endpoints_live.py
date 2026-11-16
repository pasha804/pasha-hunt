import sys, os, json, urllib.request, threading, time, http.server
sys.path.insert(0, 'job-hunter-repo')
import desktop_server

def run_tests():
    # Start server on a test port
    PORT = 19899
    server = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), desktop_server.WorkstationRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(1)

    base = f"http://127.0.0.1:{PORT}"
    results = {}

    endpoints = [
        "/api/stats",
        "/api/drafts",
        "/api/tracker",
        "/api/jobs?limit=5",
        "/api/profile",
        "/api/cv/info",
        "/api/get-cover-letters"
    ]

    for ep in endpoints:
        try:
            req = urllib.request.Request(f"{base}{ep}")
            with urllib.request.urlopen(req, timeout=5) as res:
                data = json.loads(res.read().decode('utf-8'))
                results[ep] = {"status": res.status, "ok": True, "type": type(data).__name__, "sample": str(data)[:100]}
        except Exception as e:
            results[ep] = {"ok": False, "error": str(e)}

    # Test POST /api/tailor
    try:
        post_data = json.dumps({"requirement": "Designed logos for clients"}).encode('utf-8')
        req = urllib.request.Request(f"{base}/api/tailor", data=post_data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode('utf-8'))
            results["POST /api/tailor"] = {"status": res.status, "ok": data.get("ok", False), "bullet": data.get("bullet", "")[:80]}
    except Exception as e:
        results["POST /api/tailor"] = {"ok": False, "error": str(e)}

    server.shutdown()
    server.server_close()

    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    run_tests()
