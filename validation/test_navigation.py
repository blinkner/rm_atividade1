import rclpy,time,json,math
from geometry_msgs.msg import PoseStamped,Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from rclpy.qos import qos_profile_sensor_data
rclpy.init();n=rclpy.create_node('test_aula04');d={'states':[],'samples':[],'counts':{}};pose=None;done=False
subs=[]
def odom(m):
 global pose
 pose=[m.pose.pose.position.x,m.pose.pose.position.y]
def state(m):
 global done
 if not d['states'] or d['states'][-1]!=m.data:d['states'].append(m.data)
 if m.data=='CHEGOU':done=True
subs.append(n.create_subscription(Odometry,'/odom',odom,qos_profile_sensor_data));subs.append(n.create_subscription(String,'/navigation_state',state,10))
for t in ['/scan','/ultrasonic/front/scan','/ultrasonic/left/scan','/ultrasonic/right/scan']:
 def cb(m,t=t):d['counts'][t]=d['counts'].get(t,0)+1
 subs.append(n.create_subscription(LaserScan,t,cb,qos_profile_sensor_data))
pub=n.create_publisher(PoseStamped,'/goal_pose',10)
end=time.monotonic()+5
while time.monotonic()<end:rclpy.spin_once(n,timeout_sec=.1)
m=PoseStamped();m.header.frame_id='odom';m.pose.position.x=3.;m.pose.orientation.w=1.;pub.publish(m)
start=time.monotonic();sample=start
while time.monotonic()-start<100 and not done:
 rclpy.spin_once(n,timeout_sec=.1)
 if time.monotonic()-sample>1:
  sample=time.monotonic();d['samples'].append({'t':sample-start,'pose':pose})
d.update(reached=done,elapsed=time.monotonic()-start,final_pose=pose)
open('validation/navigation_result.json','w').write(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k!='samples'},indent=2))
n.destroy_node();rclpy.shutdown()
