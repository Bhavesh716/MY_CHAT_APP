#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ctype.h>
#include <sys/select.h>

#define FILE_NAME "chat.txt"
#define MAX_LEN 1024

char encode_char(char c) {
    if (isalpha(c)) {
        char base = islower(c) ? 'a' : 'A';
        return (char)(base + (c - base + 5) % 26);
    } else if (isdigit(c)) {
        return (char)(((c - '0' + 3) % 10) + '0');
    } else if (c == ' ') {
        return '`';
    } else {
        return c;
    }
}

char decode_char(char c) {
    if (isalpha(c)) {
        char base = islower(c) ? 'a' : 'A';
        return (char)(base + (c - base + 21) % 26); // -5 mod 26
    } else if (isdigit(c)) {
        return (char)(((c - '0' + 7) % 10) + '0'); // -3 mod 10
    } else if (c == '`') {
        return ' ';
    } else {
        return c;
    }
}

void encode_and_write(const char *msg, int is_self) {
    FILE *f = fopen(FILE_NAME, "a");
    if (!f) return;

    if (is_self)
        fprintf(f, "%%%s\n", msg); // % prefix for sender
    else
        fprintf(f, "%s\n", msg);   // no prefix for receiver

    fclose(f);
}

void decode_and_print(const char *line, int self_side) {
    char decoded[MAX_LEN];
    int i;
    for (i = 0; line[i] && line[i] != '\n'; ++i) {
        decoded[i] = decode_char(line[i]);
    }
    decoded[i] = '\0';

    if (self_side) {
        printf("S: %s\n", decoded);
    } else {
        printf("R: %s\n", decoded);
    }
}

int is_palindrome(const char *str) {
    int l = 0, r = strlen(str) - 1;
    while (l < r) {
        if (tolower(str[l]) != tolower(str[r]))
            return 0;
        l++; r--;
    }
    return 1;
}

int main() {
    char input[MAX_LEN];
    char code[10];
    int is_self = 0;
    long last_pos = 0;

    printf("Enter string to check: ");
    fgets(code, sizeof(code), stdin);
    code[strcspn(code, "\n")] = 0;

    if (strcmp(code, "007") == 0) {
        is_self = 1;
        //printf("Logged in as Gf (S:)\n");
    } else if (strcmp(code, "016") == 0) {
        is_self = 0;
        //printf("Logged in as You (R:)\n");
    } else {
        if (is_palindrome(code)) {
            printf("Palindrome: Yes\n");
        } else {
            printf("Palindrome: No\n");
        }
        return 0;
    }

    // Read and decode full history first
    FILE *f = fopen(FILE_NAME, "r");
    if (f) {
        char line[MAX_LEN];
        while (fgets(line, sizeof(line), f)) {
            if (line[0] == '%') {
                if (is_self)
                    decode_and_print(line + 1, 1); // self side = S
                else
                    decode_and_print(line + 1, 0); // other = R
            } else {
                if (is_self)
                    decode_and_print(line, 0); // other = R
                else
                    decode_and_print(line, 1); // self side = S
            }
        }
        last_pos = ftell(f);
        fclose(f);
    }

    // Start live loop
    //printf("Start typing below:\n");

    while (1) {
        // Reading new messages
        FILE *rf = fopen(FILE_NAME, "r");
        if (rf) {
            fseek(rf, last_pos, SEEK_SET);
            char line[MAX_LEN];
            while (fgets(line, sizeof(line), rf)) {
                if ((line[0] == '%' && is_self) || (line[0] != '%' && !is_self)) {
                    // Skip your own
                } else {
                    if (line[0] == '%') {
                        decode_and_print(line + 1, is_self ? 0 : 1);
                    } else {
                        decode_and_print(line, is_self ? 1 : 0);
                    }
                }
                last_pos = ftell(rf);
            }
            fclose(rf);
        }

        // Check if there's input
        fd_set fds;
        struct timeval tv = {0, 100000};  // 0.1 sec

        FD_ZERO(&fds);
        FD_SET(STDIN_FILENO, &fds);

        int ret = select(STDIN_FILENO + 1, &fds, NULL, NULL, &tv);
        if (ret > 0 && FD_ISSET(STDIN_FILENO, &fds)) {
            if (fgets(input, sizeof(input), stdin)) {
                input[strcspn(input, "\n")] = 0;

                char encoded[MAX_LEN];
                for (int i = 0; input[i]; ++i) {
                    encoded[i] = encode_char(input[i]);
                }
                encoded[strlen(input)] = '\0';

                encode_and_write(encoded, is_self);
            }
        }
    }

    return 0;
}
