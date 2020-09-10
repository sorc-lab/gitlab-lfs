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
