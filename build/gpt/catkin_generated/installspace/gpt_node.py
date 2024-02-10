import rospy
from std_msgs.msg import String
from openai import OpenAI

class ChatGPTNode:
    def __init__(self):
        rospy.init_node("chatgpt_node")
        self.conversation = rospy.get_param('~openai/conversation', '~prompt/conversation')
        self.sysprompt=rospy.get_param('~prompt/sysprompt')
        self.chat_history =[
    {
        "role": "system",
        "content": sysprompt
    },
    {
        "role": "user",
        "content": "向前移动,以速度10"
    },
    {
        "role": "assistant",
        "content": """```python
tn.run_forward(linear_x)
```
This code uses the `run_forward()` function to move the turtle."""
    }
]
        self.question_sub = rospy.Subscriber("/wpr_ask", String, self.gpt_feedback, queue_size=1)
        self.response_pub = rospy.Publisher("/chatspt_answer", String, queue_size=1)
        rospy.logwarn("ChatGPT:向我提问")
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
            api_key='sk-AAcqVh7Cn1hC8Rhaiv6nL59R2WSUNz6UTZzmUhN6qgHXOCq7',
        )
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.chat_history,
            temperature=0
        )
        response = completion.choices[0].message.content
        #rospy.logwarn(response)
        if self.conversation:
            self.chat_history.append({
                "role": "assistant",
                "content": response,
            })
            self.response_pub.publish(response)

if __name__ == "__main__":
    ChatGPTNode()
