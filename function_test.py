import sys
import math
import time
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QBrush, QPen, QColor, QKeyEvent

class CircleBall(QGraphicsView):
    def __init__(self):
        super().__init__()

        # Tạo một cảnh (scene) để vẽ vòng tròn và bi
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        # Vẽ vòng tròn
        self.circle_radius = 100
        self.circle = QGraphicsEllipseItem(-self.circle_radius, -self.circle_radius, 
                                           self.circle_radius * 2, self.circle_radius * 2)
        self.circle.setPen(QPen(Qt.black, 2))
        self.scene.addItem(self.circle)

        # Vẽ bi màu xanh
        self.ball_radius = 10
        self.ball = QGraphicsEllipseItem(-self.ball_radius, -self.ball_radius, 
                                         self.ball_radius * 2, self.ball_radius * 2)
        self.ball.setBrush(QBrush(QColor("blue")))
        self.scene.addItem(self.ball)

        # Vẽ một điểm cố định bất kỳ trên vòng tròn
        self.fixed_point_radius = 5
        self.fixed_angle = math.pi / 4  # Chọn vị trí cố định tại góc 45 độ
        fixed_x = self.circle_radius * math.cos(self.fixed_angle)
        fixed_y = self.circle_radius * math.sin(self.fixed_angle)
        self.fixed_point = QGraphicsEllipseItem(-self.fixed_point_radius, -self.fixed_point_radius,
                                                self.fixed_point_radius * 2, self.fixed_point_radius * 2)
        self.fixed_point.setBrush(QBrush(QColor("red")))
        self.fixed_point.setPos(QPointF(fixed_x, fixed_y))
        self.scene.addItem(self.fixed_point)

        # Biến thời gian và tốc độ góc
        self.angle = 0
        self.angular_velocity = 0.05  # Tốc độ góc

        # Cập nhật vị trí của bi mỗi 20ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(20)

        # Biến để lưu thời gian viên bi đi qua chính giữa điểm cố định
        self.last_passed_time = None

    def update_position(self):
        # Tính toán vị trí của bi trên đường tròn
        x = self.circle_radius * math.cos(self.angle)
        y = self.circle_radius * math.sin(self.angle)

        # Cập nhật vị trí của bi
        self.ball.setPos(QPointF(x, y))

        # Kiểm tra xem bi có chạy qua điểm cố định không
        self.check_ball_passed_fixed_point(x, y)

        # Tăng góc theo tốc độ góc
        self.angle += self.angular_velocity

    def check_ball_passed_fixed_point(self, x, y):
        # Lấy tọa độ của điểm cố định
        fixed_x = self.circle_radius * math.cos(self.fixed_angle)
        fixed_y = self.circle_radius * math.sin(self.fixed_angle)

        # Tính khoảng cách giữa bi và điểm cố định
        distance = math.sqrt((x - fixed_x) ** 2 + (y - fixed_y) ** 2)

        # Chỉ lưu thời gian khi bi chạy qua chính giữa điểm cố định
        if distance < self.ball_radius / 2:  # Giả sử chính giữa là khi khoảng cách nhỏ hơn bán kính của bi
            current_time_ms = int(time.time() * 1000)  # Thời gian hiện tại tính theo ms
            self.last_passed_time = current_time_ms  # Lưu lại thời gian này
            print(f"Vừa chạy qua lúc {current_time_ms} ms")

    def keyPressEvent(self, event: QKeyEvent):
        # Kiểm tra khi nhấn phím Z, X, C
        if event.key() == Qt.Key_Z:
            self.print_time('Z')
        elif event.key() == Qt.Key_X:
            self.print_time('X')
        elif event.key() == Qt.Key_C:
            self.print_time('C')

    def print_time(self, key):
        # In ra thời gian khi nhấn phím
        current_time_ms = int(time.time() * 1000)  # Lấy thời gian hiện tại theo ms
        print(f"Phím {key} được nhấn lúc {current_time_ms} ms")

        # Tính toán độ lệch thời gian nếu viên bi đã đi qua điểm cố định
        if self.last_passed_time is not None:
            time_diff = abs(current_time_ms - self.last_passed_time)
            print(f"Độ lệch thời gian giữa lúc ấn phím và viên bi chạy qua: {time_diff} ms")

# Chạy ứng dụng
app = QApplication(sys.argv)
window = CircleBall()
window.show()
sys.exit(app.exec())
