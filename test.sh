#!/bin/bash

tbears stop
sleep 1
tbears clear
rm -f tbears.log
rm -rf exc
sleep 1
tbears start
sleep 1
tbears genconf
sleep 1
rm -f keystore_test1
python -m unittest
