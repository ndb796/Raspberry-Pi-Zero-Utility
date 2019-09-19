import os
import time
import hashlib
import string
import random


def mount(path):
    os.system("sudo mount " + path)
    time.sleep(1)


def umount(path):
    os.system("sudo umount " + path)
    time.sleep(1)


def activate(image, read_only):
    os.system("sudo modprobe g_mass_storage file=" + image + " stall=0 ro=" + read_only + " removable=1")
    time.sleep(1)


def deactivate():
    os.system("sudo modprobe g_mass_storage -r")
    time.sleep(1)


def random_string(string_length=20):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_length))


deactivate()
mount("/mnt/usb_share")

f = open("/mnt/usb_share/nonce.txt", "w")
f.write(random_string())
f.close()
time.sleep(2)

umount("/mnt/usb_share")
umount("/mnt/usb_share2")
activate("usbdisk.img", "n")
start_time = os.path.getctime('usbdisk.img')

while True:
    now_time = os.path.getctime("usbdisk.img")
    if start_time != now_time:
        print('Modification Detected')
        time.sleep(1)
        mount("/mnt/usb_share")
        mount("/mnt/usb_share2")
        deactivate()
        if os.path.isfile('/mnt/usb_share/hash.txt'):
            nonce_file = open("/mnt/usb_share/nonce.txt", "r")
            nonce_string = nonce_file.readline().strip()
            print('Nonce Value:', nonce_string)
            nonce_file.close()
            hash_file = open("/mnt/usb_share/hash.txt", "r")
            hash_string = hash_file.readline().strip()
            print('User Hash:', hash_string)
            hash_file.close()
            binary_file = open("core_binary", "rb")
            valid_hash = hashlib.sha256(binary_file.read() + nonce_string.encode()).hexdigest()
            print("Valid Hash:", valid_hash)
            binary_file.close()
            f = open("/mnt/usb_share/nonce.txt", "w")
            f.write(random_string())
            f.close()
            time.sleep(2)
            if hash_string == valid_hash:
                print('Authorized! Here is core binary.')
                os.system("cp core_binary /mnt/usb_share2/core_binary")
                if os.path.isfile("/mnt/usb_share2/pure_binary"):
                    os.remove("/mnt/usb_share2/pure_binary")
                umount("/mnt/usb_share")
                umount("/mnt/usb_share2")
                activate("usbdisk2.img", "y")
            else:
                print('Not Authorized! Here is pure binary.')
                os.system("cp pure_binary /mnt/usb_share2/pure_binary")
                if os.path.isfile("/mnt/usb_share2/core_binary"):
                    os.remove("/mnt/usb_share2/core_binary")
                umount("/mnt/usb_share")
                umount("/mnt/usb_share2")
                activate("usbdisk2.img", "y")
        else:
            umount("/mnt/usb_share")
            umount("/mnt/usb_share2")
            activate("usbdisk.img", "n")
        time.sleep(1)
        start_time = os.path.getctime("usbdisk.img") # Because Pi also writes the file.
