from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import numexpr as ne

@register(
    "astrbot_plugin_mathitools", 
    "FDMNya~", 
    "增加数学运算工具", 
    "1.0.0", 
    "https://github.com/fudengming/astrbot_plugin_mathitools"
)
class Mathitools(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    @filter.llm_tool(name="expression")
    async def expression(self, event: AstrMessageEvent, expression: str) -> MessageEventResult:
        '''计算数学表达式
        当前可用的运算符：
        "*" 表示两数相乘
        "/" 表示两数相除
        "-" 表示两数相减
        "+" 表示两数相加
        "**" 表示冥运算
        "%" 表示取模运算

        Args:
            expression(string): 数学表达式
        '''
        return str(ne.evaluate(expression))

    @filter.llm_tool(name="compare")
    async def compare(self, event: AstrMessageEvent, expression1: str, expression2: str) -> MessageEventResult:
        '''比较两个数学表达式的大小

        Args:
            expression1(string): 第一个数字表达式
            expression2(string): 第二个数字表达式

        '''
        return (
            f"expression1({ne.evaluate(expression1)})小于expression2({ne.evaluate(expression2)})" 
            if 
            ne.evaluate(f"{expression1}<{expression2}") 
            else (
                f"expression1({ne.evaluate(expression1)})大于expression2({ne.evaluate(expression2)})" 
                if ne.evaluate(f"{expression1}>{expression2}") 
                else 
                f"expression1({ne.evaluate(expression1)})等于expression2({ne.evaluate(expression2)})"
            )
        )

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""