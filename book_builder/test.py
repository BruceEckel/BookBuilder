x = []
for i in range(0, 10):
    x.append((i, i * i))

for t in x:
    a, b = t
    print(f"{a}, {b}")