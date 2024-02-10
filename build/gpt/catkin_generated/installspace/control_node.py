import rospy
from geometry_msgs.msg import Twist
import re
class TurtleNode:
    def __init__(self):
        self.answer_pub= rospy.Publisher("/turtle1/cmd_vel", Twist, queue_size=10)
    def run_forward(self,linear_x):
        twist_msg = Twist()
        twist_msg.linear.x = float(linear_x)
        twist_msg.linear.y =  0
        twist_msg.linear.z =  0
        twist_msg.angular.x = 0
        twist_msg.angular.y = 0
        twist_msg.angular.z = 0
        self.answer_pub.publish(twist_msg)
    def cross_motion(self,linear_y):
        twist_msg = Twist()
        twist_msg.linear.x = 0
        twist_msg.linear.y = linear_y
        twist_msg.linear.z =  0
        twist_msg.angular.x = 0
        twist_msg.angular.y = 0
        twist_msg.angular.z = 0
        self.answer_pub.publish(twist_msg)
class ControlNode:
    def __init__(self):
        rospy.init_node("control_node")
        tn=TurtleNode()
        self.answer_sub=rospy.Subscriber("/chatspt_answer", String,self.feedback,queue_size=1)
    def feedback(self,msg):
        code_block_regex = re.compile(r"```(.*?)```", re.DOTALL)
        code_blocks = code_block_regex.findall(msg.data) #这里得到了chatgpt给的代码
        if code_blocks:
            full_code = "\n".join(code_blocks)
            print('所有代码:',full_code)
            if full_code.startswith("python"):
                full_code = full_code[7:]
                return full_code #返回python代码
        else:
            return None
