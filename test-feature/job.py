#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Extracted from https://github.com/sankalpjonn/timeloop
"""
import time
from threading import Thread, Event
from datetime import timedelta

class Job(Thread):
    def __init__(self, interval_ms, execute, *args, **kwargs):
        Thread.__init__(self)
        self.stopped = Event()
        self.interval = timedelta(milliseconds=interval_ms)
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)


if __name__ == '__main__':
    def hello(name='foo'):
        print('Hi ', name)


    j = Job(750,hello,'bar')
    print('starting')
    j.start()
    print('sleeping for 6 seconds')
    time.sleep(6)
    print('stopping')
    j.stop()
