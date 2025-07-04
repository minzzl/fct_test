minzzl@minzzl-HP-Z6-G5-Workstation-Desktop-PC:~$ docker run -it --name flutter-dev -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/flutter-dev:/home/flutter cirrusci/flutter:latest bash
docker: Error response from daemon: Conflict. The container name "/flutter-dev" is already in use by container "2670f4bdf909e573b46c35e06f75329698494e2ab1993f2b8bb6609a95859c9c". You have to remove (or rename) that container to be able to reuse that name.
See 'docker run --help'.
minzzl@minzzl-HP-Z6-G5-Wo
