#!/bin/bash
echo "drop database eva_uiuc; create database eva_uiuc;" | python manage.py dbshell && python manage.py syncdb