x = "global"

def show():
    print(x)

def run():
    x = "local"
    show()

run()  # Prints: global
