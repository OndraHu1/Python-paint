from enum import Enum, auto

class ToolType(Enum):
    PENCIL = auto()
    BRUSH = auto()
    ERASER = auto()
    TEXT = auto()
    LINE = auto()
    RECTANGLE = auto()
    ROUNDED_RECT = auto()
    ELLIPSE = auto()
    TRIANGLE = auto()
    PENTAGON = auto()
    HEXAGON = auto()
    STAR = auto()
    ARROW = auto()
    FILL = auto()
    SELECT = auto()
    
class ThemeType(Enum):
    LIGHT = auto()
    DARK = auto()