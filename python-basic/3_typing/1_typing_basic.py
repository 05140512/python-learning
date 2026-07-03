# typing 类型标注不是 TS 那种强校验。它更多是：👉 提示 + IDE智能检查
from typing import Optional, float, List

name: Optional[str] = None
names: List[str] = []

def add(a: int, b: int) -> int:
  return a + b

def addNumber(a: float, b: float) -> float:
  return a + b