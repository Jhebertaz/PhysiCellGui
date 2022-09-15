from PySide6.QtWidgets import QWidget, QGroupBox, QFormLayout, QScrollArea, QVBoxLayout

class ScrollableWidget(QWidget):
    def __init__(self, *args, **kwargs):
        """
        :param args: whatever
        :param kwargs: key=str, value=QWidget()
        """
        super().__init__(*args)

        self.group_box = QGroupBox()
        self.layout = QVBoxLayout()

        self.group_box.setLayout(self.layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.group_box)
        self.scroll_area.setWidgetResizable(True)
        # scroll.setFixedHeight(200)

        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addWidget(self.scroll_area)
        
        
class ScrollableFormWidget(QWidget):
    def __init__(self, *args, **kwargs):
        """
        :param args: whatever
        :param kwargs: key=str, value=QWidget()
        """
        super().__init__(*args)
        self.group_box = QWidget()
        self.layout = QFormLayout()

        self.group_box.setLayout(self.layout)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.group_box)
        self.scroll_area.setWidgetResizable(True)
        # scroll.setFixedHeight(200)

        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addWidget(self.scroll_area)

        if kwargs:
            for k, v in kwargs.items():
                self.layout.addRow(k, v)

    def add_item(self, row_index=None, label=None, widget=None, **kwargs):
        """
        :param row_index: int
        :param label: str
        :param widget: Qwidget
        :param kwargs: {str: Qwidget}
        :return: None
        """
        preexisting_key = self.ordered_label_list()
        if kwargs:
            if not preexisting_key:
                preexisting_key = list(kwargs.keys())

            for k, v in kwargs.items():

                # verify if prexist
                if k in preexisting_key:
                    row_ = preexisting_key.index(k)

                    # overwrite prexisting row
                    self.overwrite_row(row_,k, v)
                else:
                    self.layout.addRow(k, v)
        else:
            # verify if the label exist
            if label in preexisting_key:
                row_ =  preexisting_key.index(label)
                # overwrite prexisting row
                self.overwrite_row(row_, label, widget)
            else:
                self.layout.addRow(label, widget)


    def ordered_label_list(self):
        if self.layout.rowCount()>0:
            return [self.layout.itemAt(i, QFormLayout.LabelRole).widget().text() for i in range(self.layout.rowCount())]
        return []

    def ordered_widget_list(self):
        if self.layout.rowCount() > 0:
            return [self.layout.itemAt(i, QFormLayout.FieldRole).widget() for i in range(self.layout.rowCount())]
        return []

    def label_widget_dictionary(self):
        if self.layout.rowCount() > 0:
            return {k:v for k,v in zip(self.ordered_label_list(), self.ordered_widget_list())}
        return {}

    def overwrite_row(self, row_index, label, widget):
        self.layout.removeRow(row_index)
        self.layout.insertRow(row_index, label, widget)


