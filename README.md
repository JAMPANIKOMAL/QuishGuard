# QuishGuard: Forensic QR & Phishing Analyzer

QuishGuard is a forensic cybersecurity tool designed for Blue Team operations. It automates the detection and analysis of malicious QR codes (Quishing) and obfuscated URLs within static files (Images/PDFs).

## Key Capabilities

### Automated Threat Detection
* **Multi-Vector Scanning**: Extracts QR codes from raw images (.png, .jpg) and parses multi-page PDF documents using PyMuPDF.
* **Heuristic Engine**: Algorithms analyze URL structures for indicators of compromise (IoC), including:
    * Deep redirection chains (greater than 3 hops).
    * Direct IP usage (e.g., http://192.168.x.x).
    * Suspicious keywords and executable extensions (.exe, .apk).

### Forensic Analysis
* **Safe URL Unshortening**: Traces redirection chains (e.g., bit.ly -> malicious.site) without executing payloads, allowing analysts to see the final destination safely.
* **Defanging**: Automatically sanitizes URLs (e.g., hxxp[:]//bad[.]site) in logs to prevent accidental clicks.
* **Audit Trails**: Maintains a local JSON-based history of all scans for evidentiary purposes.

### Enterprise-Grade UI
* **Asynchronous Processing**: Built with PyQt6 and QThread to ensure smooth UI performance during network-heavy analysis.
* **Cyber-Brutalist Design**: High-contrast Dark Mode optimized for Security Operations Center (SOC) environments.

## Installation & Usage

### Option 1: Standalone Installer (Windows)
Download the latest QuishGuard_Setup.exe from the Releases page. No Python installation required.

### Option 2: Run from Source
1.  **Clone the Repository:**
    git clone https://github.com/JAMPANIKOMAL/QuishGuard.git
    cd QuishGuard

2.  **Install Dependencies:**
    pip install -r requirements.txt

3.  **Launch:**
    python main.py

## Architecture

* **Core Engine**: OpenCV and pyzbar for optical recognition.
* **Network Analysis**: Requests with custom headers for redirection tracing.
* **Interface**: PyQt6 with custom widgets and QSS styling.
* **Deployment**: PyInstaller with WinReg integration for native Windows installation.

## Disclaimer
This tool is intended for educational and defensive security purposes only. The developer assumes no responsibility for misuse. Always analyze suspicious files in an isolated sandbox environment.

**Developed by Jampani Komal**
