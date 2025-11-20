class Theme:
    """
    Defines the palette for Dark (Default) and Light modes.
    We use CSS-like syntax (QSS) for PyQt6.
    """
    
    # --- DARK MODE (DEFAULT) ---
    DARK_STYLES = """
    QMainWindow {
        background-color: #121212;
    }
    
    /* Sidebar Gradient: Deep Black to Dark Grey */
    #sidebar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #1a1a1a);
        border-right: 1px solid #333333;
    }
    
    /* Sidebar Buttons */
    QPushButton {
        background-color: transparent;
        color: #888888;
        text-align: left;
        padding: 15px;
        border: none;
        font-weight: bold;
        font-size: 14px;
    }
    QPushButton:hover {
        color: #FFFFFF;
        background-color: #222222;
        border-left: 3px solid #FFFFFF; 
    }
    
    /* Drop Zone: Dashed Border */
    #drop_zone {
        background-color: #1E1E1E;
        border: 2px dashed #444444;
        border-radius: 10px;
        color: #888888;
        font-size: 16px;
    }
    
    /* Console/Log Area */
    #console {
        background-color: #000000;
        border-top: 1px solid #333333;
        color: #00FF00; /* Classic Terminal Green for text */
        font-family: Consolas, Monospace;
        padding: 10px;
    }
    """

    # --- LIGHT MODE (INVERTED) ---
    LIGHT_STYLES = """
    QMainWindow {
        background-color: #F5F5F5;
    }
    
    #sidebar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFFFFF, stop:1 #E0E0E0);
        border-right: 1px solid #CCCCCC;
    }
    
    QPushButton {
        color: #555555;
        background-color: transparent;
        text-align: left;
        padding: 15px;
        border: none;
        font-weight: bold;
        font-size: 14px;
    }
    QPushButton:hover {
        color: #000000;
        background-color: #EAEAEA;
        border-left: 3px solid #000000;
    }
    
    #drop_zone {
        background-color: #FFFFFF;
        border: 2px dashed #BBBBBB;
        border-radius: 10px;
        color: #555555;
    }
    
    #console {
        background-color: #FFFFFF;
        border-top: 1px solid #CCCCCC;
        color: #000000;
        font-family: Consolas, Monospace;
        padding: 10px;
    }
    """