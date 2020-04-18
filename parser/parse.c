#include <stdio.h>
#include <string.h>
#include <iconv.h>
#include <unistd.h> // access()

#define S_SIZE 1024    // Length of a line in the file
#define V_SIZE 30      // Length of a value between commas
#define ALL_F_NUM 14   // number of header fields: 都道府県名, 市区町村名...
#define KEY_F_NUM 5    // number of key header fields: ward, oaza, koaza, lat, lon
#define F_NAME_SIZE 30 // e.g. "住居表示フラグ" is 21 Bytes

// Position of fields in the source CSV header
#define WARD 1
#define OAZA 2
#define KOAZA 3
#define LAT 8
#define LON 9

char miyagi_sjis_path[] = "../raw/koaza-positions/04_2018.csv";
char miyagi_utf8_path[] = "./miyagi_utf8.csv";
char sendai_path[] = "./ages_parsed.csv";

int parse_miyagi_csv(void);
int sjis2utf8(char *, char *);
int has_expected_header(char *);
int count_comma(char *, int, int);
int split(char *, char[ALL_F_NUM][V_SIZE]);

int main()
{
    // char teststr[] = "one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve, thirteen, fourteen";
    // char result[ALL_F_NUM][V_SIZE];
    // split(teststr, result);
    // printf("%ld", sizeof(result) / sizeof(result[0]));
    // int i;
    // for (i = 0; i < ALL_F_NUM; ++i)
    // {
    //     printf("%s", result[i]);
    // }

    // return 0;

    // Check existance of UTF-8 file
    if (access(miyagi_utf8_path, F_OK) == -1)
        if (sjis2utf8(miyagi_sjis_path, miyagi_utf8_path))
            return 1;

    if (!has_expected_header(miyagi_utf8_path))
        return 1;
    printf("Header format is successfully validated.");

    return 0;
}

int parse_miyagi_csv(void)
{
    FILE *fi, *fo;
    char buff[S_SIZE];

    if (access(sendai_path, F_OK) != -1)
    {
        printf("INFO: The file \"%s\" already exists\n", sendai_path);
        return 1;
    }

    // If the source file doesn't exist, generate it
    if ((fi = fopen(miyagi_utf8_path, "r")) == NULL)
    {
        sjis2utf8(miyagi_sjis_path, miyagi_utf8_path);

        // When the even file generation fails, abort
        if ((fi = fopen(miyagi_utf8_path, "r")) == NULL)
        {
            printf("ERROR: source file not found!");
            return 1;
        }
    };

    if ((fo = fopen(sendai_path, "w")) == NULL)
    {
        printf("ERROR: couldn't specify the output file path!\n");
        return 1;
    }

    // Output the header
    fgets(buff, S_SIZE, fi);
    fputs(buff, fo);

    // Filter the rows of towns in Sendai city
    char keyword[] = "仙台市";
    char *result;
    while (fgets(buff, S_SIZE, fi) != NULL)
    {
        if (strstr(buff, keyword) != NULL)
            fputs(buff, fo);
    }

    fclose(fi);
    fclose(fo);

    printf("INFO: Extracted Sendai towns as: %s\n", sendai_path);

    return 0;
}

// This function was stolen from JA Wikipedia
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

int has_expected_header(char *csv_path)
{
    FILE *fi = fopen(csv_path, "r");
    char header[S_SIZE];
    char fields[ALL_F_NUM][F_NAME_SIZE];
    char *p; // pointer to the token found in the string
    int i = 0;

    if (fi == NULL)
    {
        printf("ERROR: CSV file not found!\n");
        return 1;
    }

    fgets(header, S_SIZE, fi);
    p = strtok(header, ",");
    strcpy(fields[i], p);

    fclose(fi);

    while ((p = strtok(NULL, ",")) != NULL)
        strcpy(fields[++i], p);

    // return 1 if all the field names are matched, if not return 0
    return strcmp(fields[WARD], "\"市区町村名\"") ==
           strcmp(fields[OAZA], "\"大字・丁目名\"") ==
           strcmp(fields[KOAZA], "\"小字・通称名\"") ==
           strcmp(fields[LAT], "\"緯度\"") ==
           strcmp(fields[LON], "\"経度\"") == 0;
}

// Count the number of commas in the string given
// This function isn't used
int count_comma(char *text, int i, int count)
{
    if (!text[i])
        return count;
    else
    {
        if (text[i] == ',')
            count++;
        i++;
        count_comma(text, i, count);
    }
}

int split(char *s, char result[ALL_F_NUM][V_SIZE])
{
    char *tp; // pointer to the token found
    int i = 0;

    tp = strtok(s, ",");
    strcpy(result[i], tp);
    while ((tp = strtok(NULL, ",")) != NULL)
        strcpy(result[++i], tp);

    return 0;
}