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
export MODULES="jumpscale_core jumpscale_lib jumpscale_prefab digital_me 0-robot"


# cloning source code Jumpscale stuff
for target in ${MODULES}; do
    git clone --depth=1 -b ${BRANCH} https://github.com/threefoldtech/${target}
done

# installing core and plugins
for target in ${MODULES}; do
    pushd ${target}
    pip3 install -e .
    popd
done
# before last pop, add 0-templates
git clone --depth=1 -b ${BRANCH} https://github.com/threefoldtech/0-templates

popd
#
# Add /opt/code/github/threefoldtech/jumpscale_core/cmds to path
echo "export PATH=\$PATH:/opt/code/github/threefoldtech/jumpscale_core/cmds" >> /root/.profile

# ensure jumpscale is well configured
js_shell 'print(j.core.dirs)'

