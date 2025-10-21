#!/bin/bash

export FT_CLIENT_ID=$(grep FT_CLIENT_ID .env | cut -d '=' -f2 | tr -d '\r')
export FT_CLIENT_SECRET=$(grep FT_CLIENT_SECRET .env | cut -d '=' -f2 | tr -d '\r')

python3 -m flask --app main/connect.py run --debug
