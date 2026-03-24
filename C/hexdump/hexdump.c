#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>

#define MAX_BUFF_SIZE 1024 * 500
#define IS_PRINTABLE_ASCII(c) (((c) > 31) && ((c) < 127))
#define NON_PRINTABLE_ASCII '.'


size_t file_open_and_read(char *filepath , char *buffer , size_t size){
    
    //check if file exists
    if (access(filepath, F_OK) != 0){
        fprintf(stderr,"Error: File %s does not exist\n",filepath);
        exit(1);
    }

    //open file
    FILE *f = fopen(filepath,"r");
    if (f == NULL){
         fprintf(stderr,"Error: File %s could not be open\n",filepath);
        exit(1);
    }

    //check file size
    size_t filesize;
    fseek(f, 0L, SEEK_END);
    filesize = ftell(f);
    fseek(f, 0L, SEEK_SET);

    if (filesize > size){
        printf("FIle too big to handle, sorry %d B . Max size allowed : %n B\n",filesize,size);
        exit(1);
    }

    //After checks , Read file to buffer
    fread(buffer, sizeof(char),filesize, f);
    fclose(f);
    
return filesize;
}

int hexdump(void *buffer, size_t size){
    uint8_t *data = buffer;
    size_t i,j;

    for (i = 0; i < size; i++){
        uint8_t byte = data[i];

        // at the start of each row, print address
        if ((i % 16) == 0) {
            printf("%08lx ", i);
        }
        
        if (i % 8 == 0) { printf(" "); }
        
        printf("%02x ",byte);
    
        //if row is over
        if (((i % 16) == 15) || (i == size - 1)){
            
            for (j = 0; j < 15 - (i % 16); j++) { printf("   "); }
            if (i % 8 == 0) { printf(" "); }

            //print ascii
            printf(" |");
            for (j = (i - (i % 16)); j <= i; j++) {
	            printf("%c", IS_PRINTABLE_ASCII(data[j]) ? data[j] : NON_PRINTABLE_ASCII);
            }
            printf("|\n");
        }
    }
    printf("%08lx\n", i);
}



int main(int argc , char **argv ) {
    if (argc != 2){
        fprintf(stderr,"Example : %s <file_name>\n",argv[0]);
        exit(1);
    }
    char *input_file = argv[1];
    char buffer[MAX_BUFF_SIZE] = {0};

    size_t file_size = file_open_and_read(input_file,buffer, MAX_BUFF_SIZE);
    hexdump(buffer,file_size);
}
