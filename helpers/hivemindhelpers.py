#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from helpers.jsonhelpers import load_from_json_file, save_to_json_file

HIVEMINDS_DIR = 'json/public/hiveminds'
HIVEMINDS_FILE = os.path.join(HIVEMINDS_DIR, 'hiveminds.json')

# create the hiveminds directory if necessary
if not os.path.isdir(HIVEMINDS_DIR):
    os.makedirs(HIVEMINDS_DIR)

# if hiveminds file doesn't exist create an empty one
if not os.path.isfile(HIVEMINDS_FILE):
    save_to_json_file(filename=HIVEMINDS_FILE, data={})


def get_hivemind_state_hash(hivemind_id):
    if ':' in hivemind_id:
        hivemind_id = hivemind_id.split(':')[0]

    hiveminds = load_from_json_file(filename=HIVEMINDS_FILE)

    if hivemind_id in hiveminds:
        return hiveminds[hivemind_id]


def update_hivemind_state_hash(hivemind_id, last_state_hash):
    if ':' in hivemind_id:
        hivemind_id = hivemind_id.split(':')[0]

    hiveminds = load_from_json_file(HIVEMINDS_FILE)

    hiveminds[hivemind_id] = last_state_hash

    save_to_json_file(filename=HIVEMINDS_FILE, data=hiveminds)
