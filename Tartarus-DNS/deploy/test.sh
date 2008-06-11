#!/bin/bash

python ./deploy.py --Ice.Config=../test/config.client --IceSSL.ServiceHost=`hostname`  "$@"

