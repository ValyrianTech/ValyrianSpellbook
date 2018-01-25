#!/usr/bin/env python
# -*- coding: utf-8 -*-


class TransactionType(object):
    SEND2SINGLE = 'Send2Single'  # A transaction sent to a single address (might still include a change address and/or a spellbook fee)
    SEND2MANY = 'Send2Many'  # A transaction with many outputs where the amount is distributed based on a custom distribution

    SEND2SIL = 'Send2SIL'  # A transaction with many outputs where the amount is distributed based on a SIL
    SEND2LBL = 'Send2LBL'  # A transaction with many outputs where the amount is distributed based on a LBL
    SEND2LRL = 'Send2LRL'  # A transaction with many outputs where the amount is distributed based on a LRL
    SEND2LSL = 'Send2LSL'  # A transaction with many outputs where the amount is distributed based on a LSL

    SEND2LAL = 'Send2LAL'  # A transaction with many outputs where each utxo is sent to the corresponding address in the LAL

