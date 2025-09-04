from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig

import mpmath
from decimal import Decimal
import re

# 设置默认精度
mpmath.mp.dps = 100

@register(
    "astrbot_plugin_mathitools",
    "FDMNya~",
    "增加较为简单的高精度数学运算工具",
    "2.1.0",
    "https://github.com/fudengming/astrbot_plugin_mathitools "
)
class Mathitools(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        mpmath.mp.dps = config.get("dps", 50)
        logger.info(f"精度(dps)已设置为{mpmath.mp.dps}")

    async def initialize(self):
        logger.info("Mathitools 插件已加载")

    def _safe_eval_expr(self, expr: str) -> mpmath.mpf:
        """
        安全地解析并计算数学表达式，使用 mpmath 支持高精度
        """
        # 预处理：替换 ^ 为 **
        expr = expr.replace('^', '**')
        # 简单的安全检查：只允许数字、括号、基本运算符和函数名
        if not re.match(r'^[0-9+\-*/().,eE \t\[\]{}a-df-zA-DF-Z_°]*$', expr):
            raise ValueError("表达式包含非法字符")

        # 使用 mpmath 计算表达式
        try:
            # 自定义命名空间
            namespace = {
                'pi': mpmath.pi,
                'e': mpmath.e,
                'sqrt': mpmath.sqrt,
                'cbrt': mpmath.cbrt,
                'root': lambda x, n: mpmath.power(x, 1/n),
                'pow': mpmath.power,
                'log': mpmath.log,
                'ln': mpmath.ln,
                'sin': mpmath.sin,
                'cos': mpmath.cos,
                'tan': mpmath.tan,
                'deg': lambda x: mpmath.mpf(x) * mpmath.pi / 180,
                # 更多函数可扩展
            }
            # 将整数/小数字符串转为 mpmath.mpf
            result = eval(expr, {"__builtins__": {}}, namespace)
            return mpmath.mpf(result)
        except Exception as e:
            raise ValueError(f"表达式计算失败: {str(e)}")

    @filter.llm_tool(name="expression")
    async def expression(self, event: AstrMessageEvent, expression: str) -> MessageEventResult:
        '''
        计算数学表达式，支持高精度大数与浮点运算。

        当前支持的运算符及其含义：
        - "+"  : 两数相加
        - "-"  : 两数相减
        - "*"  : 两数相乘
        - "/"  : 两数相除（支持高精度小数）
        - "**" : 幂运算（如 2**10 表示 2 的 10 次方）
        - "^"  : 幂运算（等同于 **，更自然的输入方式）
        - "%"  : 取模运算（求余数）
        - "//" : 整除运算（向下取整除法的近似）
        - "()" : 括号，用于改变运算优先级，支持嵌套
        - "sqrt(x)" : 计算 x 的平方根
        - "root(x, n)": 计算 x 的 n 次方根（如 root(8, 3)：计算8的3次方）
        - "pi" : 圆周率 π（约 3.14159...）
        - "e"  : 自然常数 e（约 2.71828...）
        - "log(x)" : 以 e 为底的对数（即 ln）
        - "sin(x)", "cos(x)", "tan(x)" : 三角函数（输入为弧度，若需要计算角度制的三角函数，请先使用deg进行转换）
        - "deg(x)" : 将角度 x 转换为弧度（如 deg(45)：将角度45度转换为弧度）

        Args:
            expression(string): 数学表达式字符串
        '''
        try:
            result = self._safe_eval_expr(expression.strip())
            if mpmath.isint(result):
                return f"{int(result)}"
            else:
                return mpmath.nstr(result, n=50, strip_zeros=True)
        except Exception as e:
            return f"计算出错：{str(e)}"

    @filter.llm_tool(name="compare")
    async def compare(self, event: AstrMessageEvent, expression1: str, expression2: str) -> MessageEventResult:
        '''
        比较两个数学表达式的大小，支持高精度数值比较。

        将分别计算 expression1 和 expression2 的值，并返回它们的大小关系。
        支持所有 expression 工具中的运算符和函数。

        Args:
            expression1(string): 第一个数学表达式
            expression2(string): 第二个数学表达式
        '''
        try:
            val1 = self._safe_eval_expr(expression1.strip())
            val2 = self._safe_eval_expr(expression2.strip())

            if val1 < val2:
                return f"expression1({val1}) 小于 expression2({val2})"
            elif val1 > val2:
                return f"expression1({val1}) 大于 expression2({val2})"
            else:
                return f"expression1({val1}) 等于 expression2({val2})"
        except Exception as e:
            return f"比较出错：{str(e)}"