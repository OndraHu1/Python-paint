import pytest
from tools import ToolType

def test_tool_types():
    """Test, že všechny typy nástrojů existují a jsou unikátní"""
    tools = [
        ToolType.PENCIL,
        ToolType.BRUSH,
        ToolType.ERASER,
        ToolType.LINE,
        ToolType.RECTANGLE,
        ToolType.ELLIPSE,
        ToolType.FILL,
        ToolType.SELECT
    ]
    
    # Kontrola, že každý nástroj je jiný (unikátní enumerace)
    assert len(tools) == len(set(tools))
    
    # Kontrola, že všechny nástroje jsou instance ToolType
    for tool in tools:
        assert isinstance(tool, ToolType)