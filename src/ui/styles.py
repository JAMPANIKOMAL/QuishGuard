class Theme:
    # --- SHARED DIMENSIONS ---
    # This ensures the sidebar looks good in both 60px (collapsed) and 220px (expanded) modes
    SIDEBAR_BTN_STYLE = """
    QPushButton {
        background-color: transparent;
        color: #888888;
        text-align: left;
        padding-left: 20px; /* Fixed indentation for text */
        border: none;
        border-left: 3px solid transparent; /* Invisible border for alignment */
        font-weight: bold;
        font-size: 14px;
        height: 50px; /* Fixed height for all buttons */
    }
    QPushButton:hover {
        color: #FFFFFF;
        background-color: #222222;
        border-left: 3px solid #FFFFFF; /* The white accent bar */
    }
    """

    # --- DARK MODE (DEFAULT) ---
    DARK_STYLES = SIDEBAR_BTN_STYLE + """
    QMainWindow {
        background-color: #121212;
    }
    
    #sidebar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #000000, stop:1 #1a1a1a);
        border-right: 1px solid #333333;
    }

    /* Special styling for the Hamburger Menu to center it when needed */
    #btn_menu {
        padding-left: 0px; 
        text-align: center;
        font-size: 18px;
    }
    
    #drop_zone {
        background-color: #1E1E1E;
        border: 2px dashed #444444;
        border-radius: 10px;
        color: #888888;
        font-size: 16px;
    }
    
    #console {
        background-color: #080808;
        border-top: 2px solid #333333;
        color: #00FF00;
        font-family: Consolas, Monospace;
        padding: 15px;
        font-size: 13px;
        selection-background-color: #00FF00;
        selection-color: #000000;
    }
    """

    # --- LIGHT MODE (INVERTED) ---
    LIGHT_STYLES = SIDEBAR_BTN_STYLE.replace("#888888", "#555555").replace("#FFFFFF", "#000000").replace("#222222", "#EAEAEA") + """
    QMainWindow {
        background-color: #F5F5F5;
    }
    
    #sidebar {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFFFFF, stop:1 #E0E0E0);
        border-right: 1px solid #CCCCCC;
    }
    
    #btn_menu {
        padding-left: 0px; 
        text-align: center;
        font-size: 18px;
    }
    
    #drop_zone {
        background-color: #FFFFFF;
        border: 2px dashed #BBBBBB;
        border-radius: 10px;
        color: #555555;
    }
    
    #console {
        background-color: #FFFFFF;
        border-top: 2px solid #CCCCCC;
        color: #000000;
        font-family: Consolas, Monospace;
        padding: 15px;
        font-size: 13px;
    }
    """