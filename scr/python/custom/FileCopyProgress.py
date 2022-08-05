# # https://fredrikaverpil.github.io/2015/05/12/file-copy-progress-window-with-pyqt-pyside-and-shutil/
# # https://github.com/dbr/checktveps/blob/1be8f4445fbf766eba25f98f78ec52e955571608/autoPathTv.py#L64-153
# # http://code.activestate.com/recipes/168639/
import os
import shutil

from PySide6.QtCore import QCoreApplication, QFile, QDir, QDirIterator
from PySide6.QtWidgets import QProgressDialog, QDialog, QHBoxLayout, QPushButton, QFileDialog


class QFileCopyProgress(QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent)

        # self.main_layout = QHBoxLayout()
        # self.setLayout(self.main_layout)
        #
        # self.button = QPushButton()
        # self.button.clicked.connect(lambda: self.copy_files())
        # self.main_layout.addWidget(self.button)

    # Vanilla
    @staticmethod
    def copy_loop(scr, dest):
        file_list = QFileCopyProgress.recur_file_list(scr)
        n = 0

        for file in file_list:
            QFileCopyProgress.copy_file(file, dest)
    @staticmethod
    def copy_file(scr, dest):
        try:
            shutil.copy(scr, dest)
            return True
        except:
            return False
    @staticmethod
    def create_dirtree_without_files(src, dst):
        # getting the absolute path of the source
        # directory
        src = os.path.abspath(src)

        # making a variable having the index till which
        # src string has directory and a path separator
        src_prefix = len(src) + len(os.path.sep)

        # making the destination directory
        os.makedirs(dst)

        # doing os walk in source directory
        for root, dirs, files in os.walk(src):
            for dirname in dirs:
                # here dst has destination directory,
                # root[src_prefix:] gives us relative
                # path from source directory
                # and dirname has folder names
                dirpath = os.path.join(dst, root[src_prefix:], dirname)

                # making the path which we made by
                # joining all of the above three
                os.mkdir(dirpath)

    @staticmethod
    def recur_file_list(scr):
        for roots, dirnames, files in os.walk(scr):
            # treat files before
            for f in files:
                # relative path of the file
                yield os.path.join(roots, f)

            for d in dirnames:
                QFileCopyProgress.recur_file_list(os.path.join(roots, d))
    @staticmethod
    def file_counter(scr):
        # folder path
        count = 0

        for f in QFileCopyProgress.recur_file_list(scr):
            count+=1

        return count


    # Pyside
    def copy_files(self, scr=None, dest=None, relative_path_to_remove=None):

        if scr == None:
            scr = QFileDialog.getExistingDirectory(caption="Open Source Folder")
        if dest == None:
            dest = QFileDialog.getExistingDirectory(caption="Open Destination Folder")
        if scr == None == dest:
            return False

        if not QDir(dest).exists():
            QDir().mkpath(dest)



        # copy tree before
        QFileCopyProgress.Qcopy_tree(scr, dest)
        # number of file to copy
        n = QFileCopyProgress.Qfile_counter(scr)
        # file generator
        files_to_copy = QFileCopyProgress.Qrecur_file_list(scr)
        # counter
        i = 0
        # list of file who failed to be copy
        failed_to_copy = []

        # Progress bar
        progress_dialog = QProgressDialog(self)
        progress_dialog.setCancelButtonText("&Cancel")
        progress_dialog.setRange(0, n)
        progress_dialog.setWindowTitle("Copy Files")
        progress_dialog.show()

        for f in files_to_copy:
            progress_dialog.setValue(i)
            progress_dialog.setLabelText(f"Copying file number {i} of {n}")
            QCoreApplication.processEvents()

            if progress_dialog.wasCanceled():
                break

            if relative_path_to_remove:
                destination = rf"{dest}/{f.replace(relative_path_to_remove, '')}"

            else:
                destination = rf"{dest}/{f}"
            source = rf"{scr}/{f}"


            # shutil.copy2(source, destination)
            if not QFile.copy(source, destination):
                failed_to_copy.append(f)

            i += 1
            # better in a output windows
        print(*failed_to_copy,sep='\n')
        progress_dialog.close()

        return
    @staticmethod
    def Qrecur_file_list(scr):
        _current_dir = QDir(scr)
        _current_dir.setFilter(QDir.Files or QDir.NoDotAndDotDot)
        _current_dir.setSorting(QDir.Name)
        dit = QDirIterator(scr, QDir.Files or QDir.NoDotAndDotDot, QDirIterator.Subdirectories | QDir.Files)

        while dit.hasNext():
            im = _current_dir.relativeFilePath(dit.next())
            yield im
    @staticmethod
    def Qfile_counter(scr):
        _current_dir = QDir(scr)
        _current_dir.setFilter(QDir.Files or QDir.NoDotAndDotDot)
        _current_dir.setSorting(QDir.Name)
        dit = QDirIterator(scr, QDir.Files or QDir.NoDotAndDotDot, QDirIterator.Subdirectories | QDir.Files)
        count = 0
        while dit.hasNext():
            dit.next()
            count+=1
        return count
    @staticmethod
    def Qcopy_tree(scr, dest):

        dit = QDirIterator(scr, QDir.Dirs, QDirIterator.Subdirectories)

        while dit.hasNext():
            im = dit.next()

            if '/..' in im[-3::] or '\..' in im[-3::] or '/.' in im[-2::] or '\.' in im[-2::]:
                pass
            else:
                destination = dest+im.replace(scr,"")
                # QDir().mkdir(destination)
                QDir().mkpath(destination)




# # Only needed for access to command line arguments
# import sys
# 
# # test = QFileCopyProgress()
# # test.copy_file('.',r'C:\Users\Julien\Documents')
# 
# # You need one (and only one) QApplication instance per application.
# # Pass in sys.argv to allow command line arguments for your app.
# # If you know you won't use command line arguments QApplication([]) works too.
# app = QApplication(sys.argv)
# 
# # Create a Qt widget, which will be our window.
# window = QFileCopyProgress()
# 
# 
# window.show()  # IMPORTANT!!!!! Windows are hidden by default.
# 
# # Start the event loop.
# app.exec()



