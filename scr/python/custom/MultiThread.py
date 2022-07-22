# # https://www.pythonguis.com/tutorials/multithreading-pyside6-applications-qthreadpool/

from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QMainWindow, QApplication
from PySide6.QtCore import QTimer, QRunnable, Slot, Signal, QObject, QThreadPool, QFile

import sys
import time
import traceback


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)
class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @Slot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class MainWindow(QMainWindow):


    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.counter = 0

        layout = QVBoxLayout()

        self.l = QLabel("Start")
        b = QPushButton("DANGER!")
        b.pressed.connect(self.oh_no)

        layout.addWidget(self.l)
        layout.addWidget(b)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.recurring_timer)
        self.timer.start()

    def progress_fn(self, n):
        print("%d%% done" % n)

    def execute_this_fn(self, progress_callback):
        for n in range(0, 5):
            time.sleep(1)
            progress_callback.emit(n*100/4)

        return "Done."

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def oh_no(self):
        # Pass the function to execute
        worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)


    def recurring_timer(self):
        self.counter +=1
        self.l.setText("Counter: %d" % self.counter)


app = QApplication(sys.argv)
window = MainWindow()
app.exec_()
# class MainWindow(QMainWindow):
#
#
#     def __init__(self, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
#
#         self.counter = 0
#
#         layout = QVBoxLayout()
#
#         self.l = QLabel("Start")
#         b = QPushButton("DANGER!")
#         b.pressed.connect(self.oh_no)
#
#         layout.addWidget(self.l)
#         layout.addWidget(b)
#
#         w = QWidget()
#         w.setLayout(layout)
#
#         self.setCentralWidget(w)
#         self.show()
#
#         self.threadpool = QThreadPool()
#         print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
#
#         self.timer = QTimer()
#         self.timer.setInterval(1000)
#         self.timer.timeout.connect(self.recurring_timer)
#         self.timer.start()
#
#     def progress_fn(self, n):
#         print("%d%% done" % n)
#     def execute_this_fn(self, progress_callback):
#         # Search for new file
#         def convert_in_str(x):
#             xs = str(x)
#             base = list("00000000")
#             for n in range(len(str(xs))):
#                     base[-len(xs)+n]=xs[n]
#             return ''.join(base)
#
#         n = 144
#         i = 0
#
#         while not QFile.exists(r"C:\Users\Julien\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output\final.svg"):
#             progress_callback.emit((i/n)*100)
#
#             time.sleep(1)
#             # check for the lastest every sec svg file and took is number
#             while not QFile.exists(rf"C:\Users\Julien\Documents\University\Ete2022\Stage\Code\Working\PhysiCell_V.1.10.1\output\snapshot{convert_in_str(i + 1)}.svg"):
#                 time.sleep(1)
#
#             i += 1
#         return "Done."
#     def print_output(self, s):
#         print(s)
#     def thread_complete(self):
#         print("THREAD COMPLETE!")
#     def oh_no(self):
#         # Pass the function to execute
#         worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
#         worker.signals.result.connect(self.print_output)
#         worker.signals.finished.connect(self.thread_complete)
#         worker.signals.progress.connect(self.progress_fn)
#
#         # Execute
#         self.threadpool.start(worker)
#
#     def recurring_timer(self):
#         self.counter +=1
#         self.l.setText("Counter: %d" % self.counter)
#
#
# app = QApplication(sys.argv)
# window = MainWindow()
# app.exec()