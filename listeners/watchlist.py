#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson
import argparse

WATCHLIST_FILE = 'watchlist.json'


class Watchlist(object):
    def __init__(self):
        """
        Constructor for the Watchlist class

        This method will automatically load the watchlist.json file, if none exists it will be created
        """
        self.watchlist = None
        # Load the json file
        try:
            with open(WATCHLIST_FILE, 'r') as input_file:
                try:
                    self.watchlist = simplejson.load(input_file)
                except Exception as ex:
                    raise Exception('%s does not contain a valid dictionary: %s' % (WATCHLIST_FILE, ex))
        except IOError:
            self.watchlist = {}
            self.save_file()

    def save_event(self, address, event,  command):
        """
        Save or update an event to the watchlist

        :param address: The bitcoin address to watch
        :param event: The type of event (SEND or RECEIVE)
        :param command: The command to execute
        """
        if address in self.watchlist:
            self.watchlist[address].update({event: command})
        else:
            self.watchlist[address] = {event: command}

        self.save_file()

    def delete_event(self, address, event):
        """
        Deletes an event from the watchlist

        :param address: The bitcoin address to watch
        :param event: The type of event (SEND or RECEIVE)
        """
        if address in self.watchlist:
            if event in self.watchlist[address]:
                del self.watchlist[address][event]
                self.save_file()

    def save_file(self):
        """
        Saves the watchlist to a json file
        """
        try:
            with open(WATCHLIST_FILE, 'w') as output_file:
                simplejson.dump(self.watchlist, output_file, indent=4, sort_keys=True)
        except Exception as ex:
            raise Exception('Failed to write data to %s: %s' % (WATCHLIST_FILE, ex))

    def show(self, address=None):
        """
        Show events for an address in the watchlist, if no address is given then events for all addresses are shown

        :param address: The bitcoin address to watch (optional)
        """
        if address is None:
            for address in self.watchlist:
                print(address)
                print(self.watchlist[address], '\n')
        elif address in self.watchlist:
            print(address)
            print(self.watchlist[address])
        else:
            print('No events found for address %s' % address)


if __name__ == "__main__":
    # Create main parser
    parser = argparse.ArgumentParser(description='Watchlist command line interface')
    subparsers = parser.add_subparsers(title='subcommands', metavar='', dest='subcommand')

    # Create parser for the add subcommand
    subparser = subparsers.add_parser(name='add',
                                      help='Add an event to the watchlist',
                                      formatter_class=argparse.RawDescriptionHelpFormatter,
                                      description='''
    Add an event to the watchlist. When the listener detects that a watched address receives or sends a transaction, the 
    corresponding command will be executed.
    These commands can include certain variables such as $address, $txid,
                                      ''',
                                      epilog='''
    examples:
      - watchlist.py add 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 SEND spellbook.py get_transactions $address
        -> add an event that will execute a spellbook.py command when address 1BAZ... sends a transaction
      - watchlist.py add 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 SEND spellbook.py get_transactions $address
        -> add an event that will execute a spellbook.py command when address 1BAZ... receives a transaction 
                                      ''')

    subparser.add_argument('address', help='The bitcoin address to watch')
    subparser.add_argument('event', help='The type of event to watch (SEND or RECEIVE)', choices=['SEND', 'RECEIVE'])
    subparser.add_argument('command', help='The command to execute', nargs='+')

    # Create parser for the delete subcommand
    subparser = subparsers.add_parser(name='delete',
                                      help='Delete an event from the watchlist',
                                      formatter_class=argparse.RawDescriptionHelpFormatter,
                                      description='''
    Delete an event from the watchlist
                                      ''',
                                      epilog='''
    examples:
      - watchlist.py delete 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 SEND
        -> delete the event when address 1BAZ... sends a transaction
      - watchlist.py delete 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8 RECEIVE
        -> delete the event when address 1BAZ... receives a transaction
                                      ''')

    subparser.add_argument('address', help='The bitcoin address to watch')
    subparser.add_argument('event', help='The type of event to watch (SEND or RECEIVE)', choices=['SEND', 'RECEIVE'])

    # Create parser for the show subcommand
    subparser = subparsers.add_parser(name='show',
                                      help='Show events in the watchlist',
                                      formatter_class=argparse.RawDescriptionHelpFormatter,
                                      description='''
    Show events in the watchlist
                                      ''',
                                      epilog='''
    examples:
      - watchlist.py show
        -> show all events for all addresses
      - watchlist.py show 1BAZ9hiAsMdSyw8CMeUoH4LeBnj7u6D7o8
        -> show all events for address 1BAZ...
                                      ''')

    subparser.add_argument('address', help='The bitcoin address to watch', nargs='?')

    # Parse the command line arguments
    args = parser.parse_args()

    if args.subcommand == 'add':
        Watchlist().save_event(args.address, args.event, ' '.join(args.command))
    elif args.subcommand == 'delete':
        Watchlist().delete_event(args.address, args.event)
    elif args.subcommand == 'show':
        Watchlist().show(args.address)
