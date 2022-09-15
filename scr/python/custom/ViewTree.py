#############
## Package ##
#############
from PySide6.QtWidgets import QTreeWidgetItem, QInputDialog, QTreeWidget


class ViewTree(QTreeWidget):
    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fill_item(self.invisibleRootItem(), value)
        self.modify_element_path_value_list_dict = []
        self.doubleClicked.connect(self.edit_and_store_path_value_dict)

    def edit_and_store_path_value_dict(self):
        ok = bool()
        if not ViewTree.is_sub_tree(self.selectedItems()[0]):
            text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter your name:')

            if ok and text:
                path_value_dict = ViewTree.modify_element(self.selectedItems()[0], text)

                if path_value_dict:
                    if self.modify_element_path_value_list_dict:
                        if path_value_dict == self.modify_element_path_value_list_dict[-1]:
                            return

                        else:
                            self.modify_element_path_value_list_dict.append(path_value_dict)
                            return
                    else:
                        self.modify_element_path_value_list_dict.append(path_value_dict)
                        return
    @staticmethod
    def modify_element(qtreewidgetitem, new_value):
        # get the current item
        si = qtreewidgetitem
        # verify if it has a child
        if not ViewTree.is_sub_tree(si):
            if new_value:
                si.setText(0, new_value)
            return ViewTree.current_item_path_value_dict(qtreewidgetitem)
        else:
            print("selected item have one or multiple child")
    @staticmethod
    def is_sub_tree(qtreewidgetitem):

        if qtreewidgetitem.childCount()>=1:
            return True
        else:
            return False
    @staticmethod
    def current_item_path_value_dict(qtreewidgetitem):
        path = []
        #.currentItem() for QTreeWidget
        si = qtreewidgetitem
        while si.parent():
            parent_child_count = si.parent().childCount()
            if parent_child_count>1:
                tmp = []
                uniqueness = True

                # verify if their names are different
                for i in range(parent_child_count):
                    child_name = si.parent().child(i).text(0)

                    if child_name in tmp:
                        uniqueness = False

                    tmp.append(child_name)

                if not uniqueness:
                    path.append(si.parent().indexOfChild(si))

                else:
                    path.append(si.text(0))
            else:
                path.append(si.text(0))
            si = si.parent()

        path.append(si.text(0))
        path.reverse()

        return {'path':path[:-1:], 'value':path[-1]}
    @staticmethod
    def fill_item(item: QTreeWidgetItem, value):
        if value is None:
            return
        elif isinstance(value, dict):
            for key, val in sorted(value.items()):
                ViewTree.new_item(item, str(key), val)
        elif isinstance(value, (list, tuple)):
            for val in value:
                if isinstance(val, (str, int, float)):
                    ViewTree.new_item(item, str(val))
                else:
                    ViewTree.new_item(item, f"[{type(val).__name__}]", val)
        else:
            ViewTree.new_item(item, str(value))
    @staticmethod
    def new_item(parent: QTreeWidgetItem, text:str, val=None):
        child = QTreeWidgetItem([text])
        ViewTree.fill_item(child, val)
        parent.addChild(child)
        child.setExpanded(True)