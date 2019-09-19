## Raspberry Pi Zero Utility

### 기본 내용 정리

* USB Gadget Mode: Makes a Linux system look like a USB device to a host computer. It can provide many USB devices: a serial connection, ethernet over USB, keyboard emulation, etc.

USB 가젯 모드란, 리눅스 시스템을 호스트 컴퓨터의 입장에서 보았을 때 USB Device인 것처럼 보이게 하는 방법을 의미한다. 말 그대로 시리얼 통신을 하거나, USB를 이더넷 네트워크로 사용하거나, 키보드로 사용하거나 등 다양한 USB 기기의 기능들을 지원할 수 있다.

* mount: Mounts a storage device or filesystem, making it accessible and attaching it to an existing directory structure.

마운트란, 특정한 저장 장치나 파일 시스템을 인식하여 시용자가 접근할 수 있도록 하는 것을 의미한다.

* /etc/fstab: Lists all available disk partitions and other types of file systems and data sources (for mounting).

/etc/fstab: 리눅스에서 사용하는 디스크 파티션, 파일 시스템 등의 정보들을 정적으로 저장하고 있는 파일로, 마운트 정보를 가지고 있다.

* fstab 필드 설명

  1) File System Device(파일 시스템 장치): 사용할 파티션의 경로
  2) Mount Point(마운트 포인트): 파일 시스템을 연결할 디렉토리 경로
  3) File System Type(파일 시스템 종류): 파티션 생성시 설정했던 파일 시스템의 종류 (ext3, ext4, ...)
  4) Mount Option(마운트 옵션): (rw - 읽기/쓰기, nouser - 일반 사용자 마운트 불가능, auto - 부팅시 자동 마운트, exec - 파일 실행 허용)
  5) Dump(덤프): 백업 가능 여부 (0 - 덤프 불가능, 1 - 덤프 가능)
  6) File Sequence Check Option: 무결성 검사 우선순위

<pre>
df -h: Get information of all mounted file systems.
mount -a: Mounts all mount points.
umount -l : Unmounts storage forcibly.
</pre>

* modprobe: Add/Remove a LKM(Loadable Kernel Module) to the Linux Kernel

modprobe는 의존성을 고려하여 리눅스 커널에 모듈을 로드하는 명령어다. 의존성이 있는 모듈들이 있다면 해당 모듈까지 한꺼번에 같이 로드하는 특징이 있다.

* g_mass_storage: Mass Storage Gadget (or MSG) acts as a USB Mass Storage device

  1) file: path to files or block devices used for backing storage. (Beware: that if a file is used as a backing storage, it may not be modified by any other process. This is because the host assumes the data does not change without its knowledge. It may be  read, but (if the logical unit is writable) due to buffering on the host side, the contents are not well defined.
  2) removable: either "y", "Y" or "1" for true or "n", "N" or "0" for false. (Beware: "removable" means the logical unit's media can be  ejected or removed (as is true for a CD-ROM drive or a card reader).  It does *not* mean that the entire gadget can be unplugged from the host; the proper term for that is "hot-unpluggable".
  3) ro: Specifies whether each logical unit should be reported as read only.
  4) stall: Specifies whether the gadget is allowed to halt bulk endpoints. It's usually true.

* fuser: Checks which process is occupying a file.

  1) k: Kill all the processes related to a file.
  2) v: Get detail information about processes and users related to a file.

### Usage

#### To emulate a mass storage device

* [g_mass_storage(MSG) Document](https://www.kernel.org/doc/Documentation/usb/mass-storage.txt)

<pre>
sudo modprobe g_mass_storage file={Storage File} stall=0 ro=0 removable=1
sudo modprobe g_mass_storage -r: Removes mass storage module
</pre>

#### To change USB image dynamically

<pre>
sudo bash -c 'echo "/home/pi/usbdisk2.img" > /sys/devices/platform/soc/20980000.usb/gadget/lun0/file'
</pre>

#### To make a container file and mount the container file

<pre>
# Make a container file
sudo dd bs=1M if=/dev/zero of=./usbdisk2.img count=64
sudo mkdosfs ./usbdisk2.img -F 32 -I
# Setting for mounting
sudo mkdir /mnt/usb_share2
sudo vi /etc/fstab
# Append the line below to the end of the file:
/home/pi/usbdisk2.img /mnt/usb_share2 vfat users,umask=000 0 2
# Mount
sudo mount -a
</pre>

### Issue

* Cache Coherence Problem: When Rasberry Pi provides mass storage to a host, if Rasberry Pi and host computer write the same file simultaneously, the file is corrupted. But if only Rasberry Pi writes the file, after reconneting, the host computer can read the file well. In other words, a file is used as a backing storage, it may not  be modified by any other process.
