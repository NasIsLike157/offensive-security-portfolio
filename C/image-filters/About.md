
This project is a C-based image processing program developed as part of the `CS50` course. It applies various filters to `BMP` images by directly manipulating pixel data in memory.

All filter logic was implemented from scratch, including:
- **Grayscale** – converts images by averaging `RGB` color channels  
- **Reflection** – mirrors the image horizontally  
- **Blur** – applies a box blur using neighboring pixel averaging  
- **Edge Detection** – implements the Sobel operator to detect edges  

The program operates on raw bitmap structures, providing hands-on experience with memory management, multi-dimensional arrays, and low-level image representation.

This project was designed to strengthen understanding of:
- C programming and pointer-based data manipulation  
- Byte-File processing fundamentals  
- Algorithm implementation for real-world data structures  

Compilation:
```
> make
```

Execution:
```
> ./filter -b images/courtyard.bmp out.bmp
```