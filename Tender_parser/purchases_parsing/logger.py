import  datetime


def log_write(text: str):
    print(text)
    file = open("log.txt", "a")
    file.write(str(datetime.datetime.now()) + "     " + text)
    file.close()
