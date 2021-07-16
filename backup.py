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
    lsDir = os.popen("docker exec {} ls -1 {}".format(CONTAINER_NAME, BK_DIR)).read();
    bkFiles = lsDir.splitlines();

    latestTimestamp = 0;
    fileName = None;

    for bkFile in bkFiles:
        if bkFile.endswith(".tar"):
            # get Unix timestamp portion of file name
            splitFileName = bkFile.split("_", 1);
            timestamp = int(splitFileName[0]);

            if timestamp > latestTimestamp:
                latestTimestamp = timestamp;
                fileName = bkFile;

    return fileName;


def copyBkToDropbox():
    fileName = getBkFileName();

    if fileName is None:
        print("No backup file found for current iso date string.");
        return;

    # extract the bk file from docker container first
    os.system("docker cp {}:{}/{} .".format(CONTAINER_NAME, BK_DIR, fileName));

    # TODO: Test that this copies to Dropbox home first, then modify.
    os.system("scp -rp {} {}@{}:~/".format(fileName, DROPBOX_USR_NAME, DROPBOX_IP_ADDR));


#createBk();
copyBkToDropbox();
