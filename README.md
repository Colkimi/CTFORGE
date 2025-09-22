# CTForge - CTF Challenge Generator

CTForge is a powerful command-line tool for generating Capture The Flag (CTF) challenges across multiple categories. Create realistic cybersecurity challenges for educational purposes, training, or competition events.

## 🚀 Features

- **Web Security Challenges**: SQL Injection, XSS, LFI, and Brute Force attacks
- **Cryptography Challenges**: Base64, ROT13, Vigenère Cipher, XOR, AES, and simplified RSA
- **Digital Forensics Challenges**: Steganography, EXIF metadata, PCAP analysis, and binary analysis
- **Automatic Flag Generation**: Unique UUID-based flags for each challenge
- **Complete Challenge Structure**: Includes hints, solution scripts, and README files
- **Ready-to-Deploy**: Generates Flask applications for web challenges

## 📋 Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## 🛠️ Installation

1. Clone or download the repository:
```bash
git clone https://github.com/Colkimi/CTFORGE.git
cd CTFORGE
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Usage

### Basic Usage

Generate a challenge using the command line:

```bash
python ctforge.py --type [web|crypto|forensics] --output [output_directory]
```

### Examples

**Generate a Web Security Challenge:**
```bash
python ctforge.py --type web --output challenges
```

**Generate a Cryptography Challenge:**
```bash
python ctforge.py --type crypto --output challenges
```

**Generate a Forensics Challenge:**
```bash
python ctforge.py --type forensics --output challenges
```

### Output Structure

Each generated challenge creates a directory containing:
- `flag.txt` - The challenge flag
- `README.md` - Challenge description and hints
- `SOLUTION.md` - Complete solution with explanations
- Challenge-specific files (see categories below)

## 🌐 Web Challenges

CTForge generates realistic web security challenges with vulnerabilities:

### SQL Injection
- Flask application with vulnerable database queries
- SQLite database with admin credentials
- Direct SQL query execution from user input

### Cross-Site Scripting (XSS)
- Vulnerable form that doesn't sanitize input
- Reflects user input directly in HTML
- Perfect for testing XSS payloads

### Local File Inclusion (LFI)
- File reading functionality with path traversal potential
- Attempts to restrict to base directory
- Includes sample files to read

### Brute Force
- Login form with admin credentials
- Flag embedded as the admin password
- Perfect for password cracking exercises

**Running Web Challenges:**
```bash
cd [challenge_directory]
python app.py
# Access at http://localhost:5000
```

## 🔐 Cryptography Challenges

### Base64 Encoding
- Simple Base64 encoded flags
- Includes decoding solution script

### ROT13 Caesar Cipher
- Classic rotation cipher
- Educational cryptanalysis exercise

### Vigenère Cipher
- Polyalphabetic substitution cipher
- Includes encryption key in hints

### XOR Encryption
- Single-byte XOR with random key
- Key range: 1-255 for brute force potential

### AES Encryption (Fernet)
- Modern symmetric encryption
- Uses Python's cryptography library
- Includes separate key file

### Simplified RSA
- Hex-encoded challenge (educational RSA concept)
- Introduction to asymmetric cryptography

## 🔍 Forensics Challenges

### Steganography
- JPEG images with hidden data
- Flag appended to image file
- Practice with steganography tools

### EXIF Metadata
- Images with embedded metadata
- Flag hidden in EXIF UserComment field
- Requires metadata analysis tools

### PCAP Network Analysis
- Generated network traffic files
- Flag embedded in UDP packets
- Practice with Wireshark/tshark

### Binary File Analysis
- ELF-format binary files
- Flag hidden within binary data
- Requires hex editors or strings command

**Suggested Forensics Tools:**
- `steghide`, `binwalk`, `xxd` (steganography)
- `exiftool` (metadata analysis)
- `wireshark`, `tshark` (network analysis)
- `strings`, `hexdump` (binary analysis)

## 🔧 Configuration

### Custom Output Directory
```bash
python ctforge.py --type web --output /path/to/custom/directory
```

### Generated Files
Each challenge includes:
- Unique directory name (e.g., `challenge_a1b2c3d4`)
- Challenge-specific files and databases
- Complete documentation and solutions

## 🏗️ Architecture

### Core Classes
- `ChallengeGenerator`: Main generation engine
- `ChallengeType`: Primary challenge categories
- `WebChallengeType`: Web vulnerability types
- `CryptoChallengeType`: Cryptographic methods
- `ForensicsChallengeType`: Forensics analysis types

### Challenge Generation Flow
1. Create unique challenge directory
2. Generate cryptographically random flag
3. Create challenge-specific files and databases
4. Generate documentation and solutions
5. Package complete challenge bundle

## 🎯 Educational Use Cases

- **Cybersecurity Training**: Hands-on vulnerability practice
- **CTF Competitions**: Rapid challenge creation for events
- **University Courses**: Practical security exercises
- **Penetration Testing Training**: Realistic attack scenarios
- **Security Awareness**: Demonstrate common vulnerabilities

## 🛡️ Security Considerations

- Challenges are designed for educational/controlled environments
- Web challenges include basic safety restrictions
- Do not deploy directly to production environments
- Use in isolated/sandboxed environments when possible

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional challenge types
- Enhanced difficulty levels
- More realistic scenarios
- Additional forensics file formats
- Advanced cryptographic challenges

## 📄 License

This project is open source. Please use responsibly for educational purposes.

## 🆘 Support

For issues, questions, or contributions:
- Create GitHub issues for bugs or feature requests
- Ensure all dependencies are properly installed
- Check Python version compatibility (3.7+)

## 📚 Example Workflow

```bash
# Generate a complete CTF challenge set
python ctforge.py --type web --output ctf_event
python ctforge.py --type crypto --output ctf_event  
python ctforge.py --type forensics --output ctf_event

# Your CTF event now has multiple challenges ready to deploy!
```

---

**Happy Hacking! 🚩**

*CTForge - Making cybersecurity education accessible, one challenge at a time.*
