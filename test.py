C:\Users\USER\FCTtool 디렉터리
 
2025-06-04  오후 03:11    <DIR>          .
2025-06-04  오후 03:11    <DIR>          ..
2025-06-04  오후 03:09            12,999 gui_fct.py
2025-06-04  오후 02:29             1,144 new_cfg.yml
2025-06-04  오후 03:11    <DIR>          venv
               2개 파일              14,143 바이트
               3개 디렉터리  64,366,522,368 바이트 남음
 
(venv) C:\Users\USER\FCTtool>pyinstaller --onefile --noconsole --name lg_fct_gui gui_fct.py
151 INFO: PyInstaller: 6.14.0, contrib hooks: 2025.4
152 INFO: Python: 3.12.3
175 INFO: Platform: Windows-10-10.0.19045-SP0
175 INFO: Python environment: C:\Users\USER\FCTtool\venv
176 INFO: wrote C:\Users\USER\FCTtool\lg_fct_gui.spec
179 INFO: Module search paths (PYTHONPATH):
['C:\\Users\\USER\\FCTtool\\venv\\Scripts\\pyinstaller.exe',
'C:\\Users\\USER\\AppData\\Local\\Programs\\Python\\Python312\\python312.zip',
'C:\\Users\\USER\\AppData\\Local\\Programs\\Python\\Python312\\DLLs',
'C:\\Users\\USER\\AppData\\Local\\Programs\\Python\\Python312\\Lib',
'C:\\Users\\USER\\AppData\\Local\\Programs\\Python\\Python312',
'C:\\Users\\USER\\FCTtool\\venv',
'C:\\Users\\USER\\FCTtool\\venv\\Lib\\site-packages',
'C:\\Users\\USER\\FCTtool\\venv\\Lib\\site-packages\\setuptools\\_vendor',
'C:\\Users\\USER\\FCTtool']
462 INFO: checking Analysis
463 INFO: Building Analysis because Analysis-00.toc is non existent
464 INFO: Running Analysis Analysis-00.toc
466 INFO: Target bytecode optimization level: 0
466 INFO: Initializing module dependency graph...
469 INFO: Initializing module graph hook caches...
479 INFO: Analyzing modules for base_library.zip ...
1303 INFO: Processing standard module hook 'hook-heapq.py' from 'C:\\Users\\USER\\FCTtool\\venv\\Lib\\site-packages\\PyInstaller\\hooks'
1362 INFO: Processing standard module hook 'hook-encodings.py' from 'C:\\Users\\USER\\FCTtool\\venv\\Lib\\site-packages\\PyInstaller\\hooks'
2522 INFO: Processing standard module hook 'hook-pickle.py' from 'C:\\Users\\USER\\FCTtool\\venv\\Lib\\site-packages\\PyInstaller\\hooks'
3656 INFO: Caching module dependency graph...
3680 INFO: Looking for Python shared library...
3700 INFO: Using Python shared library: C:\Users\USER\AppData\Local\Programs\Python\Python312\python312.dll
3700 INFO: Analyzing C:\Users\USER\FCTtool\gui_fct.py
 
Syntax error in C:\Users\USER\FCTtool\gui_fct.py
  File "C:\Users\USER\FCTtool\gui_fct.py", line 39
     subprocess.run(f"ssh-keygen -R {}".format(ip), shell=True)
                                     ^
SyntaxError: f-string: valid expression required before '}'
