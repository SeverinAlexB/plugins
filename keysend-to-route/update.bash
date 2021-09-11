#!/bin/bash

git pull
/home/bitcoin/lightning/cli/lightning-cli plugin stop /home/bitcoin/keysend-to-route/keysend-to-route/keysend_to_route.py
/home/bitcoin/lightning/cli/lightning-cli plugin start /home/bitcoin/keysend-to-route/keysend-to-route/keysend_to_route.py