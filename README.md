# PhysiCellGui
A simple Pyside GUI for developers of PhysiCell.

# Terminal launch
Run `.\scr\python\PhysiCellGui.py`

# How to create .exe
1. Install Pyside6 libraries\
    `pip install PySide6`
2. Install pyinstaller\
    `pip install pyinstaller`
3. Go to PhysiCellGui folder and open a terminal
4. Build\
   For Windows : `pyinstaller --distpath .\scr\python --workpath .\build\work --specpath .\build\spec --onefile --hidden-import PySide6.QtSvg --windowed .\scr\python\PhysiCellGui.py`\
   For Linux : `pyinstaller --distpath ./scr/python --workpath ./build/work --specpath ./build/spec --onefile --hidden-import PySide6.QtSvg --windowed ./scr/python/PhysiCellGui.py`

## File structure

- src : source files
- ext : externals libraries
- out : temporary files
- doc : documentations


## How to create a custom add-ons 