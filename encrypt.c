#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gmp.h>
#include <assert.h>
#include <string.h>

int main(int argc, char *argv[]){

    mpz_t n, e, c, m, temp;
    int flag;

    // Init all numbers
    mpz_inits(n, e, c, m, temp, NULL);

    // Set n
    flag = mpz_set_str(n, argv[1], 10);
    assert(flag == 0);

    // Set e
    flag = mpz_set_str(e, argv[2], 10);
    assert(flag == 0);

    // Set message
    char message[1024];
    strcpy(message, argv[3]);

    // Encrypt message
    for(int i = 0; i < strlen(message); i++){
        mpz_set_ui(m, (int)message[i]);
        mpz_powm(temp, m, e, n);
        mpz_out_str(stdout, 10, temp);
        printf("\n");
    }

    // Clear mpz_t to stop memory leaks
    mpz_clears(n, e, m, temp, c);

}

