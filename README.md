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

**!!! WARNING !!!**
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
`$ sudo umount /media/<mount_point_name>`

Unmount the USB drive:
`$ sudo umount /dev/sdc`

Remove the drive.

## Restore GitLab Server from Backup
The following must be true for a restore to work:
- You have installed the exact same version and type (CE/EE) of GitLab Omnibus with which the
  backup was created.
- You have run sudo gitlab-ctl reconfigure at least once.
- GitLab is running. If not, start it using sudo gitlab-ctl start (I've been using docker-compose)

First ensure your backup tar file is in the backup directory described in the gitlab.rb
configuration `gitlab_rails['backup_path']`.
The default is /var/opt/gitlab/backups. It needs to be owned by the git user.

**NOTE**: The commands below will be run from inside the container or via docker.

**(OPTIONAL)**: If you used a USB drive connected to host machine, you'll need to copy them into
the container:
`$ sudo docker cp [OPTIONS] SRC_PATH CONTAINER:DEST_PATH`

**NOTE**: The above 'cp' command is just a reverse of the command we used previously to copy files.

Example commands for copying and setting permissions/ownership (your filename will be different):
`$ sudo cp 11493107454_2018_04_25_10.6.4-ce_gitlab_backup.tar /var/opt/gitlab/backups/`
`$ sudo chown git.git /var/opt/gitlab/backups/11493107454_2018_04_25_10.6.4-ce_gitlab_backup.tar`

**NOTE**: The commands in the next step are all run from inside the container and do not need
'sudo', since you'll be 'root' user.

**NOTE**: Make sure docker-compose file is pulling the correct image tag/version that matches the
backup file's image/tag version.

Stop the processes that are connected to the database. Leave the rest of GitLab running:
`$ gitlab-ctl stop unicorn`
`$ gitlab-ctl stop puma`
`$ gitlab-ctl stop sidekiq`

Verify the above processes are 'down':
`$ gitlab-ctl status`

**NOTE**: I did not see unicorn on the list, but puma and sidekiq were 'down'.

**!!! WARNING !!!** This next command will overwrite data.
Restore from backup by specifying the timestamp on the file (your filename will be different):
`$ gitlab-backup restore BACKUP=11493107454_2018_04_25_10.6.4-ce`

Exit out of the container and `docker cp` the .rb config file and .json secrets file to
`/etc/gitlab/`

**NOTE**: The .rb config and .json secrets files need to be owned by 'root'.

After restoring the config and secrets file, run the following inside the container:
`$ gitlab-ctl reconfigure`
`$ gitlab-ctl restart`
`$ gitlab-rake gitlab:check SANITIZE=true`
`$ gitlab-rake gitlab:doctor:secrets`

---

**TODO**: Seems like everything looks healthy and the restore is working, but I cannot access to UI
w/ error saying "Connection refused". Also, gitlab-ctl status shows 'nginx' is down. Running
`gitlab-ctl nginx start` does not fix this.
This is because nginx cannot find /etc/gitlab/ssl/gitlab.example.com.crt cert file.
**THIS NEEDS TO BE ADDED TO THE BACKUP PROCEDURE**. How to generate a new one?

Couple things to note, the filenames need to be gitlab.crt and gitlab.key. Also play with making
the gitlab container's ssh port 522, so that the host machine's port 22 doesn't conflict. Use this
as an example for how to setup nginx config values:

**TODO**: DON'T THINK ANY OF THIS IS NEEDED, BUT MAKE SURE.

  version: '2'
  services:
    gitlab:
      image: gitlab/gitlab-ce:latest
      restart: unless-stopped
      hostname: 'gitlab.<company>.com'
      environment:
        GITLAB_OMNIBUS_CONFIG: |
          external_url 'https://gitlab.<company>.com'
          gitlab_rails['gitlab_shell_ssh_port'] = 522
          nginx['redirect_http_to_https'] = true
          nginx['ssl_certificate'] = '/etc/gitlab/ssl/gitlab.crt'
          nginx['ssl_certificate_key'] = '/etc/gitlab/ssl/gitlab.key'
      ports:
        - '80:80'
        - '443:443'
        - '522:22'
      volumes:
        - './config/gitlab:/etc/gitlab'
        - './logs:/var/log/gitlab'
        - './data:/var/opt/gitlab'


Will need to figure out how to generate .crt and key files in the short term until I can get this
done the right way w/ a valid 3rd party cert provider and turn on letsencrypt SSL verification. May
still be able to do self-signed.

This link details how to create a self-signed cert: Using Ubuntu OpenSSL:
https://futurestud.io/tutorials/how-to-run-gitlab-with-self-signed-ssl-certificate

Also, take this time to reconfigure the host name to be https://gitlab.sorclab.com

Shell into container and mkdir /etc/gitlab/ssl

**NOTE**: All SLL related files need to match "<hostname>.*", i.e. "gitlab.example.com.crt" etc.

Create a 2048 bit private key
If the ssl directory doesn't exist, please create it first
`$ openssl genrsa -out "/etc/nginx/ssl/gitlab.example.com.key" 2048`

This command generates the certificate signing request
`$ sudo openssl req -new -key "/etc/nginx/ssl/gitlab.key" -out "/etc/nginx/ssl/gitlab.example.com.csr"`

Country Name (2 letter code) [AU]:DE
State or Province Name (full name) [Some-State]:Saxony-Anhalt  
Locality Name (eg, city) []:Magdeburg  
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Future Studio  
Organizational Unit Name (eg, section) []:  
Common Name (e.g. server FQDN or YOUR name) []:gitlab.yourdomain.com  
Email Address []:

Please enter the following 'extra' attributes  
to be sent with your certificate request  
A challenge password []:  
An optional company name []:  

**NOTE**: The FQDN part is really important, but "gitlab.example.com" or whatever you set your
domain name.

Finally, generate the cert:
`$ openssl x509 -req -days 365 -in "/etc/gitlab/ssl/gitlab.example.com.csr" -signkey "/etc/gitlab/ssl/gitlab.example.com.key" -out "/etc/gitlab/ssl/gitlab.example.com.crt"`

Run `$ gitlab-ctl restart` and nginx should now spin up without errors.

---

## Next Steps
**TODO: FIGURE OUT CLEAN UP OPERATIONS OF LFS DATA AND GENERAL MAINTENANCE PROCEDURES:
https://docs.gitlab.com/ee/raketasks/cleanup.html**
**TODO: CONSIDER CRON JOBS AND AUTOMATION FOR BKS AND MAINTENANCE SCRIPTS**
**TODO: CONSIDER STORING THE SECRETS FILE SEPARATELY FROM THE BACKUPS**
