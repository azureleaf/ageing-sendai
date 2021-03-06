#include <stdio.h>
#include <string.h>
#include <iconv.h>
#include <stdlib.h>
#include <unistd.h> // access()

#define S_SIZE 1024      // Length of a line in the file
#define V_SIZE 30        // Length of a value between commas
#define FLD_NUM 14       // Number of header fields: 都道府県名, 市区町村名...
#define FLD_NAME_SIZE 30 // Length of a field name. The longest "住居表示フラグ" has 23B

// Position of fields in the source CSV header columns
#define WARD 1
#define OAZA 2
#define KOAZA 3
#define LAT 8
#define LON 9

typedef struct town
{
    char pref[FLD_NAME_SIZE];
    char ward[FLD_NAME_SIZE];  // important
    char oaza[FLD_NAME_SIZE];  // important
    char koaza[FLD_NAME_SIZE]; // important
    char lot[FLD_NAME_SIZE];
    char coordSys[4];
    char x[FLD_NAME_SIZE];
    char y[FLD_NAME_SIZE];
    char lat[FLD_NAME_SIZE]; // important
    char lon[FLD_NAME_SIZE]; // important
    char isNewAddrSys[3];
    char isRep[3];
    char isNotUpdated[3];
    char isUpdated[3];
} town_t;

// File paths
char miyagi_sjis_path[] = "./raw/koaza-positions/04_2018.csv"; // source
char miyagi_utf8_path[] = "./results/miyagi_pos_utf8.csv";
char koaza_pos_path[] = "./results/koaza_pos.csv";

// Prototypes
int filter_sendai_pos(void);
int sjis2utf8(char *, char *);
int has_expected_header(char *);
int count_comma(char *, int, int);
int split_by_commas(char *, char[FLD_NUM][V_SIZE]);
int filter_koaza(char[V_SIZE], char[V_SIZE], char[V_SIZE]);
int test_split_by_commas(void);

// Wrapper
int main()
{
    // If UTF-8 file doesn't exist, generate it
    if (access(miyagi_utf8_path, F_OK) == -1)
        if (sjis2utf8(miyagi_sjis_path, miyagi_utf8_path))
            return 1;

    // If Sendai town position file doesn't exist, generate it
    if (access(koaza_pos_path, F_OK) == -1)
        if (filter_sendai_pos())
            return 1;

    filter_koaza("\"仙台市青葉区\"", "\"芋沢\"", "\"畑前\"");

    return 0;
}

// Extract rows of Sendai towns from all the towns in Miyagi, then save it to the file
// Miyagi 267k towns => Sendai 49k towns
int filter_sendai_pos(void)
{
    FILE *fi, *fo;
    char buff[S_SIZE];
    char values[FLD_NUM][V_SIZE];

    if ((fi = fopen(miyagi_utf8_path, "r")) == NULL)
    {
        printf("ERROR: source file not found!");
        return 1;
    };

    // Overwrite if dst file already exists
    fo = fopen(koaza_pos_path, "w");

    // Output the header if the header is the one expected
    fgets(buff, S_SIZE, fi);
    if (!has_expected_header(buff))
        return 1;
    fputs(buff, fo);

    // Filter the rows of towns in Sendai city
    while (fgets(buff, S_SIZE, fi) != NULL)
    {
        split_by_commas(buff, values);
        if (strstr(values[WARD], "仙台市") != NULL)
            fputs(buff, fo);
    }

    fclose(fi);
    fclose(fo);

    printf("INFO: Saved Sendai towns as: %s\n", koaza_pos_path);

    return 0;
}

// Filter the specified koaza and show it on the console
int filter_koaza(char ward[V_SIZE], char oaza[V_SIZE], char koaza[V_SIZE])
{
    FILE *fi;
    char buff[S_SIZE];
    char values[FLD_NUM][V_SIZE];
    int row_i = 0;

    if ((fi = fopen(koaza_pos_path, "r")) == NULL)
    {
        printf("ERROR: Couldn't find the src file: %s\n", koaza_pos_path);
        return 1;
    }

    // Output the header if the header is the one expected
    fgets(buff, S_SIZE, fi);
    if (!has_expected_header(buff))
        return 1;
    row_i++;

    while (fgets(buff, S_SIZE, fi) != NULL)
    {
        // printf("buff: %s", buff);
        split_by_commas(buff, values);

        if (strcmp(values[WARD], ward) == 0 &&
            strcmp(values[OAZA], oaza) == 0 &&
            strcmp(values[KOAZA], koaza) == 0)
            printf("%d: %s", row_i, buff);
        row_i++;
    }

    fclose(fi);

    return 0;
}

// Get a Shift-JIS file, return it with UTF-8 encoding
int sjis2utf8(char *sjis_path, char *utf8_path)
{
    iconv_t icd;
    FILE *fp_src, *fp_dst;
    char s_src[S_SIZE], s_dst[S_SIZE];
    char *p_src, *p_dst;
    size_t n_src, n_dst;

    icd = iconv_open("UTF-8", "Shift_JIS");
    fp_src = fopen(sjis_path, "r");
    fp_dst = fopen(utf8_path, "w");

    while (1)
    {
        fgets(s_src, S_SIZE, fp_src);
        if (feof(fp_src))
            break;
        p_src = s_src;
        p_dst = s_dst;
        n_src = strlen(s_src);
        n_dst = S_SIZE - 1;
        while (0 < n_src)
        {
            iconv(icd, &p_src, &n_src, &p_dst, &n_dst);
        }
        *p_dst = '\0';
        fputs(s_dst, fp_dst);
    }

    fclose(fp_dst);
    fclose(fp_src);
    iconv_close(icd);

    printf("INFO: Saved UTF-8 encoded file as: %s\n", miyagi_utf8_path);
    return 0;
}

// Check if the string passed includes the expected key fields
int has_expected_header(char *s)
{
    char fields[FLD_NUM][FLD_NAME_SIZE];

    split_by_commas(s, fields);

    // Return 1 if all the field names match, if not return 0
    return strcmp(fields[WARD], "\"市区町村名\"") ==
           strcmp(fields[OAZA], "\"大字・丁目名\"") ==
           strcmp(fields[KOAZA], "\"小字・通称名\"") ==
           strcmp(fields[LAT], "\"緯度\"") ==
           strcmp(fields[LON], "\"経度\"") == 0;
}

// Count the number of commas in the string given
int count_comma(char *text, int i, int count)
{
    if (!text[i])
        return count;
    else
    {
        if (text[i] == ',')
            count++;
        i++;
        count_comma(text, i, count); // recursion
    }
}

// Get a line, split it by comma, return it as an array
// Using fscanf() instead of this function may be better
int split_by_commas(char *s, char result[FLD_NUM][V_SIZE])
{
    char *tp; // pointer to the token found
    int i = 0;
    char s_copy[S_SIZE];

    // Copy the original string because strtok() alters the source
    strcpy(s_copy, s);

    tp = strtok(s_copy, ",");
    strcpy(result[i], tp);
    while ((tp = strtok(NULL, ",")) != NULL)
        strcpy(result[++i], tp);

    return 0;
}

// Unit test
int test_split_by_commas(void)
{
    char teststr[] = "one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,thirteen,fourteen";
    char result[FLD_NUM][V_SIZE];

    printf("Original line before split: %s\n", teststr);

    split_by_commas(teststr, result);
    printf("Number of the result array elements: %ld\n", sizeof(result) / sizeof(result[0]));
    int i;
    for (i = 0; i < FLD_NUM; ++i)
    {
        printf("Elem: %s\n", result[i]);
    }

    printf("Original line after split: %s\n", teststr);

    return 0;
}