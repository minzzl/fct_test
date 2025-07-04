root@0e12f649691a:~/lgsi-homelauncher# flutter doctor
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.32.5, on Ubuntu 22.04.1 LTS 6.11.0-29-generic, locale en_US.UTF-8)
[✓] Android toolchain - develop for Android devices (Android SDK version 33.0.1)
[✗] Chrome - develop for the web (Cannot find Chrome executable at google-chrome)
    ! Cannot find Chrome. Try setting CHROME_EXECUTABLE to a Chrome executable.
[✓] Linux toolchain - develop for Linux desktop
[!] Android Studio (not installed)
[✓] Connected device (1 available)
[✓] Network resources

! Doctor found issues in 2 categories.
root@0e12f649691a:~/lgsi-homelauncher# flutter run -d linux
Launching lib/main.dart on Linux in debug mode...
CMake Error at /usr/share/cmake-3.22/Modules/FindPkgConfig.cmake:603 (message):
  A required package was not found
Call Stack (most recent call first):
  /usr/share/cmake-3.22/Modules/FindPkgConfig.cmake:825 (_pkg_check_modules_internal)
  flutter/ephemeral/.plugin_symlinks/flutter_secure_storage_linux/linux/CMakeLists.txt:15 (pkg_check_modules)


Building Linux application...                                           
Error: Unable to generate build files
root@0e12f649691a:~/lgsi-homelauncher# 
