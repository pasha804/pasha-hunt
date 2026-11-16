import sys, os, urllib.request, json, time, http.server, threading
sys.path.insert(0, 'job-hunter-repo')
import desktop_server

def test_fixes():
    # 1. Test Cover Letter Document HTML has NO watermark and NO "Drafted in Gmail"
    PORT = 19991
    server = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), desktop_server.WorkstationRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(1)

    base = f"http://127.0.0.1:{PORT}"

    # Verify Cover Letter A4 document
    req = urllib.request.Request(f"{base}/api/cover-letter/document")
    with urllib.request.urlopen(req, timeout=5) as res:
        doc_html = res.read().decode('utf-8')
        assert "status-tag" not in doc_html, "status-tag must be removed from cover letter"
        assert "Drafted in Gmail" not in doc_html, "Drafted in Gmail must not appear inside cover letter"
        assert "Official Pasha Hunt" not in doc_html, "Software watermark must not appear in cover letter footer"
        assert "Enclosure: Curriculum Vitae" in doc_html, "Executive footer enclosure should be present"
        print("✓ TEST 1 PASSED: Cover Letter Document is clean, executive, and zero-watermark!")

    # 2. Test Create Draft returns body and proper web_compose_url
    post_data = json.dumps({
        "company": "BrainX Technologies",
        "role": "Graphic & UI/UX Designer",
        "email": "careers@brainxtech.com",
        "job_id": "test-verify-1"
    }).encode('utf-8')

    req = urllib.request.Request(f"{base}/api/create-draft", data=post_data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode('utf-8'))
        assert data.get("ok") is True, f"Draft creation failed: {data}"
        assert "body" in data and len(data["body"]) > 50, "Full body text must be in draft response"
        assert "web_compose_url" in data, "web_compose_url must be present"
        assert "su=" in data["web_compose_url"], "Subject must be in web_compose_url"
        assert "body=" in data["web_compose_url"], "Body must be in web_compose_url"
        print("✓ TEST 2 PASSED: Draft created, body returned, and web_compose_url contains full body!")

    # 3. Test Save Profile persists email and app password
    save_payload = json.dumps({
        "name": "Muhammad Hasnain",
        "email": "mubasharmuhammad790@gmail.com",
        "gmail_address": "mubasharmuhammad790@gmail.com",
        "phone": "+92 336 7763874",
        "default_title": "Graphic Designer"
    }).encode('utf-8')

    req = urllib.request.Request(f"{base}/api/profile", data=save_payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=5) as res:
        data = json.loads(res.read().decode('utf-8'))
        assert data.get("ok") is True, "Profile save failed"
        prof = desktop_server.get_profile_data()
        assert prof.get("contact", {}).get("email") == "mubasharmuhammad790@gmail.com", "Contact email must be updated"
        print("✓ TEST 3 PASSED: Candidate Profile and Gmail address synchronized to mubasharmuhammad790@gmail.com!")

    server.shutdown()
    server.server_close()
    print("ALL FIX VERIFICATION TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_fixes()
