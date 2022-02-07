#!/bin/bash

# install libssl
echo "Installing OpenSSL ..."
apt-get install libssl-dev

# install GMP
echo "Installing GMP ..."
apt-get install libgmp-dev

# install PBC and required libraries (flex + bison)
echo "Installing PBC and required libraries (flex + bison) ..."
apt-get install flex bison
wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz
tar -xzf pbc-0.5.14.tar.gz
cd pbc-0.5.14
./configure
make
sudo make install

# install GNU MPFR
echo "Installing GNU MPFR ..."
apt-get install libmpfr-dev

# install needed python 3 libraries
echo "Installing needed Python 3 libraries ..."
apt-get install python3-dev python3-setuptools python3-numpy