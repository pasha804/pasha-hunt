import re, os

with open('job-hunter-repo/desktop_ui/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

script_match = re.search(r'<script>(.*?)</script>', text, re.DOTALL)
if script_match:
    js = script_match.group(1)
    defined = set(re.findall(r'function\s+([A-Za-z0-9_]+)', js))
    defined.update(re.findall(r'(?:let|const|var)\s+([A-Za-z0-9_]+)\s*=\s*(?:function|\()', js))
    
    onclicks = re.findall(r'onclick=["\']([A-Za-z0-9_]+)\(', text)
    missing_handlers = [h for h in set(onclicks) if h not in defined]
    print('Missing onclick handlers in JS:', missing_handlers)

    # Check for calls to undefined functions inside js
    calls = set(re.findall(r'\b([A-Za-z0-9_]+)\s*\(', js))
    standard_globals = {
        'fetch', 'alert', 'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
        'encodeURIComponent', 'decodeURIComponent', 'parseInt', 'parseFloat', 'isNaN', 'isFinite',
        'showToast', 'escapeHtml', 'escapeJs', 'Boolean', 'Number', 'String', 'Array', 'Object',
        'Function', 'Date', 'RegExp', 'Error', 'JSON', 'Math', 'console', 'document', 'window',
        'navigator', 'localStorage', 'sessionStorage', 'history', 'location', 'event', 'closeModals',
        'require', 'FileReader', 'Blob', 'URL', 'FormData', 'CustomEvent', 'Event', 'MutationObserver'
    }
    suspect_calls = [c for c in calls if c not in defined and c not in standard_globals and not c.startswith('_')]
    print('Suspect function calls in JS:', suspect_calls)
