This project deposits some ETH into Aave protocol, borrows some DAI, and repays the loan. 

It follows these high level steps:

1. Swap ETH for WETH
2. Deposit some ETH into Aave
3. Borrow some asset with the ETH collateral
4. Repay

To achieve the described purpose it uses tools such as

1. Brownie
  - Interfaces
  - Configs
  - Networks
  - Accounts 
2. ChainLink Interfaces
  - AggregatorV3
3. ERC20 Interface
4. Weth Interface
5. Aave Interfaces
  - Lending Pool
  - Lending Pool Addresses Provider
6. Can be tested both on a mainnet fork and on Kovan Chain
7. Python
