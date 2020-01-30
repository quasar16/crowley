#!/bin/bash

cfg=$1

newsplease -c "$cfg" -reset-elasticsearch
newsplease -c "$cfg"