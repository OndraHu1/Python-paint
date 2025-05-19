import os
from PyQt6.QtWidgets import (QMainWindow, QToolBar, QColorDialog, QFileDialog,
                            QSlider, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
                            QWidget, QDockWidget, QComboBox, QMessageBox, QStyleFactory,
                            QTabWidget, QFontComboBox, QSpinBox, QCheckBox, QGraphicsOpacityEffect)
from PyQt6.QtGui import (QPixmap, QPainter, QPen, QColor, QIcon, QImage, QFont,
                        QPainterPath, QMouseEvent, QKeySequence, QFontDatabase)
from PyQt6.QtCore import Qt, QPoint, QSize, QRect
from paint_canvas import PaintCanvas
from tools import ToolType, ThemeType

class PaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_theme = ThemeType.DARK
        self.opacity = 1.0
        self.blur_enabled = False
        self.init_ui()
        
    def init_ui(self):
        # Nastavení hlavního okna
        self.setWindowTitle("Malování")
        self.setGeometry(100, 100, 1200, 800)
        
        # Aplikace moderního stylu
        self.apply_custom_style()
        
        # Vytvoření plátna
        self.canvas = PaintCanvas(self)
        self.setCentralWidget(self.canvas)
        
        # Vytvoření nástrojů a UI
        self.create_menu_actions()
        self.create_ribbon_tabs()
        self.create_toolbars()
        self.create_color_dock()
        
        # Stavový řádek
        self.statusBar().showMessage("Připraveno")
        
    def create_menu_actions(self):
        # Nabídka Soubor
        file_menu = self.menuBar().addMenu("&Soubor")
        
        new_act = file_menu.addAction("&Nový")
        new_act.setShortcut(QKeySequence("Ctrl+N"))
        new_act.triggered.connect(self.new_canvas)
        
        open_act = file_menu.addAction("&Otevřít...")
        open_act.setShortcut(QKeySequence("Ctrl+O"))
        open_act.triggered.connect(self.open_image)
        
        save_act = file_menu.addAction("&Uložit...")
        save_act.setShortcut(QKeySequence("Ctrl+S"))
        save_act.triggered.connect(self.save_image)
        
        file_menu.addSeparator()
        
        exit_act = file_menu.addAction("&Konec")
        exit_act.setShortcut(QKeySequence("Ctrl+Q"))
        exit_act.triggered.connect(self.close)
        
        # Nabídka Edit
        edit_menu = self.menuBar().addMenu("&Úpravy")
        
        undo_act = edit_menu.addAction("&Zpět")
        undo_act.setShortcut(QKeySequence("Ctrl+Z"))
        undo_act.triggered.connect(self.canvas.undo)
        
        redo_act = edit_menu.addAction("&Znovu")
        redo_act.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        redo_act.triggered.connect(self.canvas.redo)
        
        edit_menu.addSeparator()
        
        clear_act = edit_menu.addAction("&Vyčistit plátno")
        clear_act.triggered.connect(self.canvas.clear)
        
        # Nabídka Zobrazení
        view_menu = self.menuBar().addMenu("&Zobrazení")
        
        zoom_in_act = view_menu.addAction("Přiblížit")
        zoom_in_act.setShortcut(QKeySequence("Ctrl++"))
        zoom_in_act.triggered.connect(self.canvas.zoom_in)
        
        zoom_out_act = view_menu.addAction("Oddálit")
        zoom_out_act.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_act.triggered.connect(self.canvas.zoom_out)
        
        reset_zoom_act = view_menu.addAction("Resetovat zoom")
        reset_zoom_act.triggered.connect(self.canvas.reset_zoom)
        
        # Nabídka Nápověda
        help_menu = self.menuBar().addMenu("&Nápověda")
        
        about_act = help_menu.addAction("&O aplikaci")
        about_act.triggered.connect(self.show_about)
    
    def create_ribbon_tabs(self):
        # Vytvoření horní lišty s taby
        self.ribbon = QTabWidget(self)
        self.ribbon.setTabPosition(QTabWidget.TabPosition.North)
        self.ribbon.setFixedHeight(120)
        
        # Nastavení fontu pro záložky
        tab_font = QFont("Arial", 10, QFont.Weight.Bold)
        self.ribbon.setFont(tab_font)
        
        # Záložka Domů
        home_tab = QWidget()
        home_layout = QHBoxLayout(home_tab)
        
        # Sekce nástrojů
        tools_widget = QWidget()
        tools_layout = QVBoxLayout(tools_widget)
        tools_layout.setSpacing(2)
        tools_title = QLabel("Nástroje")
        tools_title.setFont(QFont("Arial Black", 10))
        tools_layout.addWidget(tools_title)
        
        tools_grid = QHBoxLayout()
        tool_buttons = [
            ("Tužka", ToolType.PENCIL),
            ("Štětec", ToolType.BRUSH),
            ("Guma", ToolType.ERASER),
            ("Text", ToolType.TEXT),
            ("Výplň", ToolType.FILL),
            ("Výběr", ToolType.SELECT)
        ]
        
        for name, tool_type in tool_buttons:
            btn = QPushButton(name)
            btn.setFixedSize(60, 25)
            btn.clicked.connect(lambda _, t=tool_type: self.set_tool(t))
            tools_grid.addWidget(btn)
        
        tools_layout.addLayout(tools_grid)
        home_layout.addWidget(tools_widget)
        
        # Sekce tvarů
        shapes_widget = QWidget()
        shapes_layout = QVBoxLayout(shapes_widget)
        shapes_title = QLabel("Tvary")
        shapes_title.setFont(QFont("Arial Black", 10))
        shapes_layout.addWidget(shapes_title)
        
        shapes_grid = QHBoxLayout()
        shape_buttons = [
            ("Linie", ToolType.LINE),
            ("Obdélník", ToolType.RECTANGLE),
            ("Zaoblený", ToolType.ROUNDED_RECT),
            ("Elipsa", ToolType.ELLIPSE),
            ("Trojúhelník", ToolType.TRIANGLE),
            ("Šipka", ToolType.ARROW)
        ]
        
        for name, tool_type in shape_buttons:
            btn = QPushButton(name)
            btn.setFixedSize(60, 25)
            btn.clicked.connect(lambda _, t=tool_type: self.set_tool(t))
            shapes_grid.addWidget(btn)
        
        more_shapes_btn = QPushButton("Více...")
        more_shapes_btn.setFixedSize(60, 25)
        more_shapes_btn.clicked.connect(self.show_more_shapes)
        shapes_grid.addWidget(more_shapes_btn)
        
        shapes_layout.addLayout(shapes_grid)
        home_layout.addWidget(shapes_widget)
        
        # Sekce tloušťky
        thickness_widget = QWidget()
        thickness_layout = QVBoxLayout(thickness_widget)
        thickness_title = QLabel("Tloušťka")
        thickness_title.setFont(QFont("Arial Black", 10))
        thickness_layout.addWidget(thickness_title)
        
        self.thickness_slider = QSlider(Qt.Orientation.Horizontal)
        self.thickness_slider.setRange(1, 50)
        self.thickness_slider.setValue(3)
        self.thickness_slider.valueChanged.connect(self.change_thickness)
        thickness_layout.addWidget(self.thickness_slider)
        
        home_layout.addWidget(thickness_widget)
        
        # Sekce barev
        colors_widget = QWidget()
        colors_layout = QVBoxLayout(colors_widget)
        colors_title = QLabel("Barvy")
        colors_title.setFont(QFont("Arial Black", 10))
        colors_layout.addWidget(colors_title)
        
        color_grid = QHBoxLayout()
        preset_colors = [
            QColor(0, 0, 0),      # Černá
            QColor(255, 255, 255), # Bílá
            QColor(255, 0, 0),    # Červená
            QColor(0, 255, 0),    # Zelená
            QColor(0, 0, 255),    # Modrá
            QColor(255, 255, 0),  # Žlutá
            QColor(255, 0, 255),  # Purpurová
            QColor(0, 255, 255),  # Azurová
        ]
        
        for color in preset_colors:
            color_btn = QPushButton()
            color_btn.setStyleSheet(f"background-color: {color.name()}; min-width: 25px; min-height: 25px; border: 1px solid #888;")
            color_btn.setFixedSize(25, 25)
            color_btn.clicked.connect(lambda _, c=color: self.set_color(c))
            color_grid.addWidget(color_btn)
        
        more_colors_btn = QPushButton("Další...")
        more_colors_btn.setFixedSize(50, 25)
        more_colors_btn.clicked.connect(self.open_color_dialog)
        color_grid.addWidget(more_colors_btn)
        
        colors_layout.addLayout(color_grid)
        home_layout.addWidget(colors_widget)
        
        # Přidat záložku Domů do ribbonu
        self.ribbon.addTab(home_tab, "Domů")
        
        # Záložka Text
        text_tab = QWidget()
        text_layout = QHBoxLayout(text_tab)
        
        # Sekce fontu
        font_widget = QWidget()
        font_layout = QVBoxLayout(font_widget)
        font_title = QLabel("Font")
        font_title.setFont(QFont("Arial Black", 10))
        font_layout.addWidget(font_title)
        
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Arial"))
        self.font_combo.setFixedWidth(150)
        self.font_combo.currentFontChanged.connect(self.change_font)
        font_layout.addWidget(self.font_combo)
        
        text_layout.addWidget(font_widget)
        
        # Sekce velikosti
        size_widget = QWidget()
        size_layout = QVBoxLayout(size_widget)
        size_title = QLabel("Velikost")
        size_title.setFont(QFont("Arial Black", 10))
        size_layout.addWidget(size_title)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(12)
        self.font_size.valueChanged.connect(self.change_font_size)
        size_layout.addWidget(self.font_size)
        
        text_layout.addWidget(size_widget)
        
        # Sekce stylu
        style_widget = QWidget()
        style_layout = QVBoxLayout(style_widget)
        style_title = QLabel("Styl")
        style_title.setFont(QFont("Arial Black", 10))
        style_layout.addWidget(style_title)
        
        style_buttons = QHBoxLayout()
        self.bold_btn = QPushButton("B")
        self.bold_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.bold_btn.setCheckable(True)
        self.bold_btn.setFixedSize(25, 25)
        self.bold_btn.clicked.connect(self.toggle_bold)
        
        self.italic_btn = QPushButton("I")
        self.italic_btn.setFont(QFont("Arial", 10, QFont.Weight.Normal, True))
        self.italic_btn.setCheckable(True)
        self.italic_btn.setFixedSize(25, 25)
        self.italic_btn.clicked.connect(self.toggle_italic)
        
        self.underline_btn = QPushButton("U")
        self.underline_btn.setCheckable(True)
        self.underline_btn.setFixedSize(25, 25)
        self.underline_btn.clicked.connect(self.toggle_underline)
        
        style_buttons.addWidget(self.bold_btn)
        style_buttons.addWidget(self.italic_btn)
        style_buttons.addWidget(self.underline_btn)
        
        style_layout.addLayout(style_buttons)
        text_layout.addWidget(style_widget)
        
        # Sekce zarovnání
        align_widget = QWidget()
        align_layout = QVBoxLayout(align_widget)
        align_title = QLabel("Zarovnání")
        align_title.setFont(QFont("Arial Black", 10))
        align_layout.addWidget(align_title)
        
        align_buttons = QHBoxLayout()
        self.align_left = QPushButton("Vlevo")
        self.align_left.setCheckable(True)
        self.align_left.setChecked(True)
        self.align_left.setFixedSize(60, 25)
        
        self.align_center = QPushButton("Střed")
        self.align_center.setCheckable(True)
        self.align_center.setFixedSize(60, 25)
        
        self.align_right = QPushButton("Vpravo")
        self.align_right.setCheckable(True)
        self.align_right.setFixedSize(60, 25)
        
        align_buttons.addWidget(self.align_left)
        align_buttons.addWidget(self.align_center)
        align_buttons.addWidget(self.align_right)
        
        align_layout.addLayout(align_buttons)
        text_layout.addWidget(align_widget)
        
        # Přidat záložku Text do ribbonu
        self.ribbon.addTab(text_tab, "Text")
        
        # Záložka Vzhled
        view_tab = QWidget()
        view_layout = QHBoxLayout(view_tab)
        
        # Sekce tématu
        theme_widget = QWidget()
        theme_layout = QVBoxLayout(theme_widget)
        theme_title = QLabel("Téma")
        theme_title.setFont(QFont("Arial Black", 10))
        theme_layout.addWidget(theme_title)
        
        theme_buttons = QHBoxLayout()
        self.light_theme_btn = QPushButton("Světlé")
        self.light_theme_btn.setCheckable(True)
        self.light_theme_btn.setFixedSize(70, 25)
        self.light_theme_btn.clicked.connect(lambda: self.change_theme(ThemeType.LIGHT))
        
        self.dark_theme_btn = QPushButton("Tmavé")
        self.dark_theme_btn.setCheckable(True)
        self.dark_theme_btn.setChecked(True)
        self.dark_theme_btn.setFixedSize(70, 25)
        self.dark_theme_btn.clicked.connect(lambda: self.change_theme(ThemeType.DARK))
        
        theme_buttons.addWidget(self.light_theme_btn)
        theme_buttons.addWidget(self.dark_theme_btn)
        
        theme_layout.addLayout(theme_buttons)
        view_layout.addWidget(theme_widget)
        
        # Sekce průhlednosti
        opacity_widget = QWidget()
        opacity_layout = QVBoxLayout(opacity_widget)
        opacity_title = QLabel("Průhlednost")
        opacity_title.setFont(QFont("Arial Black", 10))
        opacity_layout.addWidget(opacity_title)
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        opacity_layout.addWidget(self.opacity_slider)
        
        view_layout.addWidget(opacity_widget)
        
        # Sekce efektů
        effects_widget = QWidget()
        effects_layout = QVBoxLayout(effects_widget)
        effects_title = QLabel("Efekty")
        effects_title.setFont(QFont("Arial Black", 10))
        effects_layout.addWidget(effects_title)
        
        self.blur_checkbox = QCheckBox("Rozmazání")
        self.blur_checkbox.stateChanged.connect(self.toggle_blur)
        effects_layout.addWidget(self.blur_checkbox)
        
        view_layout.addWidget(effects_widget)
        
        # Sekce plátna
        canvas_widget = QWidget()
        canvas_layout = QVBoxLayout(canvas_widget)
        canvas_title = QLabel("Plátno")
        canvas_title.setFont(QFont("Arial Black", 10))
        canvas_layout.addWidget(canvas_title)
        
        resize_button = QPushButton("Změnit velikost")
        resize_button.clicked.connect(self.resize_canvas)
        canvas_layout.addWidget(resize_button)
        
        view_layout.addWidget(canvas_widget)
        
        # Přidat záložku Vzhled do ribbonu
        self.ribbon.addTab(view_tab, "Vzhled")
        
        # Přidání ribbonu do layoutu
        self.addToolBarBreak()
        ribbon_toolbar = QToolBar()
        ribbon_toolbar.addWidget(self.ribbon)
        self.addToolBar(ribbon_toolbar)
    
    def create_toolbars(self):
        # Boční panel nástrojů
        toolbar = QToolBar("Další nástroje", self)
        toolbar.setIconSize(QSize(32, 32))
        toolbar.setOrientation(Qt.Orientation.Vertical)
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, toolbar)
        
        # Další nástroje pro kreslení
        additional_tools = [
            ("Pentagon", ToolType.PENTAGON),
            ("Šestiúhelník", ToolType.HEXAGON),
            ("Hvězda", ToolType.STAR)
        ]
        
        for name, tool_type in additional_tools:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, t=tool_type: self.set_tool(t))
            toolbar.addWidget(btn)
        
        toolbar.addSeparator()
    
    def create_color_dock(self):
        # Panel pro výběr barev
        color_dock = QDockWidget("Barvy", self)
        color_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        color_widget = QWidget()
        color_layout = QVBoxLayout()
        
        # Aktuální barva
        self.current_color = QColor(0, 0, 0)  # Výchozí je černá
        
        self.color_display = QPushButton()
        self.color_display.setStyleSheet(f"background-color: {self.current_color.name()}")
        self.color_display.setFixedSize(100, 50)
        self.color_display.clicked.connect(self.open_color_dialog)
        
        color_layout.addWidget(QLabel("Aktuální barva:"))
        color_layout.addWidget(self.color_display)
        
        # Přednastavené barvy
        color_layout.addWidget(QLabel("Oblíbené barvy:"))
        
        preset_colors = [
            QColor(0, 0, 0),      # Černá
            QColor(255, 255, 255), # Bílá
            QColor(255, 0, 0),    # Červená
            QColor(0, 255, 0),    # Zelená
            QColor(0, 0, 255),    # Modrá
            QColor(255, 255, 0),  # Žlutá
            QColor(255, 0, 255),  # Purpurová
            QColor(0, 255, 255),  # Azurová
        ]
        
        preset_layout = QHBoxLayout()
        
        for color in preset_colors:
            preset_button = QPushButton()
            preset_button.setStyleSheet(f"background-color: {color.name()}")
            preset_button.setFixedSize(30, 30)
            preset_button.clicked.connect(lambda checked, c=color: self.set_color(c))
            preset_layout.addWidget(preset_button)
        
        color_layout.addLayout(preset_layout)
        color_layout.addStretch()
        
        color_widget.setLayout(color_layout)
        color_dock.setWidget(color_widget)
        
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, color_dock)
    
    def set_tool(self, tool_type):
        self.canvas.set_tool(tool_type)
        # Aktualizace stavu tlačítek v ribbonu
        
    def change_thickness(self, value):
        self.canvas.set_pen_width(value)
    
    def change_font(self, font):
        self.canvas.set_font(font)
    
    def change_font_size(self, size):
        self.canvas.set_font_size(size)
    
    def toggle_bold(self, checked):
        self.canvas.set_font_bold(checked)
        # Zrušit zaškrtnutí ostatních pro vzájemné vyloučení
        if checked:
            self.italic_btn.setChecked(False)
            self.underline_btn.setChecked(False)
    
    def toggle_italic(self, checked):
        self.canvas.set_font_italic(checked)
        # Zrušit zaškrtnutí ostatních pro vzájemné vyloučení
        if checked:
            self.bold_btn.setChecked(False)
            self.underline_btn.setChecked(False)
    
    def toggle_underline(self, checked):
        self.canvas.set_font_underline(checked)
        # Zrušit zaškrtnutí ostatních pro vzájemné vyloučení
        if checked:
            self.bold_btn.setChecked(False)
            self.italic_btn.setChecked(False)
    
    def change_theme(self, theme_type):
        self.current_theme = theme_type
        if theme_type == ThemeType.LIGHT:
            self.light_theme_btn.setChecked(True)
            self.dark_theme_btn.setChecked(False)
            self.apply_light_theme()
        else:
            self.light_theme_btn.setChecked(False)
            self.dark_theme_btn.setChecked(True)
            self.apply_dark_theme()
    
    def apply_light_theme(self):
        # Nastavení světlého tématu
        palette = self.palette()
        palette.setColor(palette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(palette.ColorRole.WindowText, QColor(0, 0, 0))
        palette.setColor(palette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(palette.ColorRole.AlternateBase, QColor(240, 240, 240))
        palette.setColor(palette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(palette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(palette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(palette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(palette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(palette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(palette.ColorRole.Link, QColor(0, 100, 200))
        palette.setColor(palette.ColorRole.Highlight, QColor(0, 120, 215))
        palette.setColor(palette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Nastavení stylesheetů
        self.setStyleSheet("""
            QToolBar { border: none; background: #f0f0f0; }
            QToolBar::separator { background: #d0d0d0; width: 1px; height: 1px; }
            QStatusBar { background: #f0f0f0; color: black; }
            QMessageBox { background-color: #f0f0f0; }
            QDockWidget { border: 1px solid #d0d0d0; background: #f0f0f0; }
            QDockWidget::title { background: #e0e0e0; padding-left: 5px; }
            QComboBox { background: #f8f8f8; color: black; border: 1px solid #d0d0d0; padding: 2px 8px; }
            QSlider::groove:horizontal { 
                border: 1px solid #c0c0c0;
                height: 8px;
                background: #f8f8f8;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #0078d7;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QPushButton { 
                background-color: #f0f0f0; 
                color: black;
                border: 1px solid #d0d0d0;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #e5e5e5; }
            QPushButton:pressed { background-color: #d0d0d0; }
            QTabWidget::pane { border: 1px solid #d0d0d0; }
            QTabBar::tab { 
                background: #e0e0e0; 
                border: 1px solid #d0d0d0; 
                padding: 6px 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected { 
                background: #f0f0f0; 
                border-bottom-color: #f0f0f0;
            }
        """)
    
    def apply_dark_theme(self):
        # Nastavení tmavého tématu
        self.apply_custom_style()
    
    def change_opacity(self, value):
        self.opacity = value / 100.0
        self.setWindowOpacity(self.opacity)
    
    def toggle_blur(self, state):
        self.blur_enabled = state > 0
        if self.blur_enabled:
            # Implementovat blur efekt na okně nebo plátně
            # Toto by vyžadovalo pokročilé QGraphicsEffects nebo QML pro plný efekt
            # Pro demonstrační účely použijeme jen jednoduchý efekt průhlednosti
            self.setWindowOpacity(0.9)
        else:
            self.setWindowOpacity(self.opacity)
    
    def show_more_shapes(self):
        # Zobrazit dialog s dalšími tvary
        shapes = QMessageBox()
        shapes.setWindowTitle("Další tvary")
        shapes.setText("Další tvary jsou dostupné v bočním panelu nástrojů.")
        shapes.exec()
        
    def open_color_dialog(self):
        color = QColorDialog.getColor(self.current_color, self, "Vyberte barvu")
        if color.isValid():
            self.set_color(color)
    
    def set_color(self, color):
        self.current_color = color
        self.color_display.setStyleSheet(f"background-color: {color.name()}")
        self.canvas.set_pen_color(color)
    
    def new_canvas(self):
        reply = QMessageBox.question(self, "Nový obrázek", 
                                    "Chcete vytvořit nový obrázek? Neuložené změny budou ztraceny.",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.new_canvas()
    
    def open_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Otevřít obrázek", "", 
            "Obrázky (*.png *.jpg *.bmp);;Všechny soubory (*)", 
            options=options
        )
        
        if file_name:
            self.canvas.load_image(file_name)
    
    def save_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Uložit obrázek", "", 
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp)", 
            options=options
        )
        
        if file_name:
            if not any(file_name.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp']):
                file_name += '.png'  # Výchozí formát je PNG
            
            self.canvas.save_image(file_name)
            
    def resize_canvas(self):
        self.canvas.show_resize_dialog()
    
    def apply_custom_style(self):
        # Nastavení moderního stylu
        self.setStyle(QStyleFactory.create("Fusion"))
        
        # Definice barevné palety
        palette = self.palette()
        palette.setColor(palette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(palette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(palette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(palette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(palette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(palette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(palette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(palette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(palette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(palette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(palette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(palette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(palette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Nastavení stylopisu pro widgets
        self.setStyleSheet("""
            QToolBar { border: none; background: #303030; }
            QToolBar::separator { background: #505050; width: 1px; height: 1px; }
            QStatusBar { background: #303030; color: white; }
            QMessageBox { background-color: #303030; }
            QDockWidget { border: 1px solid #505050; background: #303030; }
            QDockWidget::title { background: #404040; padding-left: 5px; }
            QComboBox { background: #505050; color: white; border: 1px solid #606060; padding: 2px 8px; }
            QSlider::groove:horizontal { 
                border: 1px solid #999999;
                height: 8px;
                background: #505050;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #2a82da;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QPushButton { 
                background-color: #505050; 
                color: white;
                border: 1px solid #606060;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #606060; }
            QPushButton:pressed { background-color: #404040; }
        """)
    
    def show_about(self):
        QMessageBox.about(self, "O aplikaci Malování", 
                         "Malování\n\n"
                         "Aplikace pro malování vytvořená v Pythonu s PyQt6.\n"
                         "Verze 1.0")