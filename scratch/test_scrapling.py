from scrapling import Fetcher, Selector, StealthyFetcher
import re

html_doc = """
<!DOCTYPE html>
<html>
<head><title>Careers at Acme Corp</title></head>
<body>
    <div class="header">
        <h1>Careers Portal</h1>
    </div>
    <div class="job-list">
        <div class="job-item" data-id="job-101">
            <h2 class="title">Senior AI & Full-Stack Engineer</h2>
            <div class="meta">
                <span class="location">Remote, Worldwide</span>
                <span class="salary">$120,000 - $160,000</span>
            </div>
            <p class="description">Looking for Python, LangGraph, and Scrapling expertise. Contact careers@acmecorp.com or talent-team@acmecorp.com</p>
            <a href="https://acmecorp.com/apply/101" class="apply-btn">Apply Now</a>
        </div>
        <div class="job-item" data-id="job-102">
            <h2 class="title">Lead Product Designer</h2>
            <div class="meta">
                <span class="location">Hybrid, San Francisco</span>
                <span class="salary">$140,000</span>
            </div>
            <p class="description">Design systems in Figma. Send portfolio to design.jobs@acmecorp.com</p>
            <a href="https://acmecorp.com/apply/102" class="apply-btn">Apply Now</a>
        </div>
    </div>
</body>
</html>
"""

def test_selector_features():
    page = Selector(html_doc)
    print("Page title:", page.css("title::text").get())
    
    # CSS selector extraction
    titles = page.css(".job-item .title::text").getall()
    print("Extracted Titles:", titles)
    assert len(titles) == 2, f"Expected 2 titles, got {len(titles)}"
    
    # XPath extraction
    locations = page.xpath('//span[@class="location"]/text()').getall()
    print("Extracted Locations:", locations)
    assert len(locations) == 2, f"Expected 2 locations, got {len(locations)}"
    
    # Email extraction across all text elements or paragraphs
    all_text = " ".join(page.xpath('//text()').getall())
    emails = set(re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", all_text))
    print("Extracted Emails:", emails)
    assert "careers@acmecorp.com" in emails
    assert "talent-team@acmecorp.com" in emails
    assert "design.jobs@acmecorp.com" in emails

    print("ALL SCRAPLING SELECTOR TESTS PASSED!")

if __name__ == "__main__":
    test_selector_features()
