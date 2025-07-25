minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ nvidia-smi
NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver. Make sure that the latest NVIDIA driver is installed and running.

minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ apt policy nividia-diver-575
N: Unable to locate package nividia-diver-575
minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ apt policy nividia-driver-575
N: Unable to locate package nividia-driver-575
minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ dpkg -l | grep nvidia
ii  libnvidia-cfg1-575:amd64                         575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA binary OpenGL/GLX configuration library
ii  libnvidia-common-575                             575.64.03-0ubuntu0.24.04.1                all          Shared files used by the NVIDIA libraries
ii  libnvidia-compute-575:amd64                      575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA libcompute package
ii  libnvidia-decode-575:amd64                       575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA Video Decoding runtime libraries
ii  libnvidia-egl-wayland1:amd64                     1:1.1.13-1build1                          amd64        Wayland EGL External Platform library -- shared library
ii  libnvidia-encode-575:amd64                       575.64.03-0ubuntu0.24.04.1                amd64        NVENC Video Encoding runtime library
ii  libnvidia-extra-575:amd64                        575.64.03-0ubuntu0.24.04.1                amd64        Extra libraries for the NVIDIA driver
ii  libnvidia-fbc1-575:amd64                         575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA OpenGL-based Framebuffer Capture runtime library
ii  libnvidia-gl-575:amd64                           575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA OpenGL/GLX/EGL/GLES GLVND libraries and Vulkan ICD
rc  linux-modules-nvidia-535-6.11.0-19-generic       6.11.0-19.19~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-19
rc  linux-modules-nvidia-535-6.11.0-21-generic       6.11.0-21.21~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-21
rc  linux-modules-nvidia-535-6.11.0-24-generic       6.11.0-24.24~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-24
rc  linux-modules-nvidia-535-6.11.0-25-generic       6.11.0-25.25~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-25
rc  linux-modules-nvidia-535-6.11.0-26-generic       6.11.0-26.26~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-26
rc  linux-modules-nvidia-535-6.11.0-28-generic       6.11.0-28.28~24.04.1                      amd64        Linux kernel nvidia modules for version 6.11.0-28
rc  linux-modules-nvidia-535-6.8.0-31-generic        6.8.0-31.31                               amd64        Linux kernel nvidia modules for version 6.8.0-31
rc  linux-modules-nvidia-535-6.8.0-35-generic        6.8.0-35.35+1                             amd64        Linux kernel nvidia modules for version 6.8.0-35
rc  linux-modules-nvidia-535-6.8.0-36-generic        6.8.0-36.36+1                             amd64        Linux kernel nvidia modules for version 6.8.0-36
rc  linux-modules-nvidia-535-6.8.0-38-generic        6.8.0-38.38+1                             amd64        Linux kernel nvidia modules for version 6.8.0-38
rc  linux-modules-nvidia-535-6.8.0-39-generic        6.8.0-39.39                               amd64        Linux kernel nvidia modules for version 6.8.0-39
rc  linux-modules-nvidia-535-6.8.0-40-generic        6.8.0-40.40                               amd64        Linux kernel nvidia modules for version 6.8.0-40
rc  linux-modules-nvidia-535-6.8.0-41-generic        6.8.0-41.41+1                             amd64        Linux kernel nvidia modules for version 6.8.0-41
rc  linux-modules-nvidia-535-6.8.0-44-generic        6.8.0-44.44+1                             amd64        Linux kernel nvidia modules for version 6.8.0-44
rc  linux-modules-nvidia-535-6.8.0-45-generic        6.8.0-45.45+1                             amd64        Linux kernel nvidia modules for version 6.8.0-45
rc  linux-modules-nvidia-535-6.8.0-47-generic        6.8.0-47.47+1                             amd64        Linux kernel nvidia modules for version 6.8.0-47
rc  linux-modules-nvidia-535-6.8.0-48-generic        6.8.0-48.48+1                             amd64        Linux kernel nvidia modules for version 6.8.0-48
rc  linux-modules-nvidia-535-6.8.0-49-generic        6.8.0-49.49                               amd64        Linux kernel nvidia modules for version 6.8.0-49
rc  linux-modules-nvidia-535-6.8.0-50-generic        6.8.0-50.51+1                             amd64        Linux kernel nvidia modules for version 6.8.0-50
rc  linux-modules-nvidia-535-6.8.0-51-generic        6.8.0-51.52+1                             amd64        Linux kernel nvidia modules for version 6.8.0-51
rc  linux-modules-nvidia-535-6.8.0-52-generic        6.8.0-52.53                               amd64        Linux kernel nvidia modules for version 6.8.0-52
rc  linux-objects-nvidia-535-6.11.0-19-generic       6.11.0-19.19~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-19 (objects)
rc  linux-objects-nvidia-535-6.11.0-21-generic       6.11.0-21.21~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-21 (objects)
rc  linux-objects-nvidia-535-6.11.0-24-generic       6.11.0-24.24~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-24 (objects)
rc  linux-objects-nvidia-535-6.11.0-25-generic       6.11.0-25.25~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-25 (objects)
rc  linux-objects-nvidia-535-6.11.0-26-generic       6.11.0-26.26~24.04.1+1                    amd64        Linux kernel nvidia modules for version 6.11.0-26 (objects)
rc  linux-objects-nvidia-535-6.11.0-28-generic       6.11.0-28.28~24.04.1                      amd64        Linux kernel nvidia modules for version 6.11.0-28 (objects)
ii  linux-objects-nvidia-535-6.11.0-29-generic       6.11.0-29.29~24.04.1+3                    amd64        Linux kernel nvidia modules for version 6.11.0-29 (objects)
ii  linux-objects-nvidia-535-6.14.0-24-generic       6.14.0-24.24~24.04.3+1                    amd64        Linux kernel nvidia modules for version 6.14.0-24 (objects)
rc  linux-objects-nvidia-535-6.8.0-31-generic        6.8.0-31.31                               amd64        Linux kernel nvidia modules for version 6.8.0-31 (objects)
rc  linux-objects-nvidia-535-6.8.0-35-generic        6.8.0-35.35+1                             amd64        Linux kernel nvidia modules for version 6.8.0-35 (objects)
rc  linux-objects-nvidia-535-6.8.0-36-generic        6.8.0-36.36+1                             amd64        Linux kernel nvidia modules for version 6.8.0-36 (objects)
rc  linux-objects-nvidia-535-6.8.0-38-generic        6.8.0-38.38+1                             amd64        Linux kernel nvidia modules for version 6.8.0-38 (objects)
rc  linux-objects-nvidia-535-6.8.0-39-generic        6.8.0-39.39                               amd64        Linux kernel nvidia modules for version 6.8.0-39 (objects)
rc  linux-objects-nvidia-535-6.8.0-40-generic        6.8.0-40.40                               amd64        Linux kernel nvidia modules for version 6.8.0-40 (objects)
rc  linux-objects-nvidia-535-6.8.0-41-generic        6.8.0-41.41+1                             amd64        Linux kernel nvidia modules for version 6.8.0-41 (objects)
rc  linux-objects-nvidia-535-6.8.0-44-generic        6.8.0-44.44+1                             amd64        Linux kernel nvidia modules for version 6.8.0-44 (objects)
rc  linux-objects-nvidia-535-6.8.0-45-generic        6.8.0-45.45+1                             amd64        Linux kernel nvidia modules for version 6.8.0-45 (objects)
rc  linux-objects-nvidia-535-6.8.0-47-generic        6.8.0-47.47+1                             amd64        Linux kernel nvidia modules for version 6.8.0-47 (objects)
rc  linux-objects-nvidia-535-6.8.0-48-generic        6.8.0-48.48+1                             amd64        Linux kernel nvidia modules for version 6.8.0-48 (objects)
rc  linux-objects-nvidia-535-6.8.0-49-generic        6.8.0-49.49                               amd64        Linux kernel nvidia modules for version 6.8.0-49 (objects)
rc  linux-objects-nvidia-535-6.8.0-50-generic        6.8.0-50.51+1                             amd64        Linux kernel nvidia modules for version 6.8.0-50 (objects)
rc  linux-objects-nvidia-535-6.8.0-51-generic        6.8.0-51.52+1                             amd64        Linux kernel nvidia modules for version 6.8.0-51 (objects)
rc  linux-objects-nvidia-535-6.8.0-52-generic        6.8.0-52.53                               amd64        Linux kernel nvidia modules for version 6.8.0-52 (objects)
ii  linux-signatures-nvidia-6.11.0-29-generic        6.11.0-29.29~24.04.1+3                    amd64        Linux kernel signatures for nvidia modules for version 6.11.0-29-generic
ii  linux-signatures-nvidia-6.14.0-24-generic        6.14.0-24.24~24.04.3+1                    amd64        Linux kernel signatures for nvidia modules for version 6.14.0-24-generic
ii  nvidia-compute-utils-575                         575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA compute utilities
ii  nvidia-dkms-575                                  575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA DKMS package
ii  nvidia-driver-575                                575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA driver metapackage
ii  nvidia-firmware-575-575.64.03                    575.64.03-0ubuntu0.24.04.1                amd64        Firmware files used by the kernel module
ii  nvidia-kernel-common-575                         575.64.03-0ubuntu0.24.04.1                amd64        Shared files used with the kernel module
ii  nvidia-kernel-source-575                         575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA kernel source package
ii  nvidia-prime                                     0.8.17.2                                  all          Tools to enable NVIDIA's Prime
ii  nvidia-settings                                  510.47.03-0ubuntu4                        amd64        Tool for configuring the NVIDIA graphics driver
ii  nvidia-utils-575                                 575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA driver support binaries
ii  screen-resolution-extra                          0.18.3                                    all          Extension for the nvidia-settings control panel
ii  xserver-xorg-video-nvidia-575                    575.64.03-0ubuntu0.24.04.1                amd64        NVIDIA binary Xorg driver
minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ xrandr
Screen 0: minimum 16 x 16, current 1920 x 1080, maximum 32767 x 32767
None-1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 508mm x 285mm
   1920x1080     59.96*+
   1440x1080     59.99  
   1400x1050     59.98  
   1280x1024     59.89  
   1280x960      59.94  
   1152x864      59.96  
   1024x768      59.92  
   800x600       59.86  
   640x480       59.38  
   320x240       59.52  
   1680x1050     59.95  
   1440x900      59.89  
   1280x800      59.81  
   1152x720      59.97  
   960x600       59.63  
   928x580       59.88  
   800x500       59.50  
   768x480       59.90  
   720x480       59.71  
   640x400       59.95  
   320x200       58.96  
   1600x900      59.95  
   1368x768      59.88  
   1280x720      59.86  
   1024x576      59.90  
   864x486       59.92  
   720x400       59.55  
   640x350       59.77  
