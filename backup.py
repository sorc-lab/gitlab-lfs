import os;
import fnmatch;
import sys;

from datetime import datetime;

# NOTE: Script should only be run once per day. Logic is based on current date,
#       so it will find multiple backup files if run twice in the same day and
#       will only save off the first one it finds.

DROPBOX_USR_NAME = sys.argv[1];
DROPBOX_IP_ADDR = sys.argv[2];

CONTAINER_NAME = "gitlab-lfs_web_1";
BK_DIR = "/var/opt/gitlab/backups";

def createBk():
    # creates a backup file in /var/opt/gitlab/backups/<backupfile>.tar within container
    os.system("docker exec -t {} gitlab-backup create".format(CONTAINER_NAME));

def getBkFileName():
    # grabs everything before the 'T', e.g.: 2021-07-14T19:20:36.086270
    splitDateStr = datetime.now().isoformat().split("T", 1);
    isoDateStr = splitDateStr[0].replace("-", "_");

    # TODO: This fails because BK_DIR is pointed to host machine path, not container
    # find first backup file in dir that contains today's date
    # for file in os.listdir(BK_DIR):
    #     if fnmatch.fnmatch(file, "*{}*".format(isoDateStr)):
    #         return file;

    # TODO: Try: `docker exec --privileged $NEW_CONTAINER_ID ls -1 /var/log`
    lsDir = os.system("docker exec {} ls -1 {}".format(CONTAINER_NAME, BK_DIR));
    print("--- lsDir ----------------------------------------------------------");
    print(lsDir);
    print("--------------------------------------------------------------------");

def copyBkToDropbox():
    bkFileName = getBkFileName();

    if bkFileName is None:
        print("No backup file found for current iso date string.");
        return;

    # extract the bk file from docker container first
    os.system("docker cp {}:{}/{} .".format(CONTAINER_NAME, BK_DIR, bkFileName));

    # TODO: Test that this copies to Dropbox home first, then modify.
    os.system("scp -rp {}@{}:~/".format(DROPBOX_USR_NAME, DROPBOX_IP_ADDR));


createBk();
#copyBkToDropbox();

# TODO: REMOVE AFTER TESTING. copyBkToDropbox will call this method internally.
getBkFileName();

# *** STACK TRACE FROM FIRST TEST RUN ***
# Backup task is done.
# Traceback (most recent call last):
#   File "backup.py", line 45, in <module>
#     copyBkToDropbox();
#   File "backup.py", line 31, in copyBkToDropbox
#     bkFileName = getBkFileName();
#   File "backup.py", line 26, in getBkFileName
#     for file in os.listdir(BK_DIR):
# FileNotFoundError: [Errno 2] No such file or directory: '/var/opt/gitlab/backups'
