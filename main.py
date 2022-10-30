import game

def reader(file):
    with open(file, "r") as f:
        for line in f:
            yield line


if __name__ == "__main__":
    ex = reader("user_creation.txt")

    for paste in ex:
        print(paste)
