#include "helpers.h"
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0 ; i < height ; i ++)
    for (int j = 0 ; j < width ; j ++){
            int newcolor = (image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3;
            image[i][j].rgbtBlue = newcolor;
            image[i][j].rgbtGreen = newcolor;
            image[i][j].rgbtRed = newcolor;
        }

}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0 ; i < height ; i ++){
        RGBTRIPLE temprow[width];
        for (int j = width ; j >= 0 ; j --){
            temprow[j].rgbtBlue = image[i][width - j].rgbtBlue;
            temprow[j].rgbtGreen = image[i][width - j].rgbtGreen;
            temprow[j].rgbtRed = image[i][width - j].rgbtRed;
        }
        for (int j = 0 ; j < width ; j++){
            image[i][j].rgbtBlue = temprow[j].rgbtBlue;
            image[i][j].rgbtGreen = temprow[j].rgbtGreen;
            image[i][j].rgbtRed = temprow[j].rgbtRed;
        }
    }
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE og_image_copy[height][width];
    for (int i = 0; i < height; i++)
    for (int j = 0; j < width; j++)
    og_image_copy[i][j] = image[i][j];


    for (int i = 0; i < height; i++)
    for (int j = 0; j < width; j++){
            int red_sum = 0;
            int blue_sum = 0;
            int green_sum = 0;

            for (int row = -1; row < 2; row++)
            for (int col = -1; col < 2; col++){
                  bool is_out = i + row < 0 || i + row >= height;

                  if (is_out){
                        continue;
                    }

                    red_sum += og_image_copy[i + row][j + col].rgbtRed;
                    blue_sum += og_image_copy[i + row][j + col].rgbtBlue;
                    green_sum += og_image_copy[i + row][j + col].rgbtGreen;
           }

            image[i][j].rgbtRed = red_sum / 9;
            image[i][j].rgbtGreen = green_sum / 9;
            image[i][j].rgbtBlue = blue_sum / 9;
    }
}


// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{


    RGBTRIPLE og_image_copy[height][width];
    for (int i = 0; i < height; i++)
    for (int j = 0; j < width; j++)
    og_image_copy[i][j] = image[i][j];



    int gx[3][3] = {{-1 , 0 , 1},
                    {-2 , 0 , 2},
                    {-1 , 0 , 1}} ;




    int gy[3][3] = {{ -1 , -2 , -1},
                    {0 , 0 , 0},
                    {1 , 2 , 1}} ;






    for (int i = 1 ; i < height - 1 ; i++)
    for (int j = 1 ; j < width - 1 ; j++){


        int gxblue = 0;
        int gyblue = 0;
        int gxgreen = 0;
        int gygreen = 0;
        int gxred = 0;
        int gyred = 0;


        for (int row = -1 ; row < 2 ; row ++)
        for (int col = -1 ; col < 2 ; col ++){
            gxblue += og_image_copy[i + row][j + col].rgbtBlue  * gx[row + 1][col + 1];
            gyblue += og_image_copy[i + row][j + col].rgbtBlue  * gy[row + 1][col + 1];
            gxgreen += og_image_copy[i + row][j + col].rgbtGreen  * gx[row + 1][col + 1];
            gygreen += og_image_copy[i + row][j + col].rgbtGreen  * gy[row + 1][col + 1];
            gxred += og_image_copy[i + row][j + col].rgbtRed  * gx[row + 1][col + 1];
            gyred += og_image_copy[i + row][j + col].rgbtRed  * gy[row + 1][col + 1];

        }

            image[i][j].rgbtBlue = round(sqrt(gxblue * gxblue + gyblue * gyblue));
            image[i][j].rgbtGreen = round(sqrt(gxgreen * gxgreen + gygreen * gygreen));
            image[i][j].rgbtRed = round(sqrt(gxred * gxred + gyred * gyred));

        //printf("r%i g%i b%i\n",image[i][j].rgbtBlue , image[i][j].rgbtGreen , image[i][j].rgbtRed);
    }
}
