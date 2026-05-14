#!/bin/bash
export $(cat .env | grep -v '^#' | xargs)
docker-compose up --build
