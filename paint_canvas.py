from PyQt6.QtWidgets import (QWidget, QInputDialog, QMessageBox, QTextEdit)
from PyQt6.QtGui import (QPainter, QPen, QColor, QPixmap, QImage, QPolygon, QFont, QFontMetrics, 
                        QPainterPath, QMouseEvent, QTextCursor, QTransform, QPolygonF)
from PyQt6.QtCore import Qt, QPoint, QPointF, QRect, QSize, QLine, pyqtSignal
import numpy as np

from tools import ToolType

class PaintCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Inicializace parametrů plátna
        self.init_canvas()
        
        # Nastavení vlastností
        self.setMouseTracking(True)  # Sledování pohybu myši
        self.setCursor(Qt.CursorShape.CrossCursor)  # Kurzor jako kříž
    
    def init_canvas(self):
        # Vytvoření bílého plátna
        self.canvas_width = 1000
        self.canvas_height = 800
        self.image = QImage(self.canvas_width, self.canvas_height, QImage.Format.Format_ARGB32)
        self.image.fill(Qt.GlobalColor.white)
        
        # Historie pro funkce zpět/znovu
        self.history = [self.image.copy()]
        self.history_index = 0
        self.max_history = 20  # Maximum kroků historie
        
        # Nastavení kreslení
        self.drawing = False
        self.last_point = QPoint()
        self.current_path = QPainterPath()
        
        # Nastavení pera
        self.pen_color = QColor(0, 0, 0)  # Černá
        self.pen_width = 3
        
        # Nastavení textu
        self.text_font = QFont("Arial", 12)
        self.text_is_bold = False
        self.text_is_italic = False
        self.text_is_underline = False
        self.text_align = Qt.AlignmentFlag.AlignLeft
        self.text_editor = None
        self.editing_text = False
        self.text_position = QPoint()
        
        # Nastavení nástroje
        self.current_tool = ToolType.PENCIL
        
        # Výběrový obdélník
        self.selection_rect = None
        self.selected_image = None
        self.selecting = False
        self.moving = False
        self.selection_offset = QPoint(0, 0)
        
        # Dočasné kreslení
        self.temp_image = None
        
        # Zoom
        self.zoom_factor = 1.0
    
    def set_pen_color(self, color):
        self.pen_color = color
    
    def set_pen_width(self, width):
        self.pen_width = width
    
    def set_font(self, font):
        self.text_font = font
        if self.text_editor:
            self.text_editor.setFont(font)
    
    def set_font_size(self, size):
        font = self.text_font
        font.setPointSize(size)
        self.text_font = font
        if self.text_editor:
            self.text_editor.setFont(font)
    
    def set_font_bold(self, bold):
        self.text_is_bold = bold
        font = self.text_font
        font.setBold(bold)
        self.text_font = font
        if self.text_editor:
            self.text_editor.setFont(font)
    
    def set_font_italic(self, italic):
        self.text_is_italic = italic
        font = self.text_font
        font.setItalic(italic)
        self.text_font = font
        if self.text_editor:
            self.text_editor.setFont(font)
    
    def set_font_underline(self, underline):
        self.text_is_underline = underline
        font = self.text_font
        font.setUnderline(underline)
        self.text_font = font
        if self.text_editor:
            self.text_editor.setFont(font)
    
    def set_text_align(self, align):
        self.text_align = align
        if self.text_editor:
            if align == Qt.AlignmentFlag.AlignLeft:
                self.text_editor.setAlignment(Qt.AlignmentFlag.AlignLeft)
            elif align == Qt.AlignmentFlag.AlignCenter:
                self.text_editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
            elif align == Qt.AlignmentFlag.AlignRight:
                self.text_editor.setAlignment(Qt.AlignmentFlag.AlignRight)
    
    def set_tool(self, tool):
        # Nejprve dokončíme jakékoliv probíhající operace
        if self.editing_text and tool != ToolType.TEXT:
            self.finish_text_editing()
        
        self.current_tool = tool
        
        # Resetování výběru při změně nástroje
        if tool != ToolType.SELECT and self.selection_rect is not None:
            self.commit_selection()
            
        # Změna kurzoru podle nástroje
        if tool == ToolType.TEXT:
            self.setCursor(Qt.CursorShape.IBeamCursor)
        else:
            self.setCursor(Qt.CursorShape.CrossCursor)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Nastavení měřítka pro zoom
        painter.scale(self.zoom_factor, self.zoom_factor)
        
        # Vykreslení základního obrázku
        painter.drawImage(0, 0, self.image)
        
        # Vykreslení dočasného obrázku (pro nástroje jako obdélník, elipsa)
        if self.temp_image is not None:
            painter.drawImage(0, 0, self.temp_image)
        
        # Vykreslení výběru
        if self.selection_rect is not None:
            # Vykreslení obrázku výběru, pokud existuje
            if self.selected_image is not None:
                painter.drawImage(self.selection_rect.topLeft(), self.selected_image)
            
            # Vykreslení rámečku kolem výběru
            pen = QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.selection_rect)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Přepočet pozice podle zoomu
            position = QPoint(int(event.position().x() / self.zoom_factor), 
                             int(event.position().y() / self.zoom_factor))
            
            if self.editing_text:
                self.finish_text_editing()
                return
                
            if self.current_tool == ToolType.SELECT:
                # Pokud je aktivní výběr, zkontrolujeme, zda kliknul dovnitř výběru
                if self.selection_rect is not None and self.selection_rect.contains(position):
                    self.moving = True
                    self.selection_offset = position - self.selection_rect.topLeft()
                else:
                    # Začínáme nový výběr
                    if self.selection_rect is not None:
                        self.commit_selection()
                    self.selecting = True
                    self.last_point = position
                    self.selection_rect = QRect(position, QSize(0, 0))
            elif self.current_tool == ToolType.TEXT:
                # Vytvoříme textový editor
                self.start_text_editing(position)
            else:
                self.drawing = True
                self.last_point = position
                
                # Inicializace cesty pro nástroje kreslení
                if self.current_tool in [ToolType.PENCIL, ToolType.BRUSH, ToolType.ERASER]:
                    self.current_path = QPainterPath()
                    self.current_path.moveTo(QPointF(position))
                
                # Pokud používáme nástroj výplň
                if self.current_tool == ToolType.FILL:
                    self.fill_area(position)
    
    def mouseMoveEvent(self, event):
        # Přepočet pozice podle zoomu
        position = QPoint(int(event.position().x() / self.zoom_factor), 
                         int(event.position().y() / self.zoom_factor))
        
        # Aktualizace stavového řádku s pozicí kurzoru
        if hasattr(self.parent, 'statusBar'):
            self.parent.statusBar().showMessage(f"Pozice: ({position.x()}, {position.y()})")
        
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self.current_tool == ToolType.SELECT:
                if self.selecting:
                    # Aktualizace výběrového obdélníku při tažení
                    self.selection_rect = QRect(self.last_point, position).normalized()
                    self.update()
                elif self.moving and self.selection_rect is not None:
                    # Přesun výběru
                    self.selection_rect.moveTo(position - self.selection_offset)
                    self.update()
            elif self.drawing:
                if self.current_tool in [ToolType.PENCIL, ToolType.BRUSH, ToolType.ERASER]:
                    # Kreslení volných čar
                    self.current_path.lineTo(QPointF(position))
                    
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    
                    # Nastavení pro štětec
                    if self.current_tool == ToolType.BRUSH:
                        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                    
                    # Kreslení čáry
                    painter.drawLine(self.last_point, position)
                    self.last_point = position
                    
                    self.update()
                elif self.current_tool in [ToolType.LINE, ToolType.RECTANGLE, ToolType.ROUNDED_RECT, 
                                 ToolType.ELLIPSE, ToolType.TRIANGLE, ToolType.PENTAGON, 
                                 ToolType.HEXAGON, ToolType.STAR, ToolType.ARROW]:
                    # Dočasné vykreslení tvarů
                    self.temp_image = self.image.copy()
                    painter = QPainter(self.temp_image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    
                    if self.current_tool == ToolType.LINE:
                        painter.drawLine(self.last_point, position)
                    elif self.current_tool == ToolType.RECTANGLE:
                        rect = QRect(self.last_point, position).normalized()
                        painter.drawRect(rect)
                    elif self.current_tool == ToolType.ROUNDED_RECT:
                        rect = QRect(self.last_point, position).normalized()
                        painter.drawRoundedRect(rect, 20, 20)
                    elif self.current_tool == ToolType.ELLIPSE:
                        rect = QRect(self.last_point, position).normalized()
                        painter.drawEllipse(rect)
                    elif self.current_tool == ToolType.TRIANGLE:
                        dx = position.x() - self.last_point.x()
                        dy = position.y() - self.last_point.y()
                        
                        polygon = QPolygon()
                        polygon.append(QPoint(self.last_point.x() + dx/2, self.last_point.y()))
                        polygon.append(QPoint(self.last_point.x(), self.last_point.y() + dy))
                        polygon.append(QPoint(self.last_point.x() + dx, self.last_point.y() + dy))
                        
                        painter.drawPolygon(polygon)
                    elif self.current_tool == ToolType.PENTAGON:
                        center_x = (self.last_point.x() + position.x()) / 2
                        center_y = (self.last_point.y() + position.y()) / 2
                        radius = max(abs(position.x() - self.last_point.x()), 
                                    abs(position.y() - self.last_point.y())) / 2
                        
                        polygon = QPolygon()
                        for i in range(5):
                            angle = i * 2 * 3.14159 / 5 - 3.14159 / 2
                            polygon.append(QPoint(int(center_x + radius * np.cos(angle)), 
                                                int(center_y + radius * np.sin(angle))))
                        
                        painter.drawPolygon(polygon)
                    elif self.current_tool == ToolType.HEXAGON:
                        center_x = (self.last_point.x() + position.x()) / 2
                        center_y = (self.last_point.y() + position.y()) / 2
                        radius = max(abs(position.x() - self.last_point.x()), 
                                    abs(position.y() - self.last_point.y())) / 2
                        
                        polygon = QPolygon()
                        for i in range(6):
                            angle = i * 2 * 3.14159 / 6
                            polygon.append(QPoint(int(center_x + radius * np.cos(angle)), 
                                                int(center_y + radius * np.sin(angle))))
                        
                        painter.drawPolygon(polygon)
                    elif self.current_tool == ToolType.STAR:
                        center_x = (self.last_point.x() + position.x()) / 2
                        center_y = (self.last_point.y() + position.y()) / 2
                        outer_radius = max(abs(position.x() - self.last_point.x()), 
                                         abs(position.y() - self.last_point.y())) / 2
                        inner_radius = outer_radius * 0.4
                        
                        polygon = QPolygon()
                        for i in range(10):
                            angle = i * 3.14159 / 5
                            radius = outer_radius if i % 2 == 0 else inner_radius
                            polygon.append(QPoint(int(center_x + radius * np.cos(angle)), 
                                                int(center_y + radius * np.sin(angle))))
                        
                        painter.drawPolygon(polygon)
                    elif self.current_tool == ToolType.ARROW:
                        # Směr šipky
                        dx = position.x() - self.last_point.x()
                        dy = position.y() - self.last_point.y()
                        length = np.sqrt(dx*dx + dy*dy)
                        if length < 1:
                            length = 1
                        
                        # Normalizované směrové vektory
                        dx /= length
                        dy /= length
                        
                        # Kolmý vektor
                        nx = -dy
                        ny = dx
                        
                        # Velikost šipky na konci
                        arrow_size = min(30, length / 3)
                        
                        # Body šipky
                        arrow_tip = position
                        arrow_base1 = QPoint(int(position.x() - arrow_size * dx + arrow_size * 0.5 * nx),
                                            int(position.y() - arrow_size * dy + arrow_size * 0.5 * ny))
                        arrow_base2 = QPoint(int(position.x() - arrow_size * dx - arrow_size * 0.5 * nx),
                                            int(position.y() - arrow_size * dy - arrow_size * 0.5 * ny))
                        
                        # Kreslení čáry a hrotu
                        painter.drawLine(self.last_point, position)
                        
                        arrow_polygon = QPolygon()
                        arrow_polygon.append(arrow_tip)
                        arrow_polygon.append(arrow_base1)
                        arrow_polygon.append(arrow_base2)
                        
                        painter.drawPolygon(arrow_polygon)
                    
                    self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Přepočet pozice podle zoomu
            position = QPoint(int(event.position().x() / self.zoom_factor), 
                             int(event.position().y() / self.zoom_factor))
            
            if self.current_tool == ToolType.SELECT:
                if self.selecting:
                    # Dokončení výběrového obdélníku
                    self.selecting = False
                    self.selection_rect = QRect(self.last_point, position).normalized()
                    
                    # Uložení vybraného obsahu
                    if not self.selection_rect.isEmpty():
                        self.selected_image = self.image.copy(self.selection_rect)
                    else:
                        self.selection_rect = None
                        self.selected_image = None
                    
                elif self.moving:
                    # Dokončení přesunu výběru
                    self.moving = False
                
                self.update()
            elif self.drawing:
                self.drawing = False
                
                if self.current_tool == ToolType.LINE:
                    # Finální vykreslení linie
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    painter.drawLine(self.last_point, position)
                    self.temp_image = None
                
                elif self.current_tool == ToolType.RECTANGLE:
                    # Finální vykreslení obdélníku
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    rect = QRect(self.last_point, position).normalized()
                    painter.drawRect(rect)
                    self.temp_image = None
                
                elif self.current_tool == ToolType.ROUNDED_RECT:
                    # Finální vykreslení zaobleného obdélníku
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    rect = QRect(self.last_point, position).normalized()
                    painter.drawRoundedRect(rect, 20, 20)
                    self.temp_image = None
                
                elif self.current_tool == ToolType.ELLIPSE:
                    # Finální vykreslení elipsy
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    rect = QRect(self.last_point, position).normalized()
                    painter.drawEllipse(rect)
                    self.temp_image = None
                
                elif self.current_tool == ToolType.TRIANGLE:
                    # Finální vykreslení trojúhelníku
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    
                    dx = position.x() - self.last_point.x()
                    dy = position.y() - self.last_point.y()
                    
                    polygon = QPolygon()
                    polygon.append(QPoint(self.last_point.x() + dx/2, self.last_point.y()))
                    polygon.append(QPoint(self.last_point.x(), self.last_point.y() + dy))
                    polygon.append(QPoint(self.last_point.x() + dx, self.last_point.y() + dy))
                    
                    painter.drawPolygon(polygon)
                    self.temp_image = None
                
                elif self.current_tool == ToolType.PENTAGON:
                    # Finální vykreslení pětiúhelníku
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    
                    center_x = (self.last_point.x() + position.x()) / 2
                    center_y = (self.last_point.y() + position.y()) / 2
                    radius = max(abs(position.x() - self.last_point.x()), 
                                abs(position.y() - self.last_point.y())) / 2
                    
                    polygon = QPolygon()
                    for i in range(5):
                        angle = i * 2 * 3.14159 / 5 - 3.14159 / 2
                        polygon.append(QPoint(int(center_x + radius * np.cos(angle)), 
                                            int(center_y + radius * np.sin(angle))))
                    
                    painter.drawPolygon(polygon)
                    self.temp_image = None
                
                elif self.current_tool == ToolType.HEXAGON:
                    # Finální vykreslení šestiúhelníku
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    
                    center_x = (self.last_point.x() + position.x()) / 2
                    center_y = (self.last_point.y() + position.y()) / 2
                    radius = max(abs(position.x() - self.last_point.x()), 
                                abs(position.y() - self.last_point.y())) / 2
                    
                    polygon = QPolygon()
                    for i in range(6):
                        angle = i * 2 * 3.14159 / 6
                        polygon.append(QPoint(int(center_x + radius * np.cos(angle)), 
                                            int(center_y + radius * np.sin(angle))))
                    
                    painter.drawPolygon(polygon)
                    self.temp_image = None
                
                elif self.current_tool == ToolType.STAR:
                    # Finální vykreslení hvězdy
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    
                    center_x = (self.last_point.x() + position.x()) / 2
                    center_y = (self.last_point.y() + position.y()) / 2
                    outer_radius = max(abs(position.x() - self.last_point.x()), 
                                     abs(position.y() - self.last_point.y())) / 2
                    inner_radius = outer_radius * 0.4
                    
                    polygon = QPolygon()
                    for i in range(10):
                        angle = i * 3.14159 / 5
                        radius = outer_radius if i % 2 == 0 else inner_radius
                        polygon.append(QPoint(int(center_x + radius * np.cos(angle)), 
                                            int(center_y + radius * np.sin(angle))))
                    
                    painter.drawPolygon(polygon)
                    self.temp_image = None
                
                elif self.current_tool == ToolType.ARROW:
                    # Finální vykreslení šipky
                    painter = QPainter(self.image)
                    pen = self.get_current_pen()
                    painter.setPen(pen)
                    
                    # Směr šipky
                    dx = position.x() - self.last_point.x()
                    dy = position.y() - self.last_point.y()
                    length = np.sqrt(dx*dx + dy*dy)
                    if length < 1:
                        length = 1
                    
                    # Normalizované směrové vektory
                    dx /= length
                    dy /= length
                    
                    # Kolmý vektor
                    nx = -dy
                    ny = dx
                    
                    # Velikost šipky na konci
                    arrow_size = min(30, length / 3)
                    
                    # Body šipky
                    arrow_tip = position
                    arrow_base1 = QPoint(int(position.x() - arrow_size * dx + arrow_size * 0.5 * nx),
                                        int(position.y() - arrow_size * dy + arrow_size * 0.5 * ny))
                    arrow_base2 = QPoint(int(position.x() - arrow_size * dx - arrow_size * 0.5 * nx),
                                        int(position.y() - arrow_size * dy - arrow_size * 0.5 * ny))
                    
                    # Kreslení čáry a hrotu
                    painter.drawLine(self.last_point, position)
                    
                    arrow_polygon = QPolygon()
                    arrow_polygon.append(arrow_tip)
                    arrow_polygon.append(arrow_base1)
                    arrow_polygon.append(arrow_base2)
                    
                    painter.drawPolygon(arrow_polygon)
                    self.temp_image = None
                
                # Přidání do historie
                self.add_to_history()
    
    def get_current_pen(self):
        pen = QPen()
        
        if self.current_tool == ToolType.ERASER:
            pen.setColor(Qt.GlobalColor.white)
        else:
            pen.setColor(self.pen_color)
        
        pen.setWidth(self.pen_width)
        
        if self.current_tool == ToolType.BRUSH:
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        
        return pen
    
    def fill_area(self, position):
        # Získání barvy v bodě kliku
        target_color = self.image.pixelColor(position)
        
        # Pokud je cílová barva stejná jako barva výplně, není třeba nic dělat
        if target_color == self.pen_color:
            return
        
        # Pro zjednodušení použijeme numpy array pro flood fill algoritmus
        # Pro větší implementaci by bylo lepší použít queue-based algoritmus
        width = self.image.width()
        height = self.image.height()
        
        # Vytvoření kopie obrázku pro úpravy
        temp_image = self.image.copy()
        
        # Konverze QImage na numpy array
        bits = temp_image.bits()
        bits.setsize(height * width * 4)  # 4 bytes per pixel (RGBA)
        arr = np.frombuffer(bits, np.uint8).reshape((height, width, 4))
        
        # Získání cílové barvy jako RGBA
        target_rgba = (target_color.red(), target_color.green(), 
                      target_color.blue(), target_color.alpha())
        
        # Rekurzivní flood fill by byl nevhodný - použijeme stack
        stack = [position]
        visited = set()
        
        while stack:
            x, y = stack.pop()
            
            if (x, y) in visited or x < 0 or y < 0 or x >= width or y >= height:
                continue
            
            # Kontrola, zda barva odpovídá cílové barvě
            pixel_color = (arr[y, x, 0], arr[y, x, 1], arr[y, x, 2], arr[y, x, 3])
            if pixel_color != target_rgba:
                continue
            
            # Nastavení barvy na pozici
            temp_image.setPixelColor(x, y, self.pen_color)
            visited.add((x, y))
            
            # Přidání sousedů do stacku
            stack.append((x+1, y))
            stack.append((x-1, y))
            stack.append((x, y+1))
            stack.append((x, y-1))
            
            # Pro lepší výkon omezíme velikost stacku
            if len(stack) > 10000:
                break
        
        # Kopírování výsledku zpět do hlavního obrázku
        self.image = temp_image
        self.update()
        
        # Přidání do historie
        self.add_to_history()
    
    def start_text_editing(self, position):
        # Vytvoření textového editoru
        self.text_editor = QTextEdit(self)
        self.text_editor.setFont(self.text_font)
        self.text_editor.setTextColor(self.pen_color)
        
        # Nastavení pozice a velikosti
        self.text_position = position
        self.text_editor.setGeometry(
            int(position.x() * self.zoom_factor),
            int(position.y() * self.zoom_factor),
            300, 100
        )
        
        # Nastavení stylů
        self.text_editor.setAlignment(self.text_align)
        
        # Zobrazení a spuštění editace
        self.text_editor.setFocus()
        self.text_editor.show()
        self.editing_text = True
    
    def finish_text_editing(self):
        if self.text_editor is not None:
            # Získání textu
            text = self.text_editor.toPlainText()
            
            if text.strip():  # Pokud text není prázdný
                # Získání měřítka textu
                metrics = QFontMetrics(self.text_font)
                
                # Kreslení textu na plátno
                painter = QPainter(self.image)
                painter.setFont(self.text_font)
                painter.setPen(QPen(self.pen_color))
                
                # Výpočet oblasti textu
                text_width = metrics.horizontalAdvance(text)
                line_height = metrics.height()
                
                painter.drawText(
                    self.text_position.x(),
                    self.text_position.y() + line_height,  # Přidání výšky řádku pro lepší umístění
                    text
                )
                
                # Přidání do historie
                self.add_to_history()
            
            # Odstranění editoru
            self.text_editor.hide()
            self.text_editor.deleteLater()
            self.text_editor = None
            self.editing_text = False
            
            # Aktualizace plátna
            self.update()
            
    def commit_selection(self):
        if self.selection_rect is not None and self.selected_image is not None:
            # Vložení vybraného obsahu na aktuální pozici
            painter = QPainter(self.image)
            painter.drawImage(self.selection_rect.topLeft(), self.selected_image)
            
            # Resetování výběru
            self.selection_rect = None
            self.selected_image = None
            
            # Přidání do historie
            self.add_to_history()
            
            self.update()
    
    def add_to_history(self):
        # Odstranění historie od aktuálního indexu dále
        self.history = self.history[:self.history_index + 1]
        
        # Přidání nového stavu
        self.history.append(self.image.copy())
        self.history_index += 1
        
        # Oříznutí historie, pokud je delší než maximum
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
    
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.image = self.history[self.history_index].copy()
            self.update()
    
    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.image = self.history[self.history_index].copy()
            self.update()
    
    def clear(self):
        # Vytvoření nového čistého plátna
        self.image.fill(Qt.GlobalColor.white)
        
        # Resetování výběru
        self.selection_rect = None
        self.selected_image = None
        
        # Přidání do historie
        self.add_to_history()
        
        self.update()
    
    def new_canvas(self):
        # Inicializace nového plátna
        self.init_canvas()
        self.update()
    
    def load_image(self, file_name):
        loaded_image = QImage(file_name)
        
        if loaded_image.isNull():
            QMessageBox.critical(self, "Chyba", "Nelze načíst obrázek.")
            return False
        
        # Změna velikosti plátna podle načteného obrázku
        self.canvas_width = loaded_image.width()
        self.canvas_height = loaded_image.height()
        
        # Nastavení nového obrázku
        self.image = loaded_image.convertToFormat(QImage.Format.Format_ARGB32)
        
        # Resetování výběru
        self.selection_rect = None
        self.selected_image = None
        
        # Resetování historie
        self.history = [self.image.copy()]
        self.history_index = 0
        
        self.update()
        return True
    
    def save_image(self, file_name):
        # Uložení aktuálního plátna do souboru
        self.image.save(file_name)
    
    def show_resize_dialog(self):
        # Dialog pro změnu velikosti plátna
        width, ok1 = QInputDialog.getInt(self, "Změna velikosti plátna", 
                                       "Šířka:", self.canvas_width, 10, 3000)
        if not ok1:
            return
        
        height, ok2 = QInputDialog.getInt(self, "Změna velikosti plátna", 
                                        "Výška:", self.canvas_height, 10, 3000)
        if not ok2:
            return
        
        self.resize_canvas(width, height)
    
    def resize_canvas(self, width, height):
        # Vytvoření nového plátna s požadovanou velikostí
        new_image = QImage(width, height, QImage.Format.Format_ARGB32)
        new_image.fill(Qt.GlobalColor.white)
        
        # Překreslení původního obsahu
        painter = QPainter(new_image)
        painter.drawImage(0, 0, self.image)
        painter.end()
        
        # Aktualizace velikosti plátna
        self.canvas_width = width
        self.canvas_height = height
        self.image = new_image
        
        # Resetování výběru
        self.selection_rect = None
        self.selected_image = None
        
        # Přidání do historie
        self.add_to_history()
        
        self.update()
    
    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.update()
    
    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.zoom_factor = max(0.1, self.zoom_factor)  # Minimální zoom
        self.update()
    
    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.update()
    
    def sizeHint(self):
        # Přizpůsobení velikosti widgetu
        return QSize(self.canvas_width, self.canvas_height)