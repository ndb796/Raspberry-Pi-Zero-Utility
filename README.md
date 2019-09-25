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
df -h: Get information of all mounted file systems. (마운트 된 파일 시스템의 정보를 불러옵니다.)
mount -a: Mounts all mount points. (/etc/fstab에 작성된 모든 파일 시스템 장치를 마운트합니다.)
umount -l : Unmounts storage forcibly. (특정한 파일 시스템 장치를 강제로 마운트 해제합니다.)
</pre>

* modprobe: Add/Remove a LKM(Loadable Kernel Module) to the Linux Kernel

modprobe는 의존성을 고려하여 리눅스 커널에 모듈을 로드하는 명령어다. 의존성이 있는 모듈들이 있다면 해당 모듈까지 한꺼번에 같이 로드하는 특징이 있다. 예를 들어 가젯이 USB 스토리지처럼 보이도록 하려면 g_mass_storage 명령을 사용할 수 있다.

* g_mass_storage: Mass Storage Gadget (or MSG) acts as a USB Mass Storage device

  1) file: path to files or block devices used for backing storage. (Beware: that if a file is used as a backing storage, it may not be modified by any other process. This is because the host assumes the data does not change without its knowledge. It may be  read, but (if the logical unit is writable) due to buffering on the host side, the contents are not well defined.
  
  file 옵션은 어떤 스토리지 파일을 USB 스토리지로 사용할 지 설정해주는 것이다. 또한 특정한 스토리지 파일을 가젯을 이용해 HOST에게 USB로 제공하고 있다면, 가젯을 제공하는 입장(GUEST)에서는 스토리지 파일의 Mount를 해제해야 한다. 만약 HOST와 GUEST가 동시에 스토리지 파일에 접근하는 경우 버퍼링 문제 때문에 제대로 처리되지 않으며, GUEST를 재부팅해야 할 수도 있다.

  2) removable: either "y", "Y" or "1" for true or "n", "N" or "0" for false. (Beware: "removable" means the logical unit's media can be  ejected or removed (as is true for a CD-ROM drive or a card reader).  It does *not* mean that the entire gadget can be unplugged from the host; the proper term for that is "hot-unpluggable".
  
  removable 옵션은 일반적으로 Y를 준다. Y를 주지 않으면, 애초에 HOST에서 USB로 인식하지 않는 경우가 많다.
  
  3) ro: Specifies whether each logical unit should be reported as read only.
  
  ro 옵션은 USB를 Read Only로 제공할 지의 여부를 설정하는 것이다. Read Only로 설정하는 경우, HOST에서 GUEST(USB)의 파일을 수정하는 작업이 불가능하다.
  
  4) stall: Specifies whether the gadget is allowed to halt bulk endpoints. It's usually true.

* fuser: Checks which process is occupying a file.

  1) k: Kill all the processes related to a file. (해당 파일에 연관된 모든 프로세스 종료)
  2) v: Get detail information about processes and users related to a file. (해당 파일에 연관된 프로세스들의 정보 확인)

### Usage

#### To emulate a mass storage device

* [g_mass_storage(MSG) Document](https://www.kernel.org/doc/Documentation/usb/mass-storage.txt)
* 기본적인 사용 방법은 아래와 같다.

<pre>
sudo modprobe g_mass_storage file={Storage File} stall=0 ro=0 removable=1
sudo modprobe g_mass_storage -r: Removes mass storage module
</pre>

#### To change USB image dynamically

* USB 기능이 HOST에게 제공될 때 (USB 가젯 기능이 활성되었을 때), GUEST의 시스템 폴더에는 해당 USB 가젯의 정보가 담겨 있다. 이 때 file 파일에는 현재 제공 중인 스토리지 파일의 경로가 기록되어 있는데, 이를 수정하면 Dynamic하게 USB 스토리지의 정보를 변경할 수 있다.

<pre>
sudo bash -c 'echo "/home/pi/usbdisk2.img" > /sys/devices/platform/soc/20980000.usb/gadget/lun0/file'
</pre>

#### To make a container file and mount the container file

* 컨테이너 파일이란 스토리지 파일을 의미하는데, USB 기능을 제공하기 위한 스토리지 파일을 만드는 것이다. 64MB 등 원하는 크기로 스토리지 파일을 만들 수 있고, 이는 HOST 입장에서 USB 스토리지 그 자체가 된다. 따라서 스토리지를 생성한 뒤에 파일 시스템 설정을 해주어야 한다. 또한 GUEST 입장에서도 그 파일 시스템에 접근하기 위해서는 Mount 과정이 필요하다.

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

* Cache Coherence Problem: When Rasberry Pi provides mass storage to a host, if Rasberry Pi and host computer write the same file simultaneously, the file is corrupted. But if only Rasberry Pi writes the file, after reconneting, the host computer can read the file well. In other words, a file is used as a backing storage, it may not be modified by any other process.

* If the mounting (/mnt/usb_share) doesn't work at the right time due to 'busy' or dummy data, the **reboot** is required. (USB 가젯 모드를 이용할 때 가젯 모드 활성화 및 마운트를 반복적으로 수행하다 보면 'busy' 상태에 빠질 수 있는데, 이 때는 기기를 재부팅하면 해결된다.)

### Reference

* [Raspberry Pi Zero W를 USB Flash Drive로 만들기](https://www.raspberrypi.org/magpi/pi-zero-w-smart-usb-flash-drive/)
