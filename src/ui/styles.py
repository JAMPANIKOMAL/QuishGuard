class Theme:
    SIDEBAR_BTN_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #888888;
        text-align: left;
        padding-left: 20px;
        border: none;
        border-left: 3px solid transparent;
        font-weight: bold;
        font-size: 13px;
        height: 45px;
    }
    QPushButton:hover {
        color: #FFFFFF;
        background-color: #222222;
        border-left: 3px solid #FFFFFF;
    }
    """

    DARK_STYLES = SIDEBAR_BTN_STYLE + """
    QMainWindow { background-color: #121212; }
    
    #sidebar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #1a1a1a);
        border-right: 1px solid #333333;
    }
    
    #btn_menu { padding-left: 0px; text-align: center; }

    #drop_zone {
        background-color: #1E1E1E;
        border: 2px dashed #444444;
        border-radius: 10px;
        color: #888888;
        font-size: 16px;
        font-weight: bold;
    }
    
    #console {
        background-color: #080808;
        border: 1px solid #333333;
        color: #00FF00;
        font-family: Consolas, Monospace;
        padding: 10px;
    }
    
    /* The Resize Handle (Splitter) */
    QSplitter::handle {
        background-color: #333333;
    }
    QSplitter::handle:hover {
        background-color: #00FF00; /* Lights up green when you grab it */
    }
    """

    LIGHT_STYLES = SIDEBAR_BTN_STYLE.replace("#888888", "#555555").replace("#FFFFFF", "#000000").replace("#222222", "#EAEAEA") + """
    QMainWindow { background-color: #F5F5F5; }
    
    #sidebar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFFFFF, stop:1 #E0E0E0);
        border-right: 1px solid #CCCCCC;
    }
    
    #btn_menu { padding-left: 0px; text-align: center; }

    #drop_zone {
        background-color: #FFFFFF;
        border: 2px dashed #BBBBBB;
        border-radius: 10px;
        color: #555555;
        font-size: 16px;
    }
    
    #console {
        background-color: #FFFFFF;
        border: 1px solid #CCCCCC;
        color: #000000;
        font-family: Consolas, Monospace;
        padding: 10px;
    }
    
    QSplitter::handle {
        background-color: #CCCCCC;
    }
    """