#!/bin/bash
sudo systemctl stop ssh
docker-compose down && docker-compose up -d

