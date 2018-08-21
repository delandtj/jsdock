#!/bin/bash
set -e

# setting up locales
if ! grep -q ^en_US /etc/locale.gen; then
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
    locale-gen
fi


# this hack enable jumpscale to use /opt/ by default
touch /root/.iscontainer

# settigng up directories layout
mkdir -p /host
mkdir -p /opt/code/github/threefoldtech
mkdir -p /root/.ssh
pushd /opt/code/github/threefoldtech


# settings
export BRANCH="development"

# cloning source code Jumpscale stuff
for target in core lib; do
    git clone --depth=1 -b ${BRANCH} https://github.com/threefoldtech/jumpscale_${target}
done

# installing core and plugins
for target in jumpscale_core jumpscale_lib; do
    pushd ${target}
    pip3 install -e .
    popd
done

popd

# zrobot
pushd /opt/code/github/threefoldtech
./utils/zrobot_install.sh

# ensure jumpscale is well configured
js_shell 'print(j.core.dirs)'
