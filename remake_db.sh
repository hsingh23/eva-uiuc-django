#!/bin/bash
mysql -u root -p
read -s -p "Password: " mypassword
stty echo mypassword