#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <gmp.h>
#include <assert.h>

int main(int argc, char *argv[]){

    mpz_t n, e, d, lambda_n, p, q, i, temp, one;
    int flag;

    // Init all numbers
    mpz_inits(n, e, d, lambda_n, p, q, i, temp, one, NULL);
    mpz_set_ui(one, 1);

    // Set p
    flag = mpz_set_str(p, argv[1], 10);
    assert(flag == 0);

    // Set q
    flag = mpz_set_str(q, argv[2], 10);
    assert(flag == 0);

    // Set n = p * q
    mpz_mul(n, p, q);

    // Set lambda_n = lcm(p - 1, q - 1)
    mpz_sub_ui(p, p, 1);
    mpz_sub_ui(q, q, 1);
    mpz_lcm(lambda_n, p, q);
    mpz_add_ui(p, p, 1);
    mpz_add_ui(q, q, 1);

    // Set e
    mpz_set_ui(i, 2);
    for(i; mpz_cmp(lambda_n, i) > 0; mpz_add_ui(i, i, 1)){
        mpz_gcd(temp, i, lambda_n);
        if(mpz_cmp(temp, one) == 0){
            mpz_set(e, i);
            break;
        }
    }

    // Set d (using modular_multiplicative_inverse built in function)
    mpz_invert(d, e, lambda_n);

    // Output keys to stdout
    printf("{\"n\":");
    mpz_out_str(stdout, 10, n);
    printf(",\"e\":");
    mpz_out_str(stdout, 10, e);
    printf(",\"d\":");
    mpz_out_str(stdout, 10, d);
    printf("}");

    // Clear mpz_t to stop memory leaks
    mpz_clears(n, e, d, lambda_n, p, q, i, temp, one);

}
