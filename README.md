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
2. `$ sudo apt update -y && sudo apt upgrade -y`
3. `$ do-release-upgrade -c`
4. Run the release upgrade command from 16 to 18, then again for 18 to 20.
5. Keep doing it until you can't.

## Install Docker & docker-compose
1. `$ sudo apt install docker.io -y`
2. `$ sudo apt install docker-compose -y`

## Install Git w/ LFS
`$ git clone https://github.com/sorc-lab/gitlab-lfs.git`

Add to ~/.bashrc:
`$ export GITLAB_HOME=/srv/gitlab`
`$ source ~/.bashrc`

To run the container:
`$ sudo docker-compose up -d && sudo docker-compose logs -f`

**NOTE**: First time sign-in asks for "root" user password.

As a security measure, configure the Sign-up restrictions. Do not allow users to create an
account. This can be done in the GitLab UI.
**TODO**: Add instructions for setting the sign-up restrictions.

**NOTE**: Git LFS is enabled by default.

### GitLab Server Tools
To shell into the container:
`$ sudo docker exec -it <container name> /bin/bash`

### GitLab client setup
Ideally, Git LFS needs to be setup for a fresh repo:
`$ git lfs install`

Once LFS is installed on the remote repo you need to add the LFS tracked file types to
.gitattributes file.

Once .gitattributes file is setup, you can track files, commit and push as normal.

Check what files in the repo are Git LFS tracked:
`$ git lfs ls-files`

In order for GitLab avatars to show up in the UI commit history, it is important to make sure the git user's email
matches the email in the UI for that user:
`$ git config user.name "FIRST_NAME LAST_NAME"`
`$ git config user.email "MY_NAME@example.com"`

Verify user/email config:
`$ cat .git/config`

You can also try this, but I am skeptical of the "--global" flag here:
`$ git config --global --list`

!!! WARNING !!!
Disabling SSL verification is bad, so don't do this. This can be done temporarily to setup and
learn GitLab server and LFS prior to setting up secure SSL connections:
`$ git config http.sslVerify false`

**NOTE**: This will be necessary if you've disabled lastpass in GitLab docker-compose.yml

## Backup GitLab Server
The following will be backed up following this guide:
- Database
- Attachments
- Git repositories data
- CI/CD job output logs
- CI/CD job artifacts
- LFS objects
- Container Registry images
- GitLab Pages content
- Snippets
- Group wikis

**NOTE**: LFS objects are covered in the backup command below.

Run the backup (container must be running):
`$ docker exec -t <container name> gitlab-backup create`

**NOTE**: The above command will create a backup .tar file in `/var/opt/gitlab/backups/<backupfile>.tar`

Manually back up the .rb config file and the secrets .json file (holds DB encryption keys):
`/etc/gitlab/gitlab-secrets.json`
`/etc/gitlab/gitlab.rb`

**NOTE**: These files are REQUIRED to later restore a GitLab server.

## (OPTIONAL) Copy Files to External Drive (USB)
**NOTE**: I used Windows 10 disk format tool to format the drive w/ NTFS filesystem

Before inserting the drive, on the Linux server, run:
`$ sudo fdisk -l`

Insert the drive and run the same command to help determine which drive is the USB, if it is not
already obvious. The USB drive usually is the last on the list, but better to be sure.

Create mount point:
`$ sudo mkdir /media/<mount_point_name>`

**NOTE**: No spaces allowed, but underscores are fine.

Mount USB device to mount point:
`$ sudo mount -t ntfs-3g /dev/sdc2 /media/<mount_point_name>`

Copy backup files to the `/media/<mount_point_name>`, then unmount the drive.
You can copy files from within the container to your host machine via:
`$ sudo docker cp <container_name>:/path/to/file.jpg .`

If you don't know the container name, run 'docker ps' command to get all running containers:
`$ sudo docker ps`

Unmount the mount point:
$ sudo umount /media/R610BK

Unmount the USB drive:
$ sudo umount /dev/sdc

Remove the drive.

## Restore GitLab Server from Backup
