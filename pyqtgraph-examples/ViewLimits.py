import numpy as np

import pyqtgraph as pg

plt = pg.plot(np.random.normal(size=1000), title="View limit example")
plt.centralWidget.vb.setLimits(minXRange=50, maxXRange=100)

if __name__ == '__main__':
    pg.exec()
