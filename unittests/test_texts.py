"""Tests for the texts.py module — CLI help/description string constants.

Since texts.py contains only module-level string constants (no functions or
classes), coverage is achieved by importing the module and verifying that
key constants exist and are non-empty strings.
"""

import texts


def test_all_constants_are_strings():
    """Every public constant in texts.py should be a non-empty string."""
    const_names = [
        name for name in dir(texts)
        if name.isupper() and not name.startswith('_')
    ]
    assert len(const_names) > 0
    for name in const_names:
        value = getattr(texts, name)
        assert isinstance(value, str), f"{name} is not a string"
        assert len(value) > 0, f"{name} is empty"


def test_explorer_constants():
    assert "explorer" in texts.GET_EXPLORERS_DESCRIPTION.lower()
    assert "spellbook.py get_explorers" in texts.GET_EXPLORERS_EPILOG
    assert "Save or update" in texts.SAVE_EXPLORER_DESCRIPTION
    assert "blockchain.info" in texts.SAVE_EXPLORER_EPILOG
    assert "Get configuration" in texts.GET_EXPLORER_CONFIG_DESCRIPTION
    assert "Delete" in texts.DELETE_EXPLORER_DESCRIPTION


def test_block_and_tx_constants():
    assert "latest block" in texts.GET_LATEST_BLOCK_DESCRIPTION.lower()
    assert "488470" in texts.GET_BLOCK_EPILOG
    assert "Get a transaction" in texts.GET_TRANSACTION_DESCRIPTION
    assert "transactions" in texts.GET_TRANSACTIONS_DESCRIPTION.lower()


def test_balance_and_utxo_constants():
    assert "balance" in texts.GET_BALANCE_DESCRIPTION.lower()
    assert "UTXO" in texts.GET_UTXOS_DESCRIPTION
    assert "confirmations" in texts.GET_UTXOS_EPILOG


def test_sil_sul_profile_constants():
    assert "Simplified Inputs List" in texts.GET_SIL_DESCRIPTION
    assert "Simplified UTXO List" in texts.GET_SUL_DESCRIPTION
    assert "profile" in texts.GET_PROFILE_DESCRIPTION.lower()


def test_linked_list_constants():
    assert "Linked Address List" in texts.GET_LAL_DESCRIPTION
    assert "Linked Balance List" in texts.GET_LBL_DESCRIPTION
    assert "Linked Received List" in texts.GET_LRL_DESCRIPTION
    assert "Linked Sent List" in texts.GET_LSL_DESCRIPTION


def test_random_address_constants():
    assert "random address" in texts.GET_RANDOM_ADDRESS_DESCRIPTION.lower()
    assert "SIL" in texts.GET_RANDOM_ADDRESS_EPILOG
    assert "LBL" in texts.GET_RANDOM_ADDRESS_EPILOG


def test_trigger_constants():
    assert "triggers" in texts.GET_TRIGGERS_DESCRIPTION.lower()
    assert "Save or update" in texts.SAVE_TRIGGER_DESCRIPTION
    assert "Delete" in texts.DELETE_TRIGGER_DESCRIPTION
    assert "Activate" in texts.ACTIVATE_TRIGGER_DESCRIPTION
    assert "signed message" in texts.SEND_SIGNED_MESSAGE_DESCRIPTION.lower()
    assert "Sign a message" in texts.SIGN_MESSAGE_DESCRIPTION
    assert "Check triggers" in texts.CHECK_TRIGGERS_DESCRIPTION


def test_action_constants():
    assert "action" in texts.GET_ACTIONS_DESCRIPTION.lower()
    assert "Save or update" in texts.SAVE_ACTION_DESCRIPTION
    assert "Delete" in texts.DELETE_ACTION_DESCRIPTION
    assert "Run" in texts.RUN_ACTION_DESCRIPTION
    assert "reveal" in texts.GET_REVEAL_DESCRIPTION.lower()


def test_log_constants():
    assert "log" in texts.GET_LOGS_DESCRIPTION.lower()
    assert "ERROR" in texts.GET_LOGS_EPILOG


def test_llm_constants():
    assert "LLM" in texts.GET_LLMS_DESCRIPTION
    assert "get_llms" in texts.GET_LLMS_EPILOG
    assert "configuration" in texts.GET_LLM_CONFIG_DESCRIPTION.lower()
    assert "Save or update" in texts.SAVE_LLM_CONFIG_DESCRIPTION
    assert "Delete" in texts.DELETE_LLM_DESCRIPTION
    assert "delete_llm" in texts.DELETE_LLM_EPILOG
