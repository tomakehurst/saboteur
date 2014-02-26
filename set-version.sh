#!/usr/bin/env bash

if [[ -z $1 ]]; then
    echo "Usage $0 <new version>"
    exit 1
fi

newVersion=$1

find . -name "Makefile" -exec sed -i '' "s/VERSION = \(.*\)/VERSION = $newVersion/g" {} \;
