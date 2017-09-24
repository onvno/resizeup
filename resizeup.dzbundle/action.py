# Dropzone Action Info
# Name: resizeup
# Description: resize images & upload
# Handles: Files
# Creator: onvno
# URL: https://github.com/onvno
# Events: Clicked, Dragged
# KeyModifiers: Command, Option, Control, Shift
# SkipConfig: No
# RunsSandboxed: Yes
# Version: 1.0
# MinDropzoneVersion: 3.5
# OptionsNIB: ExtendedLogin


import time
import os
from qiniu import Auth, put_file, etag, urlsafe_base64_encode, BucketManager
import tinify
import hashlib
import sys

reload(sys)
sys.setdefaultencoding('utf8')
query = None

def getAuth():
    global query
    if query != None:
        return query
    access_key = os.environ['username']
    secret_key = os.environ['password']
    query = Auth(access_key, secret_key)
    return query


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def isFileExist(file_name):
    q = getAuth()
    # check if file already exist
    bucket_name = os.environ['server']
    bucket = BucketManager(getAuth())
    ret, info = bucket.stat(bucket_name, file_name)
    if ret != None:
        return True
    else:
        return False


def uploadFile(dest_path, file_name, backup):
    q = getAuth()
    bucket_name = os.environ['server']
    bucket_domain = os.environ['root_url']
    token = q.upload_token(bucket_name, file_name)
    ret, info = put_file(token, file_name, dest_path)

    if info.status_code == 200:
        # delete temp file
        if backup == False:
            os.unlink(dest_path)
        base_url = os.path.join(bucket_domain, file_name)
        return base_url
    else:
        return False


def copyFile(file_path,file_name):
    file = os.path.splitext(file_name)[0]
    suffix = os.path.splitext(file_name)[1]
    bucket_domain = os.environ['root_url']

    # File hash
    # Just for choosing the file did exist on qiniu or not
    md5string = md5(file_path)
    new_file = file + "." + md5string + suffix
    print("new_file:", new_file)
    if isFileExist(new_file):
        existed_url = os.path.join(bucket_domain, new_file)
        dz.percent(100)
        dz.url(existed_url)
        dz.fail("Filename existed & Ctrl + V to Use")
    
    # Zip & Copy
    dest_path = ""
    if not(suffix==".png" or suffix==".jpeg" or suffix==".jpg"):
        dz.fail("Compress File Format Error")

    backup = False
    if 'remote_path' in os.environ:
        backup = True
        dest_path = os.path.join(os.environ['remote_path'], new_file)
    else:
        dest_path = os.path.join(dz.temp_folder(), new_file)

    tinify.key = os.environ["port"]
    source = tinify.from_file(file_path)
    source.to_file(dest_path)

    # Upload
    return uploadFile(dest_path, new_file, backup)


def dragged():
    
    # Welcome to the Dropzone 3 API! It helps to know a little Python before playing in here.
    # If you haven't coded in Python before, there's an excellent introduction at http://www.codecademy.com/en/tracks/python

    # Each meta option at the top of this file is described in detail in the Dropzone API docs at https://github.com/aptonic/dropzone3-actions/blob/master/README.md#dropzone-3-api
    print(items)
    dz.begin("Starting some task...")

    # Below line switches the progress display to determinate mode so we can show progress
    dz.determinate(True)
    dz.percent(10)
    print("temp_folder:",dz.temp_folder())
    
    file_path = items[0]
    file_name = os.path.basename(file_path)
    base_url = copyFile(file_path,file_name)
    

    # The below line tells Dropzone to end with a notification center notification with the text "Task Complete"
    if base_url:
        dz.percent(100)
        dz.url(base_url)
        dz.finish("Upload Completed")
    else:
        dz.percent(100)
        dz.url(False)
        dz.fail("Upload Failed")

 
def clicked():
    # This method gets called when a user clicks on your action
    dz.finish("Not Support Click!")
    dz.url(False)
