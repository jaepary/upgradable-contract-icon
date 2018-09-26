# Upgradable Smart Contract for ICON

These are example codes of upgradable smart contracts based on [ICON platform](https://www.icondev.io/index.do). 

## Notice

These example codes didn't get a SCORE audit yet. I just hope someone to get help for his or her practical smart contracts from these.

## Module view
![Module view](https://github.com/upgradable-contract-icon/raw/master/images/module_view.png)

## Requirements

- Python
    - Version: python 3.6.x

- T-Bears
    - Version: tbears 1.0.5.1+

- ICON SDK for Python
    - Version: iconsdk 1.0.4+

## Version

0.1.0

## Setup

### Setup on MacOS

```bash
# install develop tools
$ brew install leveldb
$ brew install autoconf automake libtool pkg-config

# install RabbitMQ and start service
$ brew install rabbitmq
$ brew services start rabbitmq

# go to the root directory of upgradable-contract-icon
$ cd upgradable-contract-icon

# setup the python virtualenv development environment
$ pip3 install virtualenv
$ virtualenv -p python3 .
$ source bin/activate

# Install the example smart contracts
(upgradable-contract-icon) $ pip install -r requirements.txt
```

### Setup on Linux

```bash
# Install levelDB
$ sudo apt-get install libleveldb1 libleveldb-dev
# Install libSecp256k
$ sudo apt-get install libsecp256k1-dev

# install RabbitMQ and start service
$ sudo apt-get install rabbitmq-server

# go to the root directory of upgradable-contract-icon
$ cd upgradable-contract-icon

# Setup the python virtualenv development environment
$ virtualenv -p python3 .
$ source bin/activate

# Install the example smart contracts
(upgradable-contract-icon) $ pip install -r requirements.txt
```

## Test

```bash
# It takes more than 5 minutes
(upgradable-contract-icon) $ ./test.sh
```
