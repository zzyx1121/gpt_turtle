import rospy
from std_msgs.msg import String
from openai import OpenAI
import re
from geometry_msgs.msg import Twist

class TurtleNode:
    def __init__(self):
        self.answer_pub= rospy.Publisher("/turtle1/cmd_vel", Twist, queue_size=10)
    def forward(self,x):
        twist_msg = Twist()
        twist_msg.linear.x = 1
        twist_msg.linear.y =  0
        twist_msg.linear.z =  0
        twist_msg.angular.x = 0
        twist_msg.angular.y = 0
        twist_msg.angular.z = 0
        self.answer_pub.publish(twist_msg)
    def backward(self,x):
        twist_msg = Twist()
        twist_msg.linear.x = -1
        twist_msg.linear.y = 0
        twist_msg.linear.z =  0
        twist_msg.angular.x = 0
        twist_msg.angular.y = 0
        twist_msg.angular.z = 0
        self.answer_pub.publish(twist_msg)
    def right(self,x):
        twist_msg = Twist()
        twist_msg.linear.x = 0
        twist_msg.linear.y = -1
        twist_msg.linear.z =  0
        twist_msg.angular.x = 0
        twist_msg.angular.y = 0
        twist_msg.angular.z = 0
        self.answer_pub.publish(twist_msg)
    def left(self,x):
        twist_msg = Twist()
        twist_msg.linear.x = 0
        twist_msg.linear.y = 1
        twist_msg.linear.z =  0
        twist_msg.angular.x = 0
        twist_msg.angular.y = 0
        twist_msg.angular.z = 0
        self.answer_pub.publish(twist_msg)
class ChatGPTNode:
    def __init__(self):
        rospy.init_node("chatgpt_node")
        self.tn=TurtleNode()
        self.conversation = rospy.get_param('openai/conversation', 'prompt/conversation')
        self.chat_history =[
    {
        "role": "system",
        "content": """  
        You are an assistant helping me to control the turtle
  	When I ask you to do something, you are supposed to give me Python code that is needed to achieve that task and then an explanation of what that code does.
 	You are only allowed to use the functions I have defined for you.
  	You are not to use any other hypothetical functions that you think might exist."""
    },
    {
        "role": "user",
        "content": "向前移动"
    },
    {
        "role": "assistant",
        "content": """```python
tn.forward()
```
This code uses the `forward()` function to move the turtle. """
    }
]
        self.question_sub = rospy.Subscriber("/wpr_ask", String, self.gpt_feedback, queue_size=1)
        self.response_pub = rospy.Publisher("/chatgpt_answer", String, queue_size=1)
        rospy.logwarn("ChatGPT:发出指令")
        rospy.spin()

    def gpt_feedback(self, msg):
        rospy.loginfo(msg.data)
        if self.conversation:
            self.chat_history.append({
                "role": "user",
                "content": msg.data,
            })
        else:
            self.chat_history = [{
                "role": "user",
                "content": msg.data,
            }]
        client = OpenAI(
            base_url='https://api.openai-proxy.org/v1',
            api_key='',
        )
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.chat_history,
            temperature=0
        )
        response = completion.choices[0].message.content
        rospy.logwarn(response)
        if self.conversation:
            self.chat_history.append({
                "role": "assistant",
                "content": response,
            })
            
        code_block_regex = re.compile(r"```(.*?)```", re.DOTALL)
        code_blocks = code_block_regex.findall(response) #这里得到了chatgpt给的代码
        if code_blocks:
            full_code = "\n".join(code_blocks)
           
            if full_code.startswith("python"):
                full_code = full_code[7:]
                rospy.loginfo('所有代码:%s',full_code)
                exec(full_code, globals(), {'tn': self.tn})
        else:
            return None
        rospy.loginfo("done")

if __name__ == "__main__":
    ChatGPTNode()
