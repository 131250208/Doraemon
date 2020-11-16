import re
import sys
import socket
import queue
import threading


class Parser(threading.Thread):
    def __init__(self, queue, domain_name2ip, max_fail_num=0):
        threading.Thread.__init__(self)
        self._queue = queue
        self.domain_name2ip = domain_name2ip
        self.domain_name2fail_num = {}
        self.max_fail_num = max_fail_num

    def run(self):
        while not self._queue.empty():
            domain_name = self._queue.get()
            try:
                ip = socket.gethostbyname(domain_name)
                self.domain_name2ip[domain_name] = ip
                sys.stdout.write("\r[+] {} -> {} ---------------------------".format(domain_name, ip))
                sys.stdout.flush()

            except Exception as e:
                fail_num = self.domain_name2fail_num.get(domain_name, 0)
                if fail_num < self.max_fail_num:
                    self._queue.put(domain_name)
                else:
                    self.domain_name2ip[domain_name] = None

                self.domain_name2fail_num[domain_name] = fail_num + 1
                sys.stdout.write(
                    "\r[-] {} failed: {}/{} ----------------------".format(domain_name, fail_num, self.max_fail_num))
                sys.stdout.flush()


def urlfillter(url):
    return re.sub("https?://", "", url).split("/")[0].split(":")[0]


def gethostbyname_fast(url_list, domain_name2ip, thread_num = 20, max_fail_num = 0):
    domain_names = {urlfillter(url.strip()) for url in url_list}

    uni_queue = queue.Queue()
    for dn in domain_names:
        uni_queue.put(dn)

    workers = []
    for _ in range(thread_num):
        worker = Parser(uni_queue, domain_name2ip, max_fail_num)
        worker.start()
        workers.append(worker)

    for worker in workers:
        worker.join()


if __name__ == '__main__':
    threads = 100
    max_fail_num = 0
    domain_name2ip = {}
    url_list = ["https://www.baidu.com", "https://www.qq.com"]
    gethostbyname_fast(url_list, domain_name2ip, threads, max_fail_num)
