import math
import csv
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from .control import wrap, scan_points, choose_heading

class Navigator(Node):
    def __init__(self):
        super().__init__('navigator')
        defaults = dict(goal_x=0.0, goal_y=0.0, autostart=False, max_speed=0.15,
                        max_turn=0.65, goal_tolerance=0.12, inflation_radius=0.30,
                        lookahead=0.85, data_timeout=0.6, progress_timeout=40.0,
                        lidar_offset_x=0.008059205)

        self.p = {k:self.declare_parameter(k,v).value for k,v in defaults.items()}

        # Lista com os destinos exigidos no enunciado: P1=(1,0), P2=(3,0), P3=(3,2)
        self.waypoints = [(1.0, 0.0), (3.0, 0.0), (3.0, 2.0)]
        self.waypoint_index = 0
        # O objetivo atual será o primeiro ponto da lista caso defina-se autostart=true
        self.goal = self.waypoints[self.waypoint_index] if self.p['autostart'] else None
        
        self.pose = None
        self.scan = None
        self.t= time.monotonic()
        self.odom_time = 0.0
        self.scan_time = 0.0
        self.previous_heading = 0.0
        self.best_distance = math.inf
        self.progress_time = time.monotonic()
        self.state = ''
        self.pub = self.create_publisher(Twist,'/cmd_vel_auto',10)
        self.status = self.create_publisher(String,'/navigation_state',10)
        self.sector = self.create_publisher(String,'/sector_state',1)
        self.create_subscription(Odometry,'/odom',self.on_odom,qos_profile_sensor_data)
        self.create_subscription(LaserScan,'/scan',self.on_scan,qos_profile_sensor_data)
        self.create_subscription(PoseStamped,'/goal_pose',self.on_goal,10)

        #Limpa o arquivo de dados para uma nova rotina
        with open('dados.csv', 'w') as arquivo:
            pass

        self.create_timer(0.1, self.tick)


    def on_odom(self,m):
        p,q = m.pose.pose.position,m.pose.pose.orientation
        values = (p.x,p.y,q.x,q.y,q.z,q.w)
        if m.header.frame_id != 'odom' or not all(math.isfinite(v) for v in values) or sum(v*v for v in (q.x,q.y,q.z,q.w)) < .5:
            return
        yaw = math.atan2(2*(q.w*q.z+q.x*q.y),1-2*(q.y*q.y+q.z*q.z))
        self.pose=(p.x,p.y,yaw)
        self.odom_time=time.monotonic()


    def on_scan(self,m):
        if (m.header.frame_id != 'lidar_link' or not m.ranges
                or not all(math.isfinite(v) for v in (m.angle_min,m.angle_increment,m.range_min,m.range_max))
                or m.angle_increment <= 0 or m.range_max <= m.range_min
                or (len(m.ranges)-1)*m.angle_increment < 3.14):
            return
        self.scan= m
        self.scan_time=time.monotonic()


    def on_goal(self,m):
        if m.header.frame_id != 'odom' or not all(math.isfinite(v) for v in (m.pose.position.x,m.pose.position.y)):
            self.get_logger().warn('Objetivo recusado: use coordenadas finitas no frame odom.')
            return
        self.goal=(m.pose.position.x,m.pose.position.y)
        self.best_distance=math.inf
        self.progress_time=time.monotonic()
        self.previous_heading=0.0


    def command(self,state,v=0.0,w=0.0):
        m=Twist()
        m.linear.x=float(v)
        m.angular.z=float(w)
        self.pub.publish(m)
        self.status.publish(String(data=state))
        if state!=self.state:
            self.get_logger().info(state)
            self.state=state

    def log_sector(self,state):
            self.sector.publish(String(data=state))
            if state!=self.state:
                self.get_logger().info(state);self.state=state


    def salvar_dados(self):
        with open('dados.csv', mode= 'a', newline='', encoding='utf-8') as arquivo:
            escritor= csv.writer(arquivo)
            #[tempo, p_x, p_y, p_yaw, goal_x, goal_y, log_state]
            escritor.writerow([self.t, self.pose[0], self.pose[1], self.pose[2], self.goal[0], self.goal[1], self.state])




    def tick(self):
        now=time.monotonic()
        self.t= now

        if self.goal is None:
            self.command('AGUARDANDO_OBJETIVO')
            return
        
        if self.pose is None or self.scan is None or max(now-self.odom_time,now-self.scan_time)>self.p['data_timeout']:
            self.command('SEM_DADOS_ATUAIS')
            return

        #-------Organização dos pontos objetivos------
        x, y, yaw = self.pose
        dx, dy = self.goal[0]-x ,self.goal[1]-y
        rho = math.hypot(dx,dy)
        if rho < self.p['goal_tolerance']:
            p_atual = self.waypoints[self.waypoint_index]
            self.get_logger().info(f'Chegou ao destino P{self.waypoint_index + 1}: {p_atual}')
            
            # Reinicializa os indicadores internos conforme exigido na Questão 3.b
            self.best_distance = math.inf
            self.progress_time = now
            self.previous_heading = 0.0
            
            # Avança para o próximo waypoint
            self.waypoint_index += 1
            
            if self.waypoint_index < len(self.waypoints):
                self.goal = self.waypoints[self.waypoint_index]
            else: # Fim da missão
                self.goal = None
                self.command('MISSAO_CONCLUIDA', 0.0, 0.0)
            return
        
        if rho < self.best_distance-0.04:
            self.best_distance = rho
            self.progress_time = now

        if now-self.progress_time > self.p['progress_timeout']:
            self.command('SEM_PROGRESSO_REENVIE_OBJETIVO')
            self.goal=None
            return
        
        m = self.scan
        points, valid = scan_points(m.ranges,m.angle_min,m.angle_increment,m.range_min,m.range_max,self.p['lidar_offset_x'])
        if valid < 0.95:
            self.command('SCAN_INVALIDO')
            return
        desired = wrap(math.atan2(dy,dx)-yaw)
        heading, msg = choose_heading(points,desired,min(self.p['lookahead'],rho),self.p['inflation_radius'],self.previous_heading)
        self.log_sector(" | ".join(msg))

        if heading is None:
            self.command('BLOQUEADO')
            return
        
        self.previous_heading = heading
        w = max(-self.p['max_turn'],min(self.p['max_turn'],1.5*heading))
        v = min(self.p['max_speed'],.5*rho)*max(0.0,math.cos(heading))
        if abs(heading)>0.45: v=0.0
        self.command('DESVIANDO' if abs(wrap(heading-desired))>.1 else 'INDO_AO_PONTO',v,w)

        self.salvar_dados()

def main():
    rclpy.init();n=Navigator()
    try:rclpy.spin(n)
    except KeyboardInterrupt:pass
    finally:
        if rclpy.ok():n.command('PARADO');n.destroy_node();rclpy.shutdown()