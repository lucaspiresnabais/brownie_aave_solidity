from scripts.helpers import get_account
from scripts.get_weth import get_weth
from brownie import config, network, interface
from web3 import Web3

amount = Web3.toWei(0.001, "ether")

def main():
    account = get_account()
    
    # Get weth addres and use it to get_weth() into the account
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["kovan", "mainnet-fork"]:
        get_weth()
    
    # Get the lending pool contract 
    lending_pool = get_lending_pool()

    # Approve the weth spending and deposit
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    print("Depositing...")
    tx = lending_pool.deposit(erc20_address, amount, account.address, 0, {"from": account})
    tx.wait(1)
    print("Deposited!")

    # Get information about borrowable amounts
    (available_borrow_eth, total_debt_eth) = get_borrowable_data(lending_pool, account)

    # Get dai price based on ETH 
    dai_eth_price = get_asset_price(config["networks"][network.show_active()]["dai_eth_price_feed"])
    
    # Use the above to calculate how much dai I can actually borrow
    amount_dai_to_borrow = (1 / dai_eth_price) * (available_borrow_eth * 0.95)
    print(f"You can borrow {amount_dai_to_borrow} DAI")
    
    # Get DAI address and use lending pool to borrow
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address, 
        Web3.toWei(amount_dai_to_borrow, 'ether'),
        1,
        0,
        account.address,
        {"from": account} 
    )
    borrow_tx.wait(1)
    print("Dai borrowed!")

    # Get information about borrowable amounts, this should've change
    # since we already borrowed DAI
    get_borrowable_data(lending_pool, account)

    # Repay
    repay_all(amount, lending_pool, account)
    print("Deposited, borrowed and repayed!")

def repay_all(amount, lending_pool, account):
    dai_address = config["networks"][network.show_active()]["dai_token"]
    approve_erc20(
        Web3.toWei(amount, 'ether'), 
        lending_pool, 
        dai_address,
        account
    )
    repay_tx = lending_pool.repay(dai_address, amount, 1, account, {"from": account})
    repay_tx.wait(1)
    print("Repaid!")

def get_asset_price(price_feed_address):
    dai_eth_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = dai_eth_price_feed.latestRoundData()[1]
    converted_latest_price = Web3.fromWei(latest_price, "ether")
    print(f"The DAI/ETH price is {converted_latest_price}")
    return float(converted_latest_price)
    
def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth, 
        total_debt_eth, 
        available_borrow_eth, 
        current_liquidation_threshold,
        ltv,
        health_factor        
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    
    print(f"Collateral: {total_collateral_eth}")
    print(f"Debt: {total_debt_eth}")
    print(f"Available for borrowing: {available_borrow_eth}")

    return(float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    print("Approving an ERC20")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("Approved!")
    return tx

    
def get_lending_pool():
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    lending_pool = interface.ILendingPool(lending_pool_address)
    
    return lending_pool