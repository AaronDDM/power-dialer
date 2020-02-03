#!/usr/bin/python3
from power_dialer import PowerDialer, Database

if __name__ == '__main__':
    powerDialer = PowerDialer(1)
    powerDialer.on_agent_login()