# Pxsol spl

This repository provides a simple example of how to create an airdrop program for Solana SPL tokens. The program demonstrates how to distribute tokens from a specified source account to anyone who wants to receive the tokens.

- No permissions are required. Anyone who pays a handling fee can get a token of fixed value.
- Developed by [pxsol](https://github.com/mohanson/pxsol).

Deployed on the local test chain:

```sh
$ python make.py deploy
# 2025/05/19 11:42:11 main: deploy mana pubkey="344HRAgWWiLuhUWTm9YNKWfhV5fWK26vx45vMxA9HyCE"
```

The command above did several things:

0. Create a new token mint with 9 decimal places.
0. Mint 1,000,000 tokens to the user (6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt).
0. Deploy the airdrop program.
0. User transfer 1,000,000 tokens to the airdrop program's associated token account.

Get airdrop:

```sh
# Generate a random user and then request an airdrop.
$ python make.py genuser
# 2025/05/19 11:45:11 main: random user prikey="Dk5y9WDhMiX83VDPTfojkWgXt6KuBAYhQEgVRAKYGLYG"

$ python make.py --prikey Dk5y9WDhMiX83VDPTfojkWgXt6KuBAYhQEgVRAKYGLYG airdrop
# 2025/05/19 11:45:24 main: request spl airdrop done recv=5.0
```

# Example of using spl-token command-line tool to operate SPL tokens

```sh
# Create a new spl token (program-2022 version)
$ spl-token create-token --program-2022

# Create a new spl token account for yourself
$ spl-token create-account 3EzV9KyLvuJBGFBEQyzghRLNwnHBj4udTp349iF7oEtx

# Mint some new spl tokens to your account
$ spl-token mint 3EzV9KyLvuJBGFBEQyzghRLNwnHBj4udTp349iF7oEtx 100

# Query spl token balance
$ spl-token balance 3EzV9KyLvuJBGFBEQyzghRLNwnHBj4udTp349iF7oEtx

# Transfer spl tokens to someone else
$ spl-token transfer 3EzV9KyLvuJBGFBEQyzghRLNwnHBj4udTp349iF7oEtx 0.5 $INTO_WALLET_ADDRESS --allow-unfunded-recipient --fund-recipient
```

# License

MIT.
