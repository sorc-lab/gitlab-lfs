import os;
import fnmatch;
import sys;

from datetime import datetime;

DROPBOX_USR_NAME = sys.argv[1];
DROPBOX_IP_ADDR = sys.argv[2];

CONTAINER_NAME = "gitlab-lfs_web_1";
BK_DIR = "/var/opt/gitlab/backups";

def createBkFile():
    # creates a backup file in /var/opt/gitlab/backups/<backupfile>.tar within container
    os.system("docker exec -t {} gitlab-backup create".format(CONTAINER_NAME));

def findBkFileName():
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


def uploadBkFile(fileName):
    if fileName is None:
        print("No backup file found for current iso date string.");
        return;

    # extract the bk file from docker container first, then upload to Dropbox
    os.system("docker cp {}:{}/{} .".format(CONTAINER_NAME, BK_DIR, fileName));
    os.system("scp -rp {} {}@{}:~/".format(fileName, DROPBOX_USR_NAME, DROPBOX_IP_ADDR));


#createBkFile();

bkFile = findBkFileName();
uploadBkFile(bkFile);

# TODO:
#   [ ] Get the rest of the bk content, i.e. gitlab dir w/ certs and other stuff.
#   [ ] Pull the GitLab source code for CashSim and copy that to Dropbox:
#           Make config file to list repos to pull source code from. Right now
#           just take a single repo in as an argument.
#   [ ] Fix uploadBkFile so that it doesn't waste a step writing to Host OS
#           before cp'ing to Dropbox. Manually cleanup old files after.
#   [ ] Add console logging to show user what the script is processing.
#   [ ] Add an extra step to also copy .tar bk and gitlab dirs to USB external\
#           drive as an optional step if configuration flag is set.
