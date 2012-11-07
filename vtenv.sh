#!/bin/bash
# This script bootstraps a virtualenv
# environement for demos

# Starts
platform='unknown'
unamestr=`uname`
if [[ "$unamestr" == 'Linux' ]]; then
   platform='linux'
elif [[ "$unamestr" == 'Darwin' ]]; then
   platform='osx'
fi


if [ ! -f ./vtenv/bin/python ]
then
    if [ ! -f ./virtualenv.py ]
    then
        echo "Please get a copy of virtualenv.py"
        exit 1
    fi
    python virtualenv.py vtenv
fi
vtenv/bin/pip install -r requirements.txt --download-cache=eggs
if [ ! -d ./vtenv/src/ssh ];then
    vtenv/bin/pip install -e git://github.com/bitprophet/ssh.git#egg=ssh || echo "Please install python-dev and retry"
else
    cd vtenv/src/ssh
    git pull origin master
    cd ../../..
fi
if [ ! -f ./fab ];then
    echo " * Now you can type ./local_install.sh to init your *local* installation"
    ln -s vtenv/bin/fab fab
fi

if [[ $platform == 'osx' ]]; then
    echo "Installing gfortran, numpy, scipy and scikit-learn on osx"
    brew install gfortran
    vtenv/bin/pip install numpy
    vtenv/bin/pip install -e git+https://github.com/scipy/scipy.git#egg=scipy
    vtenv/bin/pip install scikit-learn
fi

echo " * Done"
exit
