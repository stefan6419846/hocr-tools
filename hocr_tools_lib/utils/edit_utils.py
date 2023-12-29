def edit_distance(a, b, threshold=99999):
    if a == b:
        return 0
    m = len(a)
    n = len(b)
    distances = [[threshold for j in range(n + 1)] for i in range(m + 1)]
    # distances is a 2-dimensional array such that distances[i][j]
    # will be equal to the edit distance of the first i characters
    # of a and the first j characters of b.
    for i in range(m + 1):
        distances[i][0] = i
    for j in range(n + 1):
        distances[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                cij = 0
            else:
                cij = 1
            d = min(distances[i - 1][j] + 1, distances[i][j - 1] + 1,
                    distances[i - 1][j - 1] + cij)
            if d >= threshold:
                return d
            distances[i][j] = d
    return distances[m][n]


# def remove_tex(text):
#     text_file = os.popen(f"echo {text} | detex")
#     text_plain = text_file.read()
#     text_file.close()
#     return text_plain


def remove_tex(text):
    return text
