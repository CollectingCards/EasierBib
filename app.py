from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import html
import requests
import re

app = Flask(__name__, static_folder="static", template_folder="templates")

########### FORMAT CITATION FUNCTIONS ###########

def format_mla(author, year, title, publisher):
    return f"{author}. <i>{title}</i>. {publisher}, ({year})."

def format_mla_website(author, year, title, publisher, access_date, url):
    return f'{author} "<i>{title}</i>." {publisher}, ({year}). {access_date}, {url}.'


def format_apa(author, year, title, publisher):
    return f"{author} ({year}). <i>{title}</i>. {publisher}."

def format_apa_website(author, year, title, url, access_date):
    return f"{author} ({year}). <i>{title}</i>. Retrieved {access_date}, from {url}"

########### END FORMAT CITATION FUNCTIONS ###########


# Prevents users from entering executable code or HTML into their form submission.
# Since I use |safe to allow the direct rendering of HTML through my Python code,
# this is done so code can only be run on the site through the back-end directly.
def sanitize(text):
    return html.escape(text)


##############################################################################
######################### START @APP.ROUTE FUNCTIONS #########################
##############################################################################
# @app.route is a ROUTE DECORATOR. It tells Flask:
# When a browser visits the root URL ('/'), use the function below (index() )
# Accepts 2 kinds of HTTP requests: GET = loading the page; POST = submitting a form


######################### START CREATE CITATION #########################
@app.route('/', methods=['GET', 'POST'])
def index():
    citation = None # Start with no citation


    #### NOTE about request vs requests:
    #### request [no s] references the incoming POST request from web app
    #### requests.get() makes HTTP requests to outside APIs (like CrossRef)

    if request.method == 'POST':    # If user submitted citation info
        # Gets info about how to format citation
        style = request.form['style']
        source_type = request.form.get('source_type', 'book')

        # Gets information about citation itself
        author = sanitize(request.form['author'])
        title = sanitize(request.form['title'])
        year = sanitize(request.form['year'])
        publisher = sanitize(request.form['publisher'])
        url = sanitize(request.form.get('url', ''))
        access_date = sanitize(request.form.get('access_date', ''))

        # Formats the citation properly
        if source_type == 'book':
            if style == 'MLA':
                citation = format_mla(author, title, publisher, year)
            elif style == 'APA':
                citation = format_apa(author, year, title, publisher)

        elif source_type == 'website':
            if style == 'MLA':
                citation = format_mla_website(author, year, title, publisher, access_date, url)
            elif style == 'APA':
                citation = format_apa_website(author, year, title, url, access_date)


    # Tells Flask to render the HTML file and send it to the browser
    # The 'citation' variable is passed into the template so Jinja 2 can access it
        # Used by if statement in HTML file
    return render_template('index.html', citation=citation) 
########################## END CREATE CITATION ##########################


########################## START DOI LOOKUP #############################
@app.route("/lookup-doi", methods=["POST"])
# Accepts JSON from the POST and grabs the DOI
def lookup_doi():
    data = request.get_json()
    doi = data.get("doi", "").strip()

    if not doi:
        return jsonify({"error": "DOI is required"})
    
    try:
        # Sends a GET request to CrossRef's API to fetch citation data.
        url = f"https://api.crossref.org/works/{doi}"
        response = requests.get(url)
        response.raise_for_status()

        # Pulls out the main citation data from the JSON response.
        item = response.json()["message"]

        # Combines author first+last names into a single string, separated by commas.
        author = ", ".join([
            f"{a.get('given', '')} {a.get('family', '')}".strip()
            for a in item.get("author", [])
        ])

        # Gets the title (it's inside a list, so we use [0]).
        title = item.get("title", [""])[0]

        # Tries to extract the publication year from either print or online metadata.
        year = item.get("published-print", {}).get("date-parts", [[None]])[0][0] \
            or item.get("published-online", {}).get("date-parts", [[None]])[0][0] \
            or ""
        
        # Gets the publisher name
        publisher = item.get("publisher", "")

        # Sends the structured citation data to the frontend.
        return jsonify({
            "author": author,
            "title": title,
            "year": str(year),
            "publisher": publisher
        })
    
    # If anything fails (like invalid DOI), sends back an error message.
    except Exception as e:
        return jsonify({"error": "DOI lookup failed or DOI not found."})
########################### END DOI LOOKUP ##############################
    

########################## START ISBN LOOKUP #############################
@app.route("/lookup-isbn", methods=["POST"])
# Accepts JSON from the POST and grabs the ISBN
def lookup_isbn():
    data = request.get_json()
    isbn = data.get("isbn", "").strip()

    if not isbn:
        return jsonify({"error": "ISBN is required"})

    try:
        # Sends a GET request to Open Library's API to fetch citation data.
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=data&format=json"
        response = requests.get(url)
        response.raise_for_status()

        # Pulls out the main citation data from the JSON response.
        book_data = response.json().get(f"ISBN:{isbn}")

        if not book_data:
            return jsonify({"error": "No book found for that ISBN"})

        # Parse citation fields
        title = book_data.get("title", "")
        authors = book_data.get("authors", [])
        author = ", ".join([a["name"] for a in authors]) # Separates author names by comma
        publisher = book_data.get("publishers", [{}])[0].get("name", "")
        year = book_data.get("publish_date", "")

        # Sends the structured citation data to the frontend.
        return jsonify({
            "title": title,
            "author": author,
            "publisher": publisher,
            "year": year
        })

    # If anything fails, sends back an error message.
    except Exception as e:
        return jsonify({"error": "Failed to fetch ISBN data"})
########################### END ISBN LOOKUP ##############################


########################## START URL LOOKUP #############################
@app.route("/lookup-url", methods=["POST"])
# Accepts JSON from the POST and grabs the ISBN
def lookup_url():
    data = request.get_json()
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "URL is required"})

    try:
        # Sends a GET request to Open BeautifulSoup's API to fetch citation data.
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Try to extract title from <title> tag or og:title
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag else soup.title.string if soup.title else ""

        # Try to extract publisher from meta tags or domain
        site_name_tag = soup.find("meta", property="og:site_name")
        publisher = site_name_tag["content"] if site_name_tag else urlparse(url).netloc

        # AUTHOR: Look for meta name="author" or similar tags. Defaults to unknown if not found
        author_tag = soup.find("meta", attrs={"name": "author"})
        author = author_tag["content"].strip() + "." if author_tag and author_tag.get("content") else ""

        # YEAR: Try to find a year-like pattern in the page content. Defaults to empty string if not found
        year_match = re.search(r"\b(19|20)\d{2}\b", soup.get_text()) # re => regular expressions import
        year = year_match.group(0) if year_match else ""

        return jsonify({
            "author": author,
            "title": title,
            "year": year,
            "publisher": publisher,
            "url": url
        })

    except Exception as e:
        return jsonify({"error": "Failed to fetch or parse URL metadata."})
########################### END URL LOOKUP ##############################


##############################################################################
########################## END @APP.ROUTE FUNCTIONS ##########################
##############################################################################

if __name__ == '__main__':
    app.run()
