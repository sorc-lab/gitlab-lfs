# gitlab-lfs
GitLab Docker container to be used for large repositories needing Git LFS and possibly project management.

# Setup
## Add to .bashrc
```
# The GitLab container uses host mounted volumes to store persistent data:
# .---------------------------------------------------------------------------------------------.
# | Local location	    | Container location	| Usage                                         |
# |---------------------|-----------------------|-----------------------------------------------|
# | $GITLAB_HOME/data	| /var/opt/gitlab	    | For storing application data                  |
# | $GITLAB_HOME/logs	| /var/log/gitlab	    | For storing logs                              |
# | $GITLAB_HOME/config	| /etc/gitlab	        | For storing the GitLab configuration files    |
# '---------------------------------------------------------------------------------------------'
export GITLAB_HOME=/srv/gitlab
```

## Links
Official GitLab Docker install instuctions: https://docs.gitlab.com/omnibus/docker/

## Install Ubuntu
1. Boot w/ install disk (Ubuntu 16.x)
2. `$ $ do-release-upgrade -c`
3. Run the release upgrade command from 16 to 18, then again for 18 to 20.

## Install Docker & docker-compose
1. `$ sudo apt install docker.io`
2. `$ sudo apt install docker-compose`

## Install Git w/ LFS
`$ git clone https://github.com/sorc-lab/gitlab-lfs.git`
`$ export GITLAB_HOME=/srv/gitlab`

To run the container:
`$ sudo docker-compose up -d && sudo docker-compose logs -f`

**NOTE**: First time sign-in asks for "root" user password.

As a security measrure, configure the Sign-up restrictions. Do not allow users to create an
account. This can be done in the GitLab UI.
**TODO**: Add instructions for setting the sign-up restrictions.

**NOTE**: Git LFS is enabled by default.

### GitLab Server Tools
To shell into the container:
`$ sudo docker exec -it <container name> /bin/bash`




