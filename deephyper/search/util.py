import os
import sys
import time
import logging
from importlib import import_module

masterLogger = None
LOG_LEVEL = os.environ.get('DEEPHYPER_LOG_LEVEL', 'DEBUG')
LOG_LEVEL = getattr(logging, LOG_LEVEL)

class Timer:
    def __init__(self):
        self.timings = {}

    def start(self, name):
        self.timings[name] = time.time()

    def end(self, name):
        try:
            elapsed = time.time() - self.timings[name]
        except KeyError:
            print(f"TIMER error: never called timer.start({name})")
        else:
            print(f"TIMER {name}: {elapsed:.4f} seconds")
            del self.timings[name]

def conf_logger(name):
    global masterLogger
    if (masterLogger == None):
        masterLogger = logging.getLogger('deephyper')

        handler = logging.FileHandler('deephyper.log')
        formatter = logging.Formatter(
            '%(asctime)s|%(process)d|%(levelname)s|%(name)s:%(lineno)s] %(message)s',
            "%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        masterLogger.addHandler(handler)
        masterLogger.setLevel(LOG_LEVEL)
        masterLogger.info("\n\nLoading Deephyper\n--------------")
    def log_uncaught_exceptions(exctype, value, tb):
        masterLogger.exception('Uncaught exception:', exc_info=(exctype,value,tb))
        sys.stderr.write(f"Uncaught exception {exctype}: {value}\n{tb}")
    sys.excepthook = log_uncaught_exceptions
    return logging.getLogger(name)

class DelayTimer:
    def __init__(self, max_minutes=None, period=2):
        if max_minutes is None:
            max_minutes = float('inf')
        self.max_minutes = max_minutes
        self.max_seconds = max_minutes * 60.0
        self.period = period
        self.delay = True

    def pretty_time(self, seconds):
        """Format time string"""
        seconds = round(seconds, 2)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "%02d:%02d:%02.2f" % (hours,minutes,seconds)

    def __iter__(self):
        start = time.time()
        nexttime = start + self.period
        while True:
            now = time.time()
            elapsed = now - start
            if elapsed > self.max_seconds:
                raise StopIteration
            else:
                yield self.pretty_time(elapsed)
            tosleep = nexttime - now
            if tosleep <= 0 or not self.delay:
                nexttime = now + self.period
            else:
                nexttime = now + tosleep + self.period
                time.sleep(tosleep)

def load_attr_from(str_full_module):
    """
        Args:
            - str_full_module: (str) correspond to {module_name}.{attr}
        Return: the loaded attribute from a module.
    """
    if type(str_full_module) == str:
        split_full = str_full_module.split('.')
        str_module = '.'.join(split_full[:-1])
        str_attr = split_full[-1]
        module = import_module(str_module)
        return getattr(module, str_attr)
    else:
        return str_full_module
