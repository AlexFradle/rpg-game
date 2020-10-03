#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gmp.h>
#include <assert.h>
#include <string.h>

int main(int argc, char *argv[]){

    mpz_t n, d, c, temp;
    int flag;

    // Init all numbers
    mpz_inits(n, d, c, temp, NULL);

    // Set n
    flag = mpz_set_str(n, argv[1], 10);
    assert(flag == 0);

    // Set d
    flag = mpz_set_str(d, argv[2], 10);
    assert(flag == 0);

    // Set c
    flag = mpz_set_str(c, argv[3], 10);
    assert(flag == 0);

    // Decrypt letter
    mpz_powm(temp, c, d, n);
    mpz_out_str(stdout, 10, temp);
    printf("\n");

    // Clear mpz_t to stop memory leaks
    mpz_clears(n, d, c, temp);

}