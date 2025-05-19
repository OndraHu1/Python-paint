import os
import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QColor
from PyQt6.QtCore import Qt, QPoint, QRect

from paint_app import PaintApp
from paint_canvas import PaintCanvas
from tools import ToolType

# Nastavení aplikace pro testy
@pytest.fixture
def app():
    return QApplication(sys.argv)

@pytest.fixture
def paint_app(app):
    return PaintApp()

@pytest.fixture
def paint_canvas(app):
    return PaintCanvas()

# Testy základních funkcí
def test_init_canvas(paint_canvas):
    """Test, že plátno je správně inicializováno"""
    assert paint_canvas.image is not None
    assert paint_canvas.image.width() == 1000
    assert paint_canvas.image.height() == 800
    
    # Kontrola, že plátno je bílé
    assert paint_canvas.image.pixelColor(0, 0) == QColor(Qt.GlobalColor.white)

def test_set_pen_color(paint_canvas):
    """Test, že nastavení barvy pera funguje správně"""
    test_color = QColor(255, 0, 0)  # Červená
    paint_canvas.set_pen_color(test_color)
    assert paint_canvas.pen_color == test_color

def test_set_pen_width(paint_canvas):
    """Test, že nastavení tloušťky pera funguje správně"""
    test_width = 10
    paint_canvas.set_pen_width(test_width)
    assert paint_canvas.pen_width == test_width

def test_set_tool(paint_canvas):
    """Test, že nastavení nástroje funguje správně"""
    paint_canvas.set_tool(ToolType.BRUSH)
    assert paint_canvas.current_tool == ToolType.BRUSH
    
    paint_canvas.set_tool(ToolType.ERASER)
    assert paint_canvas.current_tool == ToolType.ERASER

def test_undo_redo(paint_canvas, monkeypatch):
    """Test, že funkce zpět a znovu fungují správně"""
    # Monkeypatch pro simulaci kreslení na plátno
    def mock_add_to_history():
        paint_canvas.history.append(paint_canvas.image.copy())
        paint_canvas.history_index += 1
    
    monkeypatch.setattr(paint_canvas, "add_to_history", mock_add_to_history)
    
    # Vytvoření počátečního stavu
    initial_image = paint_canvas.image.copy()
    
    # Simulace kreslení - změníme barvu pixelu
    paint_canvas.image.setPixelColor(10, 10, QColor(255, 0, 0))
    mock_add_to_history()
    
    # Simulace druhé změny
    paint_canvas.image.setPixelColor(20, 20, QColor(0, 255, 0))
    mock_add_to_history()
    
    # Test undo
    paint_canvas.undo()
    assert paint_canvas.image.pixelColor(20, 20) != QColor(0, 255, 0)
    assert paint_canvas.image.pixelColor(10, 10) == QColor(255, 0, 0)
    
    # Test druhého undo
    paint_canvas.undo()
    assert paint_canvas.image.pixelColor(10, 10) != QColor(255, 0, 0)
    
    # Test redo
    paint_canvas.redo()
    assert paint_canvas.image.pixelColor(10, 10) == QColor(255, 0, 0)
    
    # Test druhého redo
    paint_canvas.redo()
    assert paint_canvas.image.pixelColor(20, 20) == QColor(0, 255, 0)

def test_clear(paint_canvas):
    """Test, že vyčištění plátna funguje správně"""
    # Změna barvy pixelu
    paint_canvas.image.setPixelColor(10, 10, QColor(255, 0, 0))
    
    # Vyčištění plátna
    paint_canvas.clear()
    
    # Kontrola, že plátno je bílé
    assert paint_canvas.image.pixelColor(10, 10) == QColor(Qt.GlobalColor.white)

def test_resize_canvas(paint_canvas):
    """Test, že změna velikosti plátna funguje správně"""
    # Nakreslení něčeho na plátno
    paint_canvas.image.setPixelColor(10, 10, QColor(255, 0, 0))
    
    # Změna velikosti plátna
    new_width = 800
    new_height = 600
    paint_canvas.resize_canvas(new_width, new_height)
    
    # Kontrola nové velikosti
    assert paint_canvas.image.width() == new_width
    assert paint_canvas.image.height() == new_height
    
    # Kontrola, že obsah byl zachován
    assert paint_canvas.image.pixelColor(10, 10) == QColor(255, 0, 0)

def test_zoom(paint_canvas):
    """Test, že zoom funguje správně"""
    # Počáteční zoom
    assert paint_canvas.zoom_factor == 1.0
    
    # Přiblížení
    paint_canvas.zoom_in()
    assert paint_canvas.zoom_factor > 1.0
    
    # Oddálení
    paint_canvas.zoom_out()
    paint_canvas.zoom_out()
    assert paint_canvas.zoom_factor < 1.0
    
    # Reset zoomu
    paint_canvas.reset_zoom()
    assert paint_canvas.zoom_factor == 1.0

def test_save_and_load_image(paint_canvas, tmp_path):
    """Test, že ukládání a načítání obrázků funguje správně"""
    # Nakreslení něčeho na plátno
    paint_canvas.image.setPixelColor(10, 10, QColor(255, 0, 0))
    paint_canvas.image.setPixelColor(20, 20, QColor(0, 255, 0))
    
    # Uložení do dočasného souboru
    temp_file = str(tmp_path / "test_image.png")
    paint_canvas.save_image(temp_file)
    
    # Kontrola, že soubor existuje
    assert os.path.exists(temp_file)
    
    # Vyčištění plátna
    paint_canvas.clear()
    assert paint_canvas.image.pixelColor(10, 10) == QColor(Qt.GlobalColor.white)
    
    # Načtení obrázku
    paint_canvas.load_image(temp_file)
    
    # Kontrola, že obsah byl načten správně
    assert paint_canvas.image.pixelColor(10, 10) == QColor(255, 0, 0)
    assert paint_canvas.image.pixelColor(20, 20) == QColor(0, 255, 0)

# Test integrace - hlavní aplikace a plátno
def test_app_integration(paint_app):
    """Test, že hlavní aplikace a plátno jsou správně propojeny"""
    # Kontrola, že plátno existuje
    assert paint_app.canvas is not None
    
    # Nastavení barvy v hlavní aplikaci
    test_color = QColor(0, 0, 255)  # Modrá
    paint_app.set_color(test_color)
    
    # Kontrola, že barva byla nastavena i v plátně
    assert paint_app.canvas.pen_color == test_color