"""Uma única saída /cmd_vel; parada quando os comandos ficam antigos."""
import math,time
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
class CommandGate(Node):
    def __init__(self):
        super().__init__('command_gate')
        mode=self.declare_parameter('mode','manual').value
        if mode not in ('manual','auto'):raise ValueError('mode deve ser manual ou auto')
        self.timeout=self.declare_parameter('timeout',.5).value
        self.last=0.;self.cmd=Twist()
        self.pub=self.create_publisher(Twist,'/cmd_vel',10)
        self.create_subscription(Twist,'/cmd_vel_'+mode,self.receive,10)
        self.create_timer(.05,self.tick)
    def receive(self,m):
        if not all(math.isfinite(v) for v in [m.linear.x,m.angular.z]):
            self.cmd=Twist();self.last=0.;return
        self.cmd=Twist();self.cmd.linear.x=max(-.15,min(.15,m.linear.x))
        self.cmd.angular.z=max(-.65,min(.65,m.angular.z));self.last=time.monotonic()
    def tick(self):self.pub.publish(self.cmd if time.monotonic()-self.last<self.timeout else Twist())
    
def main():
    rclpy.init();n=CommandGate()
    try:rclpy.spin(n)
    except KeyboardInterrupt:pass
    finally:
        if rclpy.ok():n.pub.publish(Twist());n.destroy_node();rclpy.shutdown()
