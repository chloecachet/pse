#!/bin/bash

# check if submodules have been pulled correctly, if not, pull them
if test ! -f "fhipe/Makefile"; then
  git submodule update --init --recursive
fi
# checkout dev branch in charm submodule
cd fhipe/charm
git checkout -f dev
# build fhipe matrix generation program
cd ..
sudo make install
cd ..