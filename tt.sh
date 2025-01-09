#!/bin/bash


docker stop $(docker ps -q)


docker rm $(docker ps -a -q)


docker rmi $(docker images -q)

docker volume prune -f

docker network prune -f


