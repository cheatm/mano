#! /bin/bash

source /etc/profile
mano notice daily -d `date -d "1 day ago" +\%Y-\%m-\%d`
