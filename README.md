# ERC20 Scanner
---

http://eyepee.lol  **This app is scanner that keeps track of newly created ERC20 tokens on the Ethereum blockchain.**

- It continuously checks for new blocks and scans the transactions within those blocks.
- When it detects a contract creation transaction, it retrieves the contract address and the address of the contract creator.
- It fetches the token name and total supply.
- If the token name is available, it logs the details of the newly created ERC20 token, including the contract address, the creator's address, the token name, and the total supply.
- The script consolidates the contract address and creator's address into a single column for a more streamlined display, with each being a clickable link leading to their respective pages on Etherscan.
- It adjusts the table's width dynamically to utilize the available screen space efficiently, reducing excessive white space.
- It implements pagination controls, center-aligned, to enable easy navigation across different pages of token data.
- The data is rendered using Jinja2 into a neatly organized table.
- Integrated with https://gopluseco.io for Token Info button, which displays the token's security score and other information.
- The application auto-refreshes every 60s to keep the data up-to-date with the latest tokens.
- To purge the list of coins use the URL: http://eyepee.lol/so_long_and_goodnight/YOUR_PASSKEY
---
# REQUIRED changes
- Update https://mainnet.infura.io/v3/API_KEY_HERE with your API key in blockchain_scanner.py
- Replace "YOUR_PASSKEY" with the actual passkey
- Use this URL to purge the DB.

---
# IP reporter
http://eyepee.lol/ip ~ **reports back simply your IP, nothing else**
- this was the original use of this domain
