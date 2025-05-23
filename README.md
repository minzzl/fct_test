	../../gcc/config/aarch64/aarch64-c.cc
/usr/bin/g++ -std=gnu++11  -fno-PIE -c  -DIN_GCC_FRONTEND -O2 -I/home/user/work/buildroot-2024.02.1/output/host/include   -DIN_GCC  -DCROSS_DIRECTORY_STRUCTURE   -fno-exceptions -fno-rtti -fasynchronous-unwind-tables -W -Wall -Wno-narrowing -Wwrite-strings -Wcast-qual -Wmissing-format-attribute -Woverloaded-virtual -pedantic -Wno-long-long -Wno-variadic-macros -Wno-overlength-strings   -DHAVE_CONFIG_H -I. -I. -I../../gcc -I../../gcc/. -I../../gcc/../include -I../../gcc/../libcpp/include -I../../gcc/../libcody -I/home/user/work/buildroot-2024.02.1/output/host/include -I/home/user/work/buildroot-2024.02.1/output/host/include -I/home/user/work/buildroot-2024.02.1/output/host/include  -I../../gcc/../libdecnumber -I../../gcc/../libdecnumber/dpd -I../libdecnumber -I../../gcc/../libbacktrace   -o glibc-c.o -MT glibc-c.o -MMD -MP -MF ./.deps/glibc-c.TPo ../../gcc/config/glibc-c.cc
virtual memory exhausted: Cannot allocate memory
virtual memory exhausted: Cannot allocate memory
virtual memory exhausted: Cannot allocate memory
Makefile:1143: recipe for target 'c-family/c-attribs.o' failed
make[3]: *** [c-family/c-attribs.o] Error 1
make[3]: *** Waiting for unfinished jobs....
Makefile:1143: recipe for target 'c-family/c-warn.o' failed
make[3]: *** [c-family/c-warn.o] Error 1
../../gcc/config/aarch64/t-aarch64:126: recipe for target 'aarch64-c.o' failed
make[3]: *** [aarch64-c.o] Error 1
/bin/bash ../../gcc/../move-if-change tmp-automata.cc insn-automata.cc
echo timestamp > s-automata
/bin/bash ../../gcc/../move-if-change tmp-attrtab.cc    insn-attrtab.cc
/bin/bash ../../gcc/../move-if-change tmp-dfatab.cc     insn-dfatab.cc
/bin/bash ../../gcc/../move-if-change tmp-latencytab.cc insn-latencytab.cc
echo timestamp > s-attrtab
rm gcc.pod
Makefile:4596: recipe for target 'all-gcc' failed
make[2]: *** [all-gcc] Error 2
package/pkg-generic.mk:280: recipe for target '/home/user/work/buildroot-2024.02.1/output/build/host-gcc-initial-12.3.0/.stamp_built' failed
make[1]: *** [/home/user/work/buildroot-2024.02.1/output/build/host-gcc-initial-12.3.0/.stamp_built] Error 2
Makefile:82: recipe for target '_all' failed
make: *** [_all] Error 2
