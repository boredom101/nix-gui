import re

from PyQt5 import QtWidgets, QtGui, QtCore

from nixui.options import api


class HTMLDelegate(QtWidgets.QStyledItemDelegate):
    def paint(self, painter, option, index):
        style = option.widget.style()
        doc = self._builddoc(option, index)
        option.text = ""
        style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter)
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        textRect = style.subElementRect(QtWidgets.QStyle.SE_ItemViewItemText, option, None)

        self.paint_background(painter, option, index)

        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def paint_background(self, painter, option, index):
        if index is not None:
            item = option.widget.itemFromIndex(index)
            if hasattr(item, 'bg_color'):
                painter.fillRect(option.rect, item.bg_color)

    def sizeHint(self, option, index):
        doc = self._builddoc(option, index)
        return QtCore.QSize(
            doc.idealWidth() + 60,  # TODO: make width the size of the rendered html, right now its too small
            option.decorationSize.height() * 1.5  # hack
        )

    def _builddoc(self, option, index):
        option = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(option, index)
        doc = QtGui.QTextDocument(defaultFont=option.font)
        doc.setHtml(option.text)
        return doc


def get_option_html(option, use_fancy_name=True, child_count=None, type_label=None, description=None, extra_text=None):
    # TODO: 60% and 100% don't work with QT
    no_margin_style = 'margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px'
    sub_style = f'font-style:italic; color:Gray; font-size:60%; {no_margin_style}'

    if use_fancy_name:
        capitalized_fancy_name = re.sub(r"(\w)([A-Z])", r"\1 \2", option.loc[-1]).title()
        s = f'<p style="font-size:100%; {no_margin_style}">{capitalized_fancy_name}</p>'
    else:
        s = f'<p style="font-size:100%; {no_margin_style}">{option}</p>'
    if child_count:
        num_children = len(api.get_option_tree().children(option))
        s += f'<p style="{sub_style}">{option}{" (" + str(num_children) + ")" if num_children else ""}</p>'
    if type_label:
        s += f'<p style="{sub_style}">Type: {type_label}</p>'
    if description:
        s += f'<p style="{sub_style}">Description: {description}</p>'
    if extra_text:
        s += f'<p style="{sub_style}">{extra_text}</p>'
    return s
