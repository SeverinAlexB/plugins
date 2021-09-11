#!/bin/bash

git pull
lcli plugin stop /home/bitcoin/keysend-to-route/keysend-to-route/keysend-to-route.py
lcli plugin start /home/bitcoin/keysend-to-route/keysend-to-route/keysend-to-route.py