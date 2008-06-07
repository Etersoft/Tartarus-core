#!/bin/bash

ICE_CONFIG=./config.client python megatest.py "$1"  --IceSSL.ServiceHost=`hostname`
