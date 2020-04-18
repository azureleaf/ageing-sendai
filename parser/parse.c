#include <stdio.h>
#include <string.h>
#include <iconv.h>

#define S_SIZE (2048) // Length of a line in the file

char miyagi_sjis_path[] = "../raw/koaza-positions/04_2018.csv";
char miyagi_utf8_path[] = "./miyagi_utf8.csv";
char sendai_path[] = "./ages_parsed.csv";

int parse_miyagi_csv(void);
int sjis2utf8(char *, char *);

int main()
{
    parse_miyagi_csv();

    return 0;
}

int parse_miyagi_csv(void)
{
    FILE *fi, *fo;
    char buff[S_SIZE];

    // If the source file doesn't exist, generate it
    if ((fi = fopen(miyagi_utf8_path, "r")) == NULL)
    {
        sjis2utf8(miyagi_sjis_path, miyagi_utf8_path);

        // When the even file generation fails, abort
        if ((fi = fopen(miyagi_utf8_path, "r")) == NULL)
        {
            printf("Error: source file not found!");
            return 1;
        }
        printf("Successfully converted SHIFT-JIS file into UTF-8.");
    };
    if ((fo = fopen(sendai_path, "w")) == NULL)
    {
        printf("Error: couldn't specify the output file path!");
        return 1;
    }

    // Output the header
    fgets(buff, S_SIZE, fi);
    fputs(buff, fo);

    char keyword[] = "仙台市";
    char *result;

    while (fgets(buff, S_SIZE, fi) != NULL)
    {
        if (strstr(buff, keyword) != NULL)
            fputs(buff, fo);
    }

    fclose(fi);
    fclose(fo);

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

    return 0;
}