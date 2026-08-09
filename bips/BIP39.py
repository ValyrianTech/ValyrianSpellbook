"""BIP39 mnemonic seed phrase generation and validation."""

from .mnemonic import Mnemonic


def get_seed(mnemonic, passphrase, language='english'):
    """Generate a seed from a BIP39 mnemonic and passphrase."""
    return Mnemonic(language=language).to_seed(mnemonic=mnemonic, passphrase=passphrase)


