**Clipkeeper** is a windows clipboard history manager designed to optimize your workflow by providing a persistent, searchable, and organized record of your clipboard content.

---

## Features

### **Comprehensive Clipboard Management**
- **Real-Time Monitoring:** Automatically capture clipboard content (text and images) as you work.
- **Persistent Storage:** Save clipboard history securely in a local SQLite database for easy retrieval.
- **Searchable History:** Locate previous entries with a keyword-based search system.

### **Web Interface**
- **Responsive Design:** Access your clipboard history via a clean, user-friendly web interface.
- **Real-Time Updates:** See new clipboard items appear instantly, without refreshing the page.
- **Integrated Management:** Easily copy or delete clipboard items directly from the interface.

### **Command-Line Tools**
- **History Display:** View your clipboard history in the terminal.
- **Search Utility:** Search for specific items using patterns or keywords.
- **Management Tools:** Clear clipboard history or copy specific entries with ease.

### **Secure and Private**
- **Local-Only Storage:** Data is stored on your machine, ensuring complete privacy.
- **Deduplication:** Duplicate entries are automatically handled to maintain a clean history.

---

## Installation

### Prerequisites
- **Operating System:** Windows 10 or 11
- **Python:** Version 3.8 or higher

### Install Clipkeeper
Install Clipkeeper with pip:

```bash
pip install clipkeeper
```

This command will install all required dependencies and set up Clipkeeper for immediate use.

---

## Usage

### **Starting Clipkeeper**
Run the following command to start the clipboard manager and launch the web interface:

```bash
clipkeeper start
```

By default, the web interface is available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

### **Command-Line Options**
#### View Clipboard History
Display saved clipboard entries in the terminal:
```bash
clipkeeper history
```

#### Search Clipboard History
Find specific items using a keyword search:
```bash
clipkeeper search "keyword"
```

#### Clear Clipboard History
Remove all saved clipboard content:
```bash
clipkeeper clear
```

---

## Configuration

### **Default Settings**
Configuration files are stored in the following location:
```
%USERPROFILE%\.clipkeeper\config.ini
```

Settings can be overridden using command-line options when starting the application.

---

## Web Interface

The Clipkeeper web interface is a central hub for managing your clipboard history. 

### Key Features:
- **Search Bar:** Quickly find specific entries.
- **History Grid:** View your clipboard items in a well-organized grid layout.
- **Actions:** Copy, delete, or view items with a single click.

![Screenshot of Clipkeeper Web Interface](https://cdn.discordapp.com/attachments/1199094088641810575/1308782592396623932/image.png?ex=673f3246&is=673de0c6&hm=f56926fdc29987379dc94b0add72c95426f1af63c9417d4a9d33cd84324f3b63&)  

---

## Roadmap

### Current Features
- Windows-only support
- Text and image clipboard tracking
- Web interface with real-time updates
- Local, secure storage using SQLite

### Planned Features
- Cross-platform support (macOS and Linux)
- Enhanced UI/UX with tagging and categorization
- Clipboard history export/import
- API for integration with external tools

---

## License

Clipkeeper is released under the **MIT License**. See the `LICENSE` file for details.

---

## Contact

For support or questions, feel free to reach out by opening an issue on GitHub.

---