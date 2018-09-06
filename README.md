## Install base container

Clone the repo:

```
git clone https://github.com/delandtj/jsdock
cd jsdock
./buildit.sh
```

That will prepare you a docker image with jumpscale

## install jumpscale in base container

### start base container

```
YOURTREE=$HOME/dev/jumpy
docker run -d --net=host -v $YOURTREE:/opt --name js jumpy
```
So now your bokz iz running

### ssh 
```
ssh root@localhost -p 6322
cd ~
./installit.sh
```
this will install `jump* robo* digitalme*`
and add `js_*` to `/usr/local/bin`

when you stop that container, you'll need to reinstall with `./installit.sh`

otherwise, commit your container and use that as image.. all up to you



