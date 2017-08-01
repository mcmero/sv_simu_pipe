#!/bin/sh

base_path=$1
mem=$2
shift

java -Xmx${mem}g -jar ${base_path}snvindelsim.jar $*
