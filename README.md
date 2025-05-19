# Pxsol spl

This repository provides a simple example of how to create an airdrop program for Solana SPL tokens. The program demonstrates how to distribute tokens from a specified source account to anyone who wants to receive the tokens.

- No permissions are required. Anyone who pays a handling fee can get a token of fixed value.
- Developed by [pxsol](https://github.com/mohanson/pxsol).

Deployed on the local test chain:

```sh
$ python make.py deploy
# 2025/05/19 11:42:11 main: deploy mana pubkey="344HRAgWWiLuhUWTm9YNKWfhV5fWK26vx45vMxA9HyCE"
```

Get airdrop:

```sh
$ python make.py genuser
# 2025/05/19 11:45:11 main: random user prikey="Dk5y9WDhMiX83VDPTfojkWgXt6KuBAYhQEgVRAKYGLYG"

$ python make.py --prikey Dk5y9WDhMiX83VDPTfojkWgXt6KuBAYhQEgVRAKYGLYG airdrop
# 2025/05/19 11:45:24 main: request spl airdrop done recv=5.0
```

# License

MIT.
