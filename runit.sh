#!/bin/bash

MYDIR=${HOME}/ThreeFold/

docker run -d --name js --net=host \
	-v ${MYDIR}:/opt/code \
	jumpy
