# EYEPEE (IP) and EYEPEE ERC20 Scanner
---
http://eyepee.lol ~ **reports back with simply your IP with a php file.**

```
<?php echo $_SERVER['REMOTE_ADDR']; ?>
```

http://eyepee.lol/scanner ~ **This app is scanner that keeps track of newly created ERC20 tokens on the Ethereum blockchain.**

- It continuously checks for new blocks and scans the transactions within those blocks.
- When a contract creation transaction is detected, it retrieves: [contract_address, creator_address, token_name, total_supply]
- If the token name is available, it logs the details of the newly created ERC20 token.
- The script also generates an HTML report using a template, which includes the contract addresses, contract owner, block numbers, token names, and total supply.
