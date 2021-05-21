import psutil


class PS_Utils:

    def cpu_count(self):
        try:
            return psutil.cpu_count()
        except:
            return -1

    def cpu_percent(self, **kward):
        try:
            return psutil.cpu_percent(**kward)
        except:
            return -1

    def disk_partitions_count(self):
        try:
            return len(psutil.disk_partitions())
        except:
            return -1

    def net_connections_count(self, kind='tcp'):
        try:
            return len(psutil.net_connections(kind=kind))
        except:
            return -1

    def processes_count(self):
        try:
            pids = psutil.pids()
            return len(pids)
        except:
            return -1

    def threads_count(self):
        try:
            pids = psutil.pids()
            thread_count = 0
            for pid in pids:
                try:
                    p = psutil.Process(int(pid))
                    process_treads = p.num_threads()
                    thread_count += process_treads
                except:
                    pass
            return thread_count
        except:
            return -1

    def virtual_memory_percent(self):
        try:
            return psutil.virtual_memory().percent
        except:
            return -1