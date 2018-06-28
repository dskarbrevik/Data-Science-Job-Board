@ECHO OFF
path\to\glassdoor_scrape.py path\to\search_terms.txt && ^
path\to\processing.py && ^
START path\to\app.py
TIMEOUT 30
SET BROWSER=chrome.exe
START %BROWSER% -new-tab "http://127.0.0.1:8050/"
PAUSE
