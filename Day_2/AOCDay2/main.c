//
//  main.c
//  AdventOfCode2022Test
//
//  Created by Badger on 27/11/2023.
//

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define RED_MASK    0x000000ff
#define GREEN_MASK  0x0000ff00
#define BLUE_MASK   0x00ff0000

#define RED_SHIFT 0
#define GREEN_SHIFT 8
#define BLUE_SHIFT 16

typedef char** t_string_array;

void foo(char**, size_t);

void from_asm(int i) {
    printf("I got %d from assembly", i);
}

// WARNING: This is sensitive to the format of the input file. It requires
// every line to end in \n, i.e. we need a blank line at the end of the
// input.
size_t get_num_lines(FILE* f) {
    fpos_t pos;
    if (fgetpos(f, &pos) != 0) {
        fprintf(stderr, "Couldn't get file position.\n");
        exit(1);
    }
    char ch;
    size_t count = 0;
    do {
        ch = fgetc(f);
        if (ch == '\n')
            count++;
    } while (ch != EOF);
    fsetpos(f, &pos);
    return count;
}

int read_lines_from_file(const char* filename, t_string_array* pStrArray, size_t* numLines) {
    FILE* f = fopen(filename, "r");
    if (f == NULL) {
        fprintf(stderr, "Cannot open input file %s\n", filename);
        return 1;
    }
    *numLines = get_num_lines(f);
    *pStrArray = calloc(*numLines, sizeof(char*));
    
    size_t len = 0;
    ssize_t read;
    char* readline = NULL;
    t_string_array currentLine = *pStrArray;
    while ((read = getline(&readline, &len, f)) != -1) {
        if (currentLine >= *pStrArray + *numLines) {
            fprintf(stderr, "Buffer overrun!\n");
            exit(1);
        }
        *currentLine = calloc(strlen(readline) + 1, sizeof(char));
        strncpy(*currentLine, readline, strlen(readline));
        
        // To make parsing easier, we change the newline to a semi-colon.
        // That means we can split the string by semi-colons.
        if ((*currentLine)[strlen(readline) - 1] != '\n') {
            fprintf(stderr, "Bad input line. Expected it to end in \\n!\n");
            exit(1);
        }
        (*currentLine)[strlen(readline) - 1] = ';';
        ++currentLine;
    }

    if (readline)
        free(readline);
    fclose(f);
    return 0;
}

// This is very sketchy. It's bodged together and makes a lot of
// assumptions about input format.
int32_t parse_draw(const char* draw) {
    int32_t ret = 0;
    int val;
    // Max size needed is 5 for green
    char colour[6] = {0};
    const char* index = draw;
    while (index != NULL) {
        index += 1;
        sscanf(index, "%d %s", &val, colour);
        index = strstr(index, ",");
        
        if (strstr(colour, "blue")) {
            int32_t shifted = val << BLUE_SHIFT;
            ret &= shifted;
        } else if (strstr(colour, "green")) {
            int32_t shifted = val << GREEN_SHIFT;
            ret &= shifted;
        } else if (strstr(colour, "red")) {
            int32_t shifted = val << RED_SHIFT;
            ret &= shifted;
        } else {
            fprintf(stderr, "You f*@cked up!");
            exit(1);
        }
    }
    return 0;
}

int32_t** parse_lines(const char** lines, size_t num_lines) {
    int32_t** ret = calloc(num_lines, sizeof(int32_t*));
    int32_t** current_game = ret;
    for (size_t iline = 0; iline < num_lines; iline ++) {
        const char* line = lines[iline];
        // Need to copy the line because strtok modifies strings
        // in place.
        char* lineCopy = calloc(strlen(line) + 1, sizeof(char));
        strcpy(lineCopy, line);
        char* firstDraw = strstr(lineCopy, ":");
        if (firstDraw == NULL) {
            fprintf(stderr, "Failed to parse line: %s", line);
            exit(1);
        }
        // Move firstDraw pointer past the colon.
        firstDraw += 1;
        
        // Count the number of draws in each game
        size_t numDraws = 0;
        char* tok = strtok(firstDraw, ";");
        while (tok != NULL) {
            numDraws++;
            tok = strtok(NULL, ";");
        }
        
        // Allocate space for the number of draws
        *current_game = calloc(numDraws + 1, sizeof(int32_t));
        memset(ret, 0, numDraws + 1);
        
        int32_t* draw = *current_game;
        tok = strtok(firstDraw, ";");
        while (tok != NULL) {
            *draw = parse_draw(tok);
            draw++;
            tok = strtok(NULL, ";");
        }
        
        free(lineCopy);
        current_game++;
    }
    return ret;
}

int32_t count_from_draw(int32_t* draw, int32_t mask, int32_t shift) {
    return (*draw & mask) >> shift;
}

bool game_is_good(int32_t* draws) {
    static const int32_t max_red = 12;
    static const int32_t max_green = 13;
    static const int32_t max_blue = 14;
    
    bool good_game = true;
    int32_t* draw = draws;
    while (draw != NULL) {
        int32_t num_red = count_from_draw(draw, RED_MASK, RED_SHIFT);
        int32_t num_green = count_from_draw(draw, GREEN_MASK, GREEN_SHIFT);
        int32_t num_blue = count_from_draw(draw, BLUE_MASK, BLUE_SHIFT);
        
        if (num_red > max_red || num_green > max_green || num_blue > max_blue) {
            good_game = false;
            break;
        }
        
        draw++;
    }
    return good_game;
}

int main(int argc, const char * argv[]) {
    
    char** lines;
    size_t num_lines;
    if (read_lines_from_file("test_input.txt", &lines, &num_lines) != 0) {
        exit(1);
    }

    int32_t** games = parse_lines(lines, num_lines);
    for (size_t i = 0; i < num_lines; ++i) {
        printf("%s\n", *(lines + i));
    }
    
    free(lines);
    
    int32_t sum = 0;
    int32_t igame = 1;
    int32_t** game = games;
    while (game != NULL) {
        if (game_is_good(*game)) {
            sum += igame;
        }
        igame++;
        game++;
    }
    
    printf("Answer to part 1 is %d", sum);
    
    
//    foo(lines, num_lines);
    // TODO: Release games
    printf("The world did not end\n");
    return 0;
}
