import datetime

def make_page_url_by_num(url: str, page_num: int) -> str:
    print(page_num)
    file = open("log.txt", "a")
    file.write("\n" + str(page_num))
    file.write("     " + str(datetime.datetime.now()))
    file.close()
    page_num = str(page_num)
    num_start = url.find("pageNumber=")
    if num_start == -1:
        new_url = url + "&pageNumber=" + page_num
        return new_url
    num_finish = url[url.find("pageNumber="):].find("&") + url.find("pageNumber=")
    new_url = url[:num_start] + "pageNumber=" + str(page_num) + url[num_finish:]
    return new_url
