from flask import Flask, render_template, redirect, url_for, make_response
import logging
import sqlite3

# Configure logging
logging.basicConfig(
    filename='/var/log/scanner/scanner.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

@app.route('/')
def index():
    logging.info("Accessed index route")
    return redirect(url_for('home', page_num=1))

@app.route('/<int:page_num>')
def home(page_num):
    logging.info(f"Accessed home route with page number {page_num}")

    contracts_per_page = 20

    # Connect to the SQLite database
    conn = sqlite3.connect('contracts.db')
    c = conn.cursor()

    # Load contracts from the database
    c.execute('SELECT * FROM contracts')
    contracts = c.fetchall()

    total_pages = (len(contracts) + contracts_per_page - 1) // contracts_per_page

    if page_num < 1 or page_num > total_pages:
        return redirect(url_for('home', page_num=total_pages))  # Redirect to the last available page

    start = (page_num - 1) * contracts_per_page
    end = start + contracts_per_page

    contracts_to_render = contracts[start:end]

    rendered = render_template('template.html', contracts=contracts_to_render, page_num=page_num)
    logging.info(f"Rendered template: {rendered[:100]}...")  # Log the first 100 characters of the rendered HTML

    with open("index.html", "w") as f:
        f.write(rendered)
    logging.info(f"Wrote rendered template to /opt/bitnami/nginx/html/index.html")

    # Close the cursor and connection
    c.close()
    conn.close()

    return make_response(rendered)


if __name__ == "__main__":
    app.run(debug=True)
