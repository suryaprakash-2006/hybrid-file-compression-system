# Hybrid File Compression and Integrity Verification System

This project implements a Hybrid File Compression and Integrity Verification System that integrates low-level 8086 microprocessor programming with modern web technologies. The system demonstrates how assembly-level algorithms can be combined with high-level software frameworks to perform efficient file compression and decompression.

The core compression engine is implemented in 8086 Assembly Language using the EMU8086 emulator. It applies Run-Length Encoding (RLE) and pattern-based encoding techniques to compress text and structured data files. File handling operations such as open, read, write, and close are performed using DOS Interrupt 21H services, illustrating interrupt-driven programming and low-level data manipulation within the microprocessor environment.

The system also incorporates a Python-based backend built with Flask that acts as the controller between the web interface and the compression engines. It manages file uploads, invokes the appropriate compression module, and returns the processed files to the user. In addition to the 8086 compression engine, Python-based modules support modern compression algorithms and handle file types not processed by the assembly engine.

A web interface developed using HTML, CSS, and Bootstrap allows users to upload files, perform compression or decompression operations, and download the resulting output files. Compressed files produced by the assembly engine are stored in a custom Hybrid File Compression (.HFC) format.

To ensure reliability, the system includes an integrity verification mechanism that compares the original and decompressed files to confirm lossless compression.

Technologies Used
- 8086 Assembly Language (EMU8086)
- Python with Flask
- HTML, CSS, Bootstrap
- DOS Interrupt 21H File Services
- Run-Length Encoding (RLE)

System Workflow
User Upload → Backend Controller (Flask) → Compression Engine Selection → 8086 RLE Engine / Python Compression Module → Compressed File Generation → Integrity Verification → Download Result

Future Enhancements
- Support for advanced compression algorithms such as Huffman Coding, LZMA, and Deflate
- Improved handling of binary and multimedia file formats
- Compression performance visualization and statistics dashboard
- Support for larger files and streaming compression
- Migration of the frontend to a modern framework such as React


