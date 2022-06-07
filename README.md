# PhysiCellGui
A simple Pyside GUI for developers of PhysiCell.

# How to open it
1. Install Pyside6 libraries\
    `pip install PySide6`
2. Install pyinstaller\
    `pip install pyinstaller`
3. Go to PhysiCellGui folder and open a terminal
4. Run this command\
   For Windows : `pyside6-uic ..\ui\PhysiCellGui.ui -o ui_PhysiCellGui.py`\
   For Linux : `pyside6-uic ..\ui\PhysiCellGui.ui > ui_PhysiCellGui.py`
5. Repeat 3. 
6. Build\
   For Windows : `pyinstaller --distpath .\scr\python --workpath .\build\work --specpath .\build\spec --onefile --windowed .\scr\python\PhysiCellGui.py`\
   For Linux : `pyinstaller --distpath ./scr/python --workpath ./build/work --specpath ./build/spec --onefile --windowed ./scr/python/PhysiCellGui.py`

## File structure

- src : source files
- ext : externals libraries
- out : temporary files
- doc : documentations