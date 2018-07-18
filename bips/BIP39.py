from mnemonic import Mnemonic


def get_seed(mnemonic, passphrase, language='english'):
    return Mnemonic(language=language).to_seed(mnemonic=mnemonic, passphrase=passphrase)


