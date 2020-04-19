#include <stdio.h>
#include <string.h>
#include <iconv.h>
#include <unistd.h> // access()

#define S_SIZE 1024    // Length of a line in the file
#define V_SIZE 30      // Length of a value between commas
#define ALL_F_NUM 14   // number of header fields: 都道府県名, 市区町村名...
#define KEY_F_NUM 5    // number of key header fields: ward, oaza, koaza, lat, lon
#define F_NAME_SIZE 30 // e.g. "住居表示フラグ" is 21 Bytes

// Position of fields in the source CSV header columns
#define WARD 1
#define OAZA 2
#define KOAZA 3
#define LAT 8
#define LON 9

// File paths
char miyagi_sjis_path[] = "../raw/koaza-positions/04_2018.csv"; // source
char miyagi_utf8_path[] = "./miyagi_pos_utf8.csv";
char sendai_path[] = "./sendai_pos.csv";
char koaza_pos_path[] = "./koaza_pos.csv";

// Prototypes
int filter_sendai_pos(void);
int sjis2utf8(char *, char *);
int has_expected_header(char *);
int count_comma(char *, int, int);
int split_by_commas(char *, char[ALL_F_NUM][V_SIZE]);
int calc_koaza_pos(void);
int test_split_by_commas(void);

// Wrapper
int main()
{
    // test_split_by_commas();

    // Check existance of UTF-8 file
    if (access(miyagi_utf8_path, F_OK) == -1)
        if (sjis2utf8(miyagi_sjis_path, miyagi_utf8_path))
            return 1;

    filter_sendai_pos();
    calc_koaza_pos();

    return 0;
}

// Test function
int test_split_by_commas(void)
{
    char teststr[] = "one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,thirteen,fourteen";
    char result[ALL_F_NUM][V_SIZE];

    printf("Original line before split: %s\n", teststr);

    split_by_commas(teststr, result);
    printf("Number of the result array elements: %ld\n", sizeof(result) / sizeof(result[0]));
    int i;
    for (i = 0; i < ALL_F_NUM; ++i)
    {
        printf("Elem: %s\n", result[i]);
    }

    printf("Original line after split: %s\n", teststr);

    return 0;
}

// Extract rows of Sendai towns from all the towns in Miyagi, then save it to the file
int filter_sendai_pos(void)
{
    FILE *fi, *fo;
    char buff[S_SIZE];

    if (access(sendai_path, F_OK) != -1)
    {
        printf("INFO: Skipped the file generation. (\"%s\" already exists)\n", sendai_path);
        return 0;
    }

    if ((fi = fopen(miyagi_utf8_path, "r")) == NULL)
    {
        printf("ERROR: source file not found!");
        return 1;
    };

    if ((fo = fopen(sendai_path, "w")) == NULL)
    {
        printf("ERROR: couldn't specify the output file path.\n");
        return 1;
    }

    // Output the header if the header is the one expected
    fgets(buff, S_SIZE, fi);
    if (!has_expected_header(buff))
        return 1;
    fputs(buff, fo);

    // Filter the rows of towns in Sendai city
    char keyword[] = "仙台市";
    while (fgets(buff, S_SIZE, fi) != NULL)
    {
        if (strstr(buff, keyword) != NULL)
            fputs(buff, fo);
    }

    fclose(fi);
    fclose(fo);

    printf("INFO: Saved Sendai towns as: %s\n", sendai_path);

    return 0;
}

// Calculate the central position coordinates of every Koaza
int calc_koaza_pos(void)
{
    FILE *fi, *fo;
    char buff[S_SIZE];
    char values[ALL_F_NUM][V_SIZE];
    int row_i = 0;
    char keyword[] = "\"上愛子\"";

    if ((fi = fopen(sendai_path, "r")) == NULL)
    {
        printf("ERROR: couldn't find the file: %s\n", sendai_path);
        return 1;
    }

    if ((fo = fopen(koaza_pos_path, "w")) == NULL)
    {
        printf("ERROR: couldn't specify the output path: %s\n", koaza_pos_path);
        return 1;
    }

    // Output the header if the header is the one expected
    fgets(buff, S_SIZE, fi);
    if (!has_expected_header(buff))
        return 1;
    fputs(buff, fo);

    while (fgets(buff, S_SIZE, fi) != NULL && row_i < 5)
    {
        // printf("buff: %s", buff);
        split_by_commas(buff, values);
        printf("values: %s\n", values[OAZA]);

        if (strstr(values[OAZA], keyword) != NULL)
            fputs(buff, fo);

        row_i++;
    }

    fclose(fi);
    fclose(fo);

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

    printf("INFO: Converted SHIFT-JIS file into UTF-8 as: %s\n", miyagi_utf8_path);

    return 0;
}

// Check if the string passed includes the expected key fields
int has_expected_header(char *s)
{
    char fields[ALL_F_NUM][F_NAME_SIZE];

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
int split_by_commas(char *s, char result[ALL_F_NUM][V_SIZE])
{
    char *tp; // pointer to the token found
    int i = 0;
    char s_copy[S_SIZE];

    // Copy the original string because "strtok" alter the source one
    strcpy(s_copy, s);

    tp = strtok(s_copy, ",");
    strcpy(result[i], tp);
    while ((tp = strtok(NULL, ",")) != NULL)
        strcpy(result[++i], tp);

    return 0;
}