#include <stdio.h>
#include <string.h>
#include <iconv.h>
#include <unistd.h> // access()

#define S_SIZE (1024) // Length of a line in the file
#define NUM_FIELDS 14
#define LEN_FIELD_NAME_MAX 30 // e.g. "住居表示フラグ" is 21 Bytes, I guess

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

int main()
{
    // Check existance of UTF-8 file
    if (access(miyagi_utf8_path, F_OK) == -1)
        if (parse_miyagi_csv())
            return 1; // on error

    if (!has_expected_header(sendai_path))
        return 1;

    printf("hello!");

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
        printf("ERROR: couldn't specify the output file path!");
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
    char fields[NUM_FIELDS][LEN_FIELD_NAME_MAX];
    char *p; // pointer to the token found
    int i = 0;

    if (fi == NULL)
    {
        printf("ERROR: CSV file not found!");
        return 1;
    }

    fgets(header, S_SIZE, fi);
    p = strtok(header, ",");
    strcpy(fields[i], p);

    while ((p = strtok(NULL, ",")) != NULL)
        strcpy(fields[++i], p);

    // for (i = 0; i < NUM_FIELDS; i++)
    //     printf("%s,", fields[i]);
    // printf("\n");

    return strcmp(fields[WARD], "\"市区町村名\"") ==
           strcmp(fields[OAZA], "\"大字・丁目名\"") ==
           strcmp(fields[KOAZA], "\"小字・通称名\"") ==
           strcmp(fields[LAT], "\"緯度\"") ==
           strcmp(fields[LON], "\"経度\"") == 0;
}