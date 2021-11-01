from brownie import accounts, network, config

LOCAL_BLOCKCHAIN_ENVS = ["development", "ganache-local", "mainnet-fork"]
FORKED_LOCAL_ENVS = []

def get_account(index=None, id=None):
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")

    if index:
        return accounts[index]
    if id: 
        return accounts.load(id)
    if (network.show_active() in LOCAL_BLOCKCHAIN_ENVS 
        or network.show_active() in FORKED_LOCAL_ENVS):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])