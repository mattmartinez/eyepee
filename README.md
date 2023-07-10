# EYEPEE (IP) and EYEPEE ERC20 Scanner
---
http://eyepee.lol ~ **reports back with simply your IP with a php file.**

```
<?php echo $_SERVER['REMOTE_ADDR']; ?>
```

http://eyepee.lol/scanner ~ **This app is scanner that keeps track of newly created ERC20 tokens on the Ethereum blockchain.**

- It continuously checks for new blocks and scans the transactions within those blocks.
- When it detects a contract creation transaction, it retrieves the contract address and fetches the token name and total supply.
- If the token name is available, it logs the details of the newly created ERC20 token.
- The script renders the data using jinja2 into a table.
- Integrated with https://gopluseco.io for Token Info button, which displays the token's security score and other information.
- Auto-refresh every 60s.
