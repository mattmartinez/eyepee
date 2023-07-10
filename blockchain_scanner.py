import time
import json
import logging
import sqlite3
from web3 import Web3, HTTPProvider
from web3.exceptions import BlockNotFound
from web3.middleware import geth_poa_middleware 

# Configure logging
logging.basicConfig(
    filename='/var/log/scanner/scanner.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Import ERC20 ABI
ERC20_ABI = [{"constant":True,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"}]

# Connect to Ethereum mainnet
w3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/a4f07ce23d074bb1bff907585859734a'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Connect to the SQLite database (this will create it if it doesn't exist)
conn = sqlite3.connect('contracts.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE IF NOT EXISTS contracts
            (address text, creator text, block integer, name text, supply text, timestamp integer)''')  # Add `timestamp` column of type integer

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
                return  # Skip this iteration and try again in the next one

            for tx in block.transactions:
                if tx['to'] is None:
                    receipt = self.w3.eth.get_transaction_receipt(tx['hash'])
                    contract_address = receipt['contractAddress']

                    if contract_address is not None:
                        # Print contract address
                        logging.info(f"Contract address: {contract_address}")
                        # Create contract instance
                        contract = self.w3.eth.contract(address=contract_address, abi=ERC20_ABI)

                        try:
                            # Fetch token name and total supply
                            token_name = contract.functions.name().call()
                            total_supply = contract.functions.totalSupply().call()

                            # Fetch contract creator's address
                            contract_creator = receipt['from']

                            # Only print details if token name is available
                            if token_name:
                                logging.info(f"New contract (assumed ERC20) created at {contract_address} in block {current_block}, Token Name: {token_name}, Total Supply: {total_supply}")

                                # Get current timestamp
                                timestamp = int(time.time())

                                # Insert contract into the database
                                try:
                                    c.execute("INSERT INTO contracts VALUES (?, ?, ?, ?, ?, ?)",
                                              (contract_address, contract_creator, current_block, token_name, str(total_supply), timestamp))  # Convert `total_supply` to string before insertion
                                    # Commit the changes
                                    conn.commit()
                                except Exception as e:
                                    logging.info(f'Could not insert contract at {contract_address} into the database. Error: {e}')
                        except Exception as e:
                            # Check if error message contains "execution reverted" and only print if it does not
                            if "execution reverted" not in str(e):
                                logging.info(f"Could not fetch details for contract at {contract_address}. Error: {str(e)}")

scanner = Scanner(w3)

while True:
    scanner.scan_blockchain()
    time.sleep(10)