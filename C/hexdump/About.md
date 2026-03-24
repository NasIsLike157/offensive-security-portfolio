
This project is a custom `hexdump` utility written in C that reads a file into memory and displays its raw byte representation in both hexadecimal and `ASCII` formats.

The implementation mimics the behavior of standard tools like `hexdump`/`xxd`, printing:
- Memory offsets for each row  
- Hexadecimal byte values  
- Corresponding ASCII representation for printable characters  
Non-printable bytes are replaced with a placeholder character, allowing clear visualization of binary data.

The program includes:
- File validation and size checks  
- Buffered file reading into memory  
- Structured output formatting in fixed-width rows  
- Byte-level parsing using `uint8_t` for precise control  

This project was designed to strengthen understanding of low-level data representation, file I/O, and memory handling in C, while building a practical tool commonly used in debugging, reverse engineering, and binary analysis.