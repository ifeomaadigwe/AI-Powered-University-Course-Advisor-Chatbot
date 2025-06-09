import os
import requests
from bs4 import BeautifulSoup
from weasyprint import HTML

# Folder to save PDFs
os.makedirs("docs", exist_ok=True)

# URLs to scrape
url_map = {
    "Admissions": "https://www.en.uni-muenchen.de/students/degree/index.html",
    "Language Requirements": "https://www.en.uni-muenchen.de/students/int_student_guide/language/index.html",
    "Fees and Finances": "https://www.en.uni-muenchen.de/students/fees/index.html",
    "Living Costs and Funding": "https://www.en.uni-muenchen.de/students/int_student_guide/finance/index.html",
    "Enrollment Guide": "https://www.en.uni-muenchen.de/students/int_student_guide/first_steps/index.html",
    "Housing Info": "https://www.en.uni-muenchen.de/students/int_student_guide/housing/index.html",
    "Academic Calendar": "https://www.en.uni-muenchen.de/students/int_student_guide/dates/index.html",
    "Course Catalog": "https://www.en.uni-muenchen.de/students/int_student_guide/course_info/index.html",
    "Program Outline": "https://www.en.uni-muenchen.de/students/int_student_guide/programs/index.html"
}

# Main loop
for title, url in url_map.items():
    try:
        print(f"Fetching: {title}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")

        # Clean unwanted tags
        for tag in soup(["nav", "footer", "script", "style", "header", "aside"]):
            tag.decompose()

        # Convert to PDF
        clean_html = str(soup)
        filename = f"docs/{title.replace(' ', '_').lower()}.pdf"
        HTML(string=clean_html).write_pdf(filename)
        print(f"Saved: {filename}")
    except Exception as e:
        print(f"Failed on {title}: {e}")
