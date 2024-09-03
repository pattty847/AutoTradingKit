# PySide6_VerticalQTabWidget
Vertical QTabWidget for PySide6

## Requirements
PySide6 >= 6.4

## Setup
`python -m pip install PySide6_VerticalQTabWidget`

## Usage
```python
from PySide6.QtWidgets import QWidget
from PySide6_VerticalQTabWidget import VerticalQTabWidget

vertical_tab_widget = VerticalQTabWidget()
widget1 = QWidget()
widget2 = QWidget()
vertical_tab_widget.addTab(widget1, "First Tab")
vertical_tab_widget.addTab(widget2, "Second Tab")
```
## Acknowledge
[yjg30737]<br>
[Ortham’s Software Notes]

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [yjg30737]: https://github.com/yjg30737/pyqt-vertical-tab-widget
   [Ortham’s Software Notes]: https://ortham.github.io/2022/01/15/qt-vertical-tabs.html