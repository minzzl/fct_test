==473084== 1,048,576 bytes in 1 blocks are definitely lost in loss record 345 of 345                                                                             
==473084==    at 0x487519C: malloc (vg_replace_malloc.c:381)                                                                                                     
==473084==    by 0x48B182B: ??? (in /lib/libSegFault.so)                                                                                                         
==473084==    by 0x4005663: call_init.part.0 (dl-init.c:74)                                                                                                      
==473084==    by 0x4005777: call_init (dl-init.c:29)                                                                                                             
==473084==    by 0x4005777: _dl_init (dl-init.c:121)                                                                                                             
==473084==    by 0x4017D67: ??? (in /lib/ld-linux-aarch64.so.1)                                                                                                  
==473084==                                                                                                                                                       
==473084== LEAK SUMMARY:                                                                                                                                         
==473084==    definitely lost: 1,048,603 bytes in 6 blocks                                                                                                       
==473084==    indirectly lost: 0 bytes in 0 blocks                                                                                                               
==473084==      possibly lost: 2,112 bytes in 6 blocks                                                                                                           
==473084==    still reachable: 173,390 bytes in 1,350 blocks                                                                                                     
==473084==         suppressed: 0 bytes in 0 blocks                                                                                                               
==473084== Reachable blocks (those to which a pointer was found) are not shown.                                                                                  
==473084== To see them, rerun with: --leak-check=full --show-leak-kinds=all                                                                                      
==473084==                                                                                                                                                       
==473084== For lists of detected and suppressed errors, rerun with: -s                                                                                           
==473084== ERROR SUMMARY: 14 errors from 14 contexts (suppressed: 0 from 0)                                                                                      
[root@webOSNano-unofficial /media/cryptofs/apps/usr/palm/services/com.acp.lcd.service]#
