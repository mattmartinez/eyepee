from flask import Flask, render_template, redirect, url_for, make_response, request
import logging
import sqlite3
import math
from token_utils import getContractScan, extractSafeyVector
import datetime

logging.basicConfig(
    filename='/var/log/scanner/scanner.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__)

@app.route('/so_long_and_goodnight')
def purge_db():
    passkey = request.form.get('passkey')
    if passkey != 'YOUR_PASSKEY':
        return "Invalid passkey"
    
    conn = sqlite3.connect('contracts.db')
    c = conn.cursor()

    c.execute('''
        DELETE FROM contracts
        WHERE timestamp NOT IN (
            SELECT MAX(timestamp) 
            FROM contracts
        )
    ''')

    conn.commit()
    conn.close()

    return "Database purged, kept most recent entry"



def format_number(value):
    if isinstance(value, str):
        return value
    elif isinstance(value, int):
        utc_datetime = datetime.datetime.utcfromtimestamp(value)
        utc_string = utc_datetime.strftime('%Y-%m-%d %H:%M:%S UTC')
        return utc_string
    else:
        return "{:,}".format(value)

app.jinja_env.filters['format_number'] = format_number

@app.route('/token_info', methods=['POST'])
def token_info():
    contract_address = request.get_json().get('contract_address')
    
    data = getContractScan(1, contract_address)
    data = extractSafeyVector(contract_address, data)

    app.logger.info(data)

    return data

@app.route('/ip')
def get_my_ip():
    return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

@app.route('/')
def index():
    return redirect(url_for('home', page_num=1))

@app.route('/<int:page_num>')
def home(page_num):
    contracts_per_page = 40

    conn = sqlite3.connect('contracts.db')
    c = conn.cursor()

    c.execute('SELECT * FROM contracts ORDER BY timestamp DESC')
    contracts = c.fetchall()

    total_contracts = len(contracts)
    total_pages = math.ceil(total_contracts / contracts_per_page)

    if page_num < 1 or page_num > total_pages:
        return redirect(url_for('home', page_num=total_pages))

    start = (page_num - 1) * contracts_per_page
    end = start + contracts_per_page

    contracts_to_render = contracts[start:end]

    rendered = render_template('template.html', contracts=contracts_to_render, total_pages=total_pages, current_page=page_num)

    with open("index.html", "w") as f:
        f.write(rendered)

    c.close()
    conn.close()

    return make_response(rendered)


if __name__ == "__main__":
    app.run(debug=False)
