import time
import json
import logging
import sqlite3
from web3 import Web3, HTTPProvider
from web3.exceptions import BlockNotFound
from web3.middleware import geth_poa_middleware 

logging.basicConfig(
    filename='/var/log/scanner/scanner.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

w3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/API_KEY_HERE'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

conn = sqlite3.connect('contracts.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS contracts
            (address text, creator text, block integer, name text, supply text, timestamp integer)''')

class Scanner:
    def __init__(self, w3):
        self.w3 = w3
        self.latest_block = self.w3.eth.block_number

    def scan_blockchain(self):
        current_block = self.w3.eth.block_number
        logging.info(f"Current block number: {current_block}")
        if current_block > self.latest_block:
            self.latest_block = current_block
            try:
                block = self.w3.eth.get_block(current_block, full_transactions=True)
            except BlockNotFound:
                logging.error(f"Block {current_block} not found.")
                return

            for tx in block.transactions:
                if tx['to'] is None:
                    receipt = self.w3.eth.get_transaction_receipt(tx['hash'])
                    contract_address = receipt['contractAddress']

                    if contract_address is not None:
                        logging.info(f"Contract address: {contract_address}")
                        contract = self.w3.eth.contract(address=contract_address, abi=ERC20_ABI)

                        try:
                            token_name = contract.functions.name().call()
                            total_supply = contract.functions.totalSupply().call()

                            contract_creator = receipt['from']

                            if token_name:
                                logging.info(f"New contract (assumed ERC20) created at {contract_address} in block {current_block}, Token Name: {token_name}, Total Supply: {total_supply}")

                                timestamp = int(time.time())

                                try:
                                    c.execute("INSERT INTO contracts VALUES (?, ?, ?, ?, ?, ?)",
                                              (contract_address, contract_creator, current_block, token_name, str(total_supply), timestamp))
                                    conn.commit()
                                except Exception as e:
                                    logging.info(f'Could not insert contract at {contract_address} into the database. Error: {e}')
                        except Exception as e:
                            if "execution reverted" not in str(e):
                                logging.info(f"Could not fetch details for contract at {contract_address}. Error: {str(e)}")

scanner = Scanner(w3)

while True:
    scanner.scan_blockchain()
    time.sleep(10)