import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot

def test_engines():
    print("=" * 80)
    print("PASHA HUNT 2.0 — JOB SOURCING ENGINES AUDIT & TEST SUITE")
    print("=" * 80)
    print(f"{'Engine Name':<28} | {'Status':<10} | {'Jobs Found':<12} | {'Latency':<8} | {'Notes / Errors'}")
    print("-" * 80)
    
    results = []
    
    for i, fn in enumerate(bot.SOURCES):
        name = fn.__name__
        start_t = time.time()
        status = "PASS"
        jobs_found = 0
        error_msg = ""
        
        try:
            # Execute source engine
            job_gen = fn()
            jobs = list(job_gen) if job_gen else []
            jobs_found = len(jobs)
            elapsed = time.time() - start_t
            
            # Check structure of returned jobs if any
            if jobs:
                first = jobs[0]
                if not isinstance(first, dict) or not first.get("title"):
                    status = "WARN"
                    error_msg = "Invalid job dictionary structure"
                else:
                    error_msg = f"OK (e.g. {first.get('company', 'Unknown')[:18]})"
            else:
                status = "EMPTY"
                error_msg = "0 jobs returned (rate-limited, empty feed, or cache cold)"
                
        except Exception as e:
            elapsed = time.time() - start_t
            status = "FAIL"
            error_msg = f"{e.__class__.__name__}: {str(e)[:40]}"
            
        print(f"{name:<28} | {status:<10} | {jobs_found:<12} | {elapsed:>6.2f}s | {error_msg}")
        results.append({
            "engine": name,
            "status": status,
            "jobs_found": jobs_found,
            "latency": elapsed,
            "notes": error_msg
        })
        
    print("-" * 80)
    passed = sum(1 for r in results if r["status"] in ("PASS", "WARN"))
    print(f"SUMMARY: {passed}/{len(results)} engines operational. Total raw items extracted: {sum(r['jobs_found'] for r in results)}")
    return results

if __name__ == "__main__":
    test_engines()
