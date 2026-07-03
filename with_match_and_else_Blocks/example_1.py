with open('mirror.py') as fp:
    src = fp.read(60)
    print("Fetch 60 Character : ", src)

print("Length : ", len(src))

print("fp : ", fp)

print(fp.closed, fp.encoding)

print("Again Read : ", fp.read(60))
