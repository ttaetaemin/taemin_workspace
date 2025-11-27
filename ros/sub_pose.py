#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class PoseSub(Node):
    def __init__(self):
        super().__init__('sub_test')
        # 구독자 객체를 인스턴스 변수로 보관해야 함!
        self.sub = self.create_subscription(
            Pose, '/turtle1/pose', self.cb_pose, 10
        )

    def cb_pose(self, msg: Pose):
        self.get_logger().info(f'x={msg.x:.2f}, y={msg.y:.2f}, th={msg.theta:.2f}')

def main():
    rclpy.init()
    node = PoseSub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
