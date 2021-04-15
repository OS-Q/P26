#!/bin/bash

set -x
# Initialize any submodules.
git checkout gh
git submodule update --init --recursive

cp -rf ../boards .
cp -rf ../builder .
cp -rf ../extend .
cp -f ../link.json .
cp -f ../link.py .

git add .
git commit -am "update by github action"
git push origin gh

exit 0
