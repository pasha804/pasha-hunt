import sys, os, json, urllib.request, threading, time, http.server
sys.path.insert(0, 'job-hunter-repo')
import desktop_server

def test_draft():
    PORT = 19898
    server = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), desktop_server.WorkstationRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(1)

    base = f"http://127.0.0.1:{PORT}"

    post_data = json.dumps({
        "company": "Canva",
        "role": "Brand & Visual Designer",
        "email": "careers@canva.com",
        "job_id": "test-canva-1"
    }).encode('utf-8')

    req = urllib.request.Request(f"{base}/api/create-draft", data=post_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode('utf-8'))
        print('Create Draft Result:')
        print(json.dumps(data, indent=2))
        assert data.get("ok") is True, f"Expected ok True, got {data}"
        assert "web_compose_url" in data, "web_compose_url should be returned"
        print('web_compose_url:', data.get("web_compose_url"))

    # Verify tracker has the new entry
    tracker = desktop_server.get_tracker_data()
    print('Tracker entries after draft:', len(tracker))
    assert ('canva', 'brand & visual designer') in tracker, "Canva should be in tracker"

    # Verify stats
    req = urllib.request.Request(f"{base}/api/stats")
    with urllib.request.urlopen(req, timeout=5) as res:
        stats = json.loads(res.read().decode('utf-8'))
        print('Stats drafted count:', stats.get("drafted"), 'total_applied:', stats.get("total_applied"))
        assert stats.get("drafted") >= 3, "Drafted count should be at least 3"

    server.shutdown()
    server.server_close()
    print('ALL DRAFT CREATION TESTS PASSED!')

if __name__ == '__main__':
    test_draft()
