# QuishGuard - Advanced Phishing Detection System

QuishGuard is a forensic cybersecurity tool designed to detect, analyze, and unmask malicious QR codes and URLs. Unlike standard scanners, it focuses on Blue Team analysis—revealing redirection chains, hidden scripts, and potential threats before the user opens the link.

## Features

### Smart Detection Engine
- **Multi-Format Scanning**: Drag and drop Images (.png, .jpg) or PDF Documents.
- **Batch Processing**: Automatically finds and analyzes every QR code in a multi-page PDF.
- **Heuristic Analysis**: Calculates a "Threat Score" based on redirection depth, IP hostnames, and suspicious keywords.

### Forensic Analysis
- **Redirection Tracing**: Unmasks shortened links (e.g., bit.ly, tinyurl) to show the final destination without visiting it.
- **Defanging**: Automatically converts malicious URLs (e.g., http://malware.com becomes hxxp[:]//malware[.]com) to prevent accidental clicks.
- **Detailed Logs**: View the full hop-by-hop path of any link.

### Professional Reporting
- **Scan History**: Automatically saves a local audit trail of all scans.
- **Export Reports**: Generates timestamped forensic text reports for evidence.

### Modern UI
- **Cyber-Brutalist Design**: Dark mode interface built with PyQt6.
- **Privacy First**: All analysis happens locally on your machine. No files are uploaded to the cloud.

---

## Installation

### For End Users (Recommended)
This project uses Git LFS to provide a complete, pre-compiled Windows installer. You do not need Python installed to run this version.

1.  Navigate to the **dist** folder in this repository.
2.  Download the file named **QuishGuard_Setup.exe**.
3.  Run the installer. It will guide you through the setup and create shortcuts on your Desktop and Start Menu.

### For Developers
If you wish to modify the source code or build it yourself, follow these steps.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/QuishGuard.git](https://github.com/YOUR_USERNAME/QuishGuard.git)
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python main.py
    ```

## Building from Source
To compile the executable and installer from the source code, use the included build script. This will generate the distribution files in the `dist` folder.

```bash
python build_final.py
````

## Acknowledgments

  - **Gemini (Google):** For providing extensive assistance in the architectural design, debugging, and development of the application logic and user interface.
  - **QtAwesome:** For the FontAwesome icon implementation.
  - **PyMuPDF & OpenCV:** For the core document and image processing capabilities.

## Disclaimer

This tool is developed for educational and defensive purposes only. The developers are not responsible for any misuse of this software. Ensure you have authorization before analyzing suspicious files.

```
```