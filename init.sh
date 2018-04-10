#! /bin/bash

echo `python mano/export.py` > /etc/profile.d/env.sh

/usr/sbin/cron -f