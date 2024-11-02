





r3a = pg.RectROI([0,0], [10,10])

x,y = r3a.x(),-r3a.boundingRect().height()
r3_ = pg.RectROI([x,y], [10,10])
r3_.setParentItem(r3a)

r3_.mouseDragEvent = r3a.mouseDragEvent

v3.addItem(r3a)

right_handle_r3a = r3a.addScaleHandle([1, 0], [0, 0], lockAspect=True)
parent_handle = r3a.addScaleHandle([0, 1], [0, 0], lockAspect=True)

right_handle_r3_ = r3_.addScaleHandle([1, 0], [0, 0], lockAspect=True,item=right_handle_r3a)
r3_.addScaleHandle([0, 0], [0, 1], lockAspect=True)