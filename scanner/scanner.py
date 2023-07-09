import time
import logging
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware 
from jinja2 import Environment, FileSystemLoader

# Configure logging
logging.basicConfig(
    filename='/var/log/scanner/scanner.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Import ERC20 ABI
ERC20_ABI = [{"constant":True,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"}]

# Connect to Ethereum mainnet
w3 = Web3(HTTPProvider('https://mainnet.infura.io/v3/{API_KEY}'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load Jinja2 template
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('template.html')

latest_block = w3.eth.block_number
contracts = []

while True:
    current_block = w3.eth.block_number
    logging.info(f"Current block number: {current_block}")
    if current_block > latest_block:
        latest_block = current_block
        block = w3.eth.get_block(current_block, full_transactions=True)

        for tx in block.transactions:
            if tx['to'] is None:
                receipt = w3.eth.get_transaction_receipt(tx['hash'])
                contract_address = receipt['contractAddress']

                if contract_address is not None:
                    # Print contract address
                    logging.info(f"Contract address: {contract_address}")
                    # Create contract instance
                    contract = w3.eth.contract(address=contract_address, abi=ERC20_ABI)

                    try:
                        # Fetch token name and total supply
                        token_name = contract.functions.name().call()
                        total_supply = contract.functions.totalSupply().call()

                        # Fetch contract creator's address
                        contract_creator = receipt['from']

                        # Only print details if token name is available
                        if token_name:
                            logging.info(f"New contract (assumed ERC20) created at {contract_address} in block {current_block}, Token Name: {token_name}, Total Supply: {total_supply}")
                            contracts.append({
                                "address": contract_address,
                                "creator": contract_creator,
                                "block": current_block,
                                "name": token_name,
                                "supply": total_supply
                            })
                            # Generate new index.html file
                            with open("index.html", "w") as f:
                                f.write(template.render(contracts=contracts))
                    except Exception as e:
                        # Check if error message contains "execution reverted" and only print if it does not
                        if "execution reverted" not in str(e):
                            logging.info(f"Could not fetch details for contract at {contract_address}. Error: {str(e)}")
    else:
        time.sleep(10)
