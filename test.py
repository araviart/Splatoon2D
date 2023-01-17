a = {
    (0, 0): {
        "a": 2
    },
    (1, 2): {
        "a": 2
    }
}

def t(t):
    return t[0]

n = max(a, key=t)[0]
print(n)