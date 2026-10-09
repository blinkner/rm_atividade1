import time,rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from geometry_msgs.msg import Twist,PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from rm_bot_aula04.command_gate import CommandGate
from rm_bot_aula04.navigator import Navigator
rclpy.init();gate=CommandGate();nav=Navigator();probe=Node('probe');ex=SingleThreadedExecutor()
for n in [gate,nav,probe]:ex.add_node(n)
latest={}
def cb(m,k):latest[k]=m
s1=probe.create_subscription(Twist,'/cmd_vel',lambda m:cb(m,'gate'),10)
s2=probe.create_subscription(Twist,'/cmd_vel_auto',lambda m:cb(m,'auto'),10)
p=probe.create_publisher(Twist,'/cmd_vel_manual',10)
def spin(sec):
 end=time.monotonic()+sec
 while time.monotonic()<end:ex.spin_once(timeout_sec=.02)
spin(.5);m=Twist();m.linear.x=.1;p.publish(m);spin(.2);assert latest['gate'].linear.x==.1
spin(.7);assert latest['gate'].linear.x==0
scan=LaserScan();scan.header.frame_id='lidar_link';scan.angle_increment=.01;scan.range_min=.02;scan.range_max=12.;scan.ranges=[float('inf')]*630
odom=Odometry();odom.header.frame_id='odom';odom.pose.pose.orientation.w=1.
goal=PoseStamped();goal.header.frame_id='odom';goal.pose.position.x=3.;nav.on_goal(goal);nav.on_odom(odom);nav.on_scan(scan);spin(.2);assert latest['auto'].linear.x>0
spin(.7);assert latest['auto'].linear.x==0 and latest['auto'].angular.z==0
print('PASS: command_gate para por timeout; navigator para por sensores/odom antigos.')
for n in [gate,nav,probe]:n.destroy_node()
rclpy.shutdown()
