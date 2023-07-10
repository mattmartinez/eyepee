import requests

def getContractScan(network, address) -> dict:
    if network is None:
        network = 1

    url = "https://api.gopluslabs.io/api/v1/token_security/{}?contract_addresses={}".format(
        network, address)
    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code != 200:
        raise Exception("Error: " + response.text)
    return response.json()["result"]


def extractSafeyVector(address, contractResult):
    firstItem = contractResult[address.lower()]
    return {
        "is_blacklisted":
        bool(int(firstItem.get("is_blacklisted", False))),
        "is_honeypot":
        bool(int(firstItem.get("is_honeypot", False))),
        "is_in_dex":
        bool(int(firstItem.get("is_in_dex", False))),
        "is_open_source":
        bool(int(firstItem.get("is_open_source", False))),
        "can_take_back_ownership":
        bool(int(firstItem.get("can_take_back_ownership", False))),
        "is_proxy":
        bool(int(firstItem.get("is_proxy", False))),
        "buy_tax":
        firstItem.get("buy_tax", "None"),
        "sell_tax":
        firstItem.get("sell_tax", "None"),
        "token_name":
        firstItem.get("token_name", "Unknown"),
        "lp_holder_count":
        firstItem.get("lp_holder_count", "Unknown"),
    }