#!/bin/bash

cfg=$1

news-please -c "$cfg" -reset-elasticsearch
news-please -c "$cfg"