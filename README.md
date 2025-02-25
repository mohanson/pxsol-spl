# Pxsol spl

This repository provides a simple example of how to create an airdrop program for Solana SPL tokens. The program demonstrates how to distribute tokens from a specified source account to anyone who wants to receive the tokens.

- No permissions are required. Anyone who pays a handling fee can get a token of fixed value.
- Developed by [pxsol](https://github.com/mohanson/pxsol).

Deployed on the local test chain:

```sh
$ python make.py
```

If you want to deploy on the mainnet, please modify the private key in `res/info.json` and run

```sh
python make.py --net mainnet
```

# License

MIT.
