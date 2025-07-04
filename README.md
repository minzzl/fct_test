root@0e12f649691a:/opt# flutter doctor 
Doctor summary (to see all details, run flutter doctor -v):
[✓] Flutter (Channel stable, 3.32.5, on Ubuntu 22.04.1 LTS 6.11.0-29-generic, locale en_US.UTF-8)
[✓] Android toolchain - develop for Android devices (Android SDK version 33.0.1)
[✗] Chrome - develop for the web (Cannot find Chrome executable at google-chrome)
    ! Cannot find Chrome. Try setting CHROME_EXECUTABLE to a Chrome executable.
[✗] Linux toolchain - develop for Linux desktop
    ✗ CMake is required for Linux development.
      It is likely available from your distribution (e.g.: apt install cmake), or can be downloaded from https://cmake.org/download/
    ! Unable to access driver information using 'eglinfo'.
      It is likely available from your distribution (e.g.: apt install mesa-utils)
[!] Android Studio (not installed)
[✓] Connected device (1 available)
[✓] Network resources

! Doctor found issues in 3 categories.
root@0e12f649691a:/opt# cd 
android-sdk-linux/ flutter/           
root@0e12f649691a:/opt# cd 
android-sdk-linux/ flutter/           
root@0e12f649691a:/opt# cd 
root@0e12f649691a:~# cd 
.android/                 .config/                  .gitconfig                .pub-cache/               workspace.code-workspace
.bash_history             .dotnet/                  .gnupg/                   .ssh/                     
.bashrc                   fct_test/                 lgsi-homelauncher/        .vscode-server/           
.cache/                   .flutter                  .profile                  .wget-hsts                
root@0e12f649691a:~# cd lgsi-homelauncher/
root@0e12f649691a:~/lgsi-homelauncher# flutter pub get
Resolving dependencies... 
Downloading packages... 
  archive 3.6.1 (4.0.7 available)
  characters 1.4.0 (1.4.1 available)
  d_chart 2.10.5 (3.0.0 available)
  file_picker 8.3.7 (10.2.0 available)
  fl_chart 0.68.0 (1.0.0 available)
  flutter_lints 3.0.2 (6.0.0 available)
  flutter_secure_storage 8.1.0 (9.2.4 available)
  flutter_secure_storage_linux 1.2.3 (2.0.1 available)
  flutter_secure_storage_macos 3.1.3 (4.0.0 available)
  flutter_secure_storage_platform_interface 1.1.2 (2.0.1 available)
  flutter_secure_storage_web 1.2.1 (2.0.0 available)
  flutter_secure_storage_windows 2.1.1 (4.0.0 available)
  image 4.3.0 (4.5.4 available)
  internet_connection_checker 1.0.0+1 (3.0.1 available)
  js 0.6.7 (0.7.2 available)
  leak_tracker 10.0.9 (11.0.1 available)
  leak_tracker_flutter_testing 3.0.9 (3.0.10 available)
  leak_tracker_testing 3.0.1 (3.0.2 available)
  lints 3.0.0 (6.0.0 available)
  material_color_utilities 0.11.1 (0.13.0 available)
  meta 1.16.0 (1.17.0 available)
  petitparser 6.1.0 (7.0.0 available)
  syncfusion_flutter_core 29.2.11 (30.1.38 available)
  syncfusion_flutter_pdf 29.2.11 (30.1.38 available)
  syncfusion_flutter_pdfviewer 29.2.11 (30.1.38 available)
  syncfusion_flutter_signaturepad 29.2.11 (30.1.38 available)
  syncfusion_pdfviewer_macos 29.2.11 (30.1.38 available)
  syncfusion_pdfviewer_platform_interface 29.2.11 (30.1.38 available)
  syncfusion_pdfviewer_web 29.2.11 (30.1.38 available)
  syncfusion_pdfviewer_windows 29.2.11 (30.1.38 available)
  test_api 0.7.4 (0.7.6 available)
  timezone 0.9.4 (0.10.1 available)
  vector_math 2.1.4 (2.2.0 available)
  vm_service 15.0.0 (15.0.2 available)
  window_manager 0.4.3 (0.5.0 available)
  xml 6.5.0 (6.6.0 available)
Got dependencies!
36 packages have newer versions incompatible with dependency constraints.
Try `flutter pub outdated` for more information.
root@0e12f649691a:~/lgsi-homelauncher# flutter run -d linux
Launching lib/main.dart on Linux in debug mode...
Building Linux application...                                           
Error: CMake is required for Linux development.
It is likely available from your distribution (e.g.: apt install cmake), or can be downloaded from https://cmake.org/download/
