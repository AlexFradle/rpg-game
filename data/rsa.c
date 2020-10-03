#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#define len(x)  (sizeof(x) / sizeof((x)[0]))


unsigned long long gcd(unsigned long long a, unsigned long long b) {
    // Using Euclid's algorithm
    unsigned long long t;
    while(b != 0){
        t = b;
        b = a % b;
        a = t;
    }
    return a;
}

unsigned long long check_coprime(unsigned long long a, unsigned long long b) {
    // in pyhton -> return 1 if gcd(a, b) == 1 else 0
    return (gcd(a, b) == 1 ? 1 : 0);
}

unsigned long long get_coprime(unsigned long long n) {
    unsigned long long i;
    for(i = 2; i < n; i++){
        if(check_coprime(n, i) == 1){
            return i;
        }
    }
}

unsigned long long check_prime(unsigned long long n) {
    unsigned long long a = get_coprime(n);
    unsigned long long a_pow_n = (unsigned long long) pow(a, (n - 1));
    // in pyhton -> return 1 if a_pow_n % n == 1 else 0
    return (a_pow_n % n == 1 ? 1 : 0);
}

unsigned long long lcm(unsigned long long a, unsigned long long b) {
    return abs(a * b) / gcd(a, b);
}

unsigned long long modular_multiplicative_inverse(unsigned long long a, unsigned long long b) {
    a = a % b;
    for(unsigned long long i = 1; i < b; i++){
        if((a * i) % b == 1){
            return i;
        }
    }
}

struct Keys{
    unsigned long long n;
    unsigned long long e;
    unsigned long long d;
};

struct Keys make_keys(unsigned long long p, unsigned long long q) {
    unsigned long long n, lambda_n, e, d;
    struct Keys k;
    n = p * q;
    lambda_n = lcm(p - 1, q - 1);
    e = 0;
    for(int i = 2; i < lambda_n; i++){
        if(check_coprime(i, lambda_n) == 1){
            e = i;
            break;
        }
    }
    d = modular_multiplicative_inverse(e, lambda_n);
    k.n = n;
    k.e = e;
    k.d = d;
    return k;
}

unsigned long long encrypt(int m, unsigned long long e, unsigned long long n) {
    return ((unsigned long long) pow(m, e)) % n;
}

unsigned long long decrypt(unsigned long long c, unsigned long long d, unsigned long long n) {
    printf("c = %llu, d = %llu\n", c, d);
    return ((unsigned long long) pow(c, d)) % n;
}

int main() {
    struct Keys final_keys;
    
    final_keys = make_keys(53, 61);
    printf("n = %llu\ne = %llu\nd = %llu\n", final_keys.n, final_keys.e, final_keys.d);
    
    char message[] = "Test";

    unsigned long long encrypted[strlen(message)];
    for(int i = 0; i < strlen(message); i++){
        encrypted[i] = encrypt((int)message[i], final_keys.e, final_keys.n);
        printf("%llu ", (int)message[i]);
    }

    printf("\n");

    unsigned long long decrypted[len(encrypted)];
    for(int i = 0; i < len(encrypted); i++){
        decrypted[i] = decrypt(encrypted[i], final_keys.d, final_keys.n);
        printf("%llu ", encrypted[i]);
    }

    printf("\n");

    for(int i = 0; i < len(decrypted); i++){
        printf("%d ", decrypted[i]);
    }

}