root@0e12f649691a:~/acpi-launcher# flutter run -d linux
Launching lib/main.dart on Linux in debug mode...
Building Linux application...                                           
✓ Built build/linux/x64/debug/bundle/acpi_launcher

(acpi_launcher:164129): dbind-WARNING **: 06:04:39.940: Couldn't connect to accessibility bus: Failed to connect to socket /run/user/1000/at-spi/bus: No such file or directory
Gtk-Message: 06:04:39.958: Failed to load module "canberra-gtk-module"
Gtk-Message: 06:04:39.959: Failed to load module "canberra-gtk-module"

(acpi_launcher:164129): Atk-CRITICAL **: 06:04:39.975: atk_socket_embed: assertion 'plug_id != NULL' failed
libGL error: glx: failed to create dri3 screen
libGL error: failed to load driver: nouveau
Proxy server (Socket based) started on http://localhost:41309
ApiConstants.baseUrl: http://localhost:41309/?url=/api/v1
[🌎 Easy Localization] [DEBUG] Localization initialized
[🌎 Easy Localization] [DEBUG] Start
[🌎 Easy Localization] [DEBUG] Init state
[🌎 Easy Localization] [DEBUG] Build
[🌎 Easy Localization] [DEBUG] Init Localization Delegate
[🌎 Easy Localization] [DEBUG] Init provider
[🌎 Easy Localization] [DEBUG] Load Localization Delegate
[🌎 Easy Localization] [DEBUG] Load asset from assets/translations
Syncing files to device Linux...                                   190ms

Flutter run key commands.
r Hot reload. 🔥🔥🔥
R Hot restart.
h List all available interactive commands.
d Detach (terminate "flutter run" but leave application running).
c Clear the screen
q Quit (terminate the application on the device).

A Dart VM Service on Linux is available at: http://127.0.0.1:45875/7jAZvTvnRtg=/
The Flutter DevTools debugger and profiler on Linux is available at: http://127.0.0.1:9100?uri=http://127.0.0.1:45875/7jAZvTvnRtg=/

** (acpi_launcher:164129): WARNING **: 06:04:40.868: libsecret_error: Failed to unlock the keyring
[ERROR:flutter/runtime/dart_vm_initializer.cc(40)] Unhandled Exception: PlatformException(Libsecret error, Failed to unlock the keyring, null, null)
#0      StandardMethodCodec.decodeEnvelope (package:flutter/src/services/message_codecs.dart:652:7)
#1      MethodChannel._invokeMethod (package:flutter/src/services/platform_channel.dart:370:18)
<asynchronous suspension>
#2      _SignInScreenState._loadSavedIp (package:acpi_launcher/screens/accounts/sign_in_screen.dart:56:16)
<asynchronous suspension>
#3      _SignInScreenState.initState.<anonymous closure> (package:acpi_launcher/screens/accounts/sign_in_screen.dart:41:25)
<asynchronous suspension>

*** Request ***
uri: http://localhost:41309/?url=/api/v1/admin
method: GET
responseType: ResponseType.json
followRedirects: true
persistentConnection: true
connectTimeout: null
sendTimeout: null
receiveTimeout: null
receiveDataWhenStatusError: true
extra: {}
headers:
data:
null

[Proxy UriDebug] Input urlParam: /api/v1/admin
[Proxy UriDebug] API call. Resolved URI with original port: https://10.175.195.66:9300/api/v1/admin for path: /api/v1/admin
[Proxy Auth] Request to: /api/v1/admin, Method: GET, isApiCall: true, requiresAuth (rule based): true, final requiresAuthHeader: true

** (acpi_launcher:164129): WARNING **: 06:05:05.429: libsecret_error: Failed to unlock the keyring
Error in _forwardHttpRequestWithSocket for https://10.175.195.66:9300/api/v1/admin: PlatformException(Libsecret error, Failed to unlock the keyring, null, null)
#0      StandardMethodCodec.decodeEnvelope (package:flutter/src/services/message_codecs.dart:652:7)
#1      MethodChannel._invokeMethod (package:flutter/src/services/platform_channel.dart:370:18)
<asynchronous suspension>
#2      AccountsManageRepository.getValidAccessToken (package:acpi_launcher/repos/accounts/accounts_manage_repository.dart:50:27)
<asynchronous suspension>
#3      _forwardHttpRequestWithSocketAuthAndRetry (package:acpi_launcher/network/proxy_server.dart:294:37)
<asynchronous suspension>
#4      _proxyHandler (package:acpi_launcher/network/proxy_server.dart:112:28)
<asynchronous suspension>
#5      logRequests.<anonymous closure>.<anonymous closure>.<anonymous closure> (package:shelf/src/middleware/logger.dart:30:62)
<asynchronous suspension>
#6      handleRequest (package:shelf/shelf_io.dart:140:16)
<asynchronous suspension>

Proxy: 2025-07-04T06:05:05.321913  0:00:00.123614 GET     [503] /?url=/api/v1/admin
*** DioException ***:
uri: http://localhost:41309/?url=/api/v1/admin
DioException [bad response]: This exception was thrown because the response has a status code of 503 and RequestOptions.validateStatus was configured to throw for this status code.
The status code of 503 has the following meaning: "Server error - the server failed to fulfil an apparently valid request"
Read more about status codes at https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
In order to resolve this exception you typically have either to verify and fix your request code or you have to fix the server code.

uri: http://localhost:41309/?url=/api/v1/admin
statusCode: 503
headers:
 x-powered-by: Dart with package:shelf
 date: Fri, 04 Jul 2025 06:05:05 GMT
 access-control-allow-origin: *
 content-length: 116
 x-frame-options: SAMEORIGIN
 content-type: text/plain; charset=utf-8
 x-xss-protection: 1; mode=block
 x-content-type-options: nosniff
Response Text:
Proxy to origin server failed (Socket): PlatformException(Libsecret error, Failed to unlock the keyring, null, null)


checkAdmin Exception: Instance of 'CustomException'
