from collections import namedtuple, defaultdict
import logging
import subprocess
import time

from deephyper.evaluators import evaluate

logger = logging.getLogger(__name__)

class PopenFuture:
    FAIL_RETURN_VALUE = evaluate.Evaluator.FAIL_RETURN_VALUE

    def __init__(self, args, parse_fxn):
        self.proc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, encoding='utf-8')
        self._state = 'active'
        self._result = None
        self._parse = parse_fxn

    def _poll(self):
        if not self._state == 'active': return
        retcode = self.proc.poll()
        if retcode is None:
            self._state = 'active'
        elif retcode == 0:
            self._state = 'done'
        else:
            self._state = 'failed'

    def result(self):
        if self._result is not None:
            return self._result
        self.proc.wait()
        if self.done:
            stdout, _ = self.proc.communicate()
            self._result = self._parse(stdout)
        else:
            stdout, _ = self.proc.communicate()
            self._result = self.FAIL_RETURN_VALUE
            logger.error(f"Eval failed: {stdout}")
        return self._result

    def cancel(self):
        self.proc.kill()
        try: self.proc.communicate()
        except ValueError: pass
        self._state = 'cancelled'

    @property
    def active(self):
        self._poll()
        return self._state == 'active'

    @property
    def done(self):
        self._poll()
        return self._state == 'done'

    @property
    def failed(self):
        self._poll()
        return self._state == 'failed'

    @property
    def cancelled(self):
        self._poll()
        return self._state == 'cancelled'

class LocalEvaluator(evaluate.Evaluator):
    WaitResult = namedtuple('WaitResult', ['active', 'done', 'failed', 'cancelled'])
    def __init__(self, run_function, cache_key=None):
        super().__init__(run_function, cache_key)
        self.num_workers = self.WORKERS_PER_NODE
        logger.info(f"Local Evaluator will execute {self._run_function.__name__}() from module {self._run_function.__module__}")

    def _args(self, x):
        exe = self._runner_executable
        cmd = ' '.join((exe, f"'{self.encode(x)}'"))
        return cmd

    def _eval_exec(self, x):
        assert isinstance(x, dict)
        cmd = self._args(x)
        future = PopenFuture(cmd, self._parse)
        return future

    @staticmethod
    def _timer(timeout):
        if timeout is None:
            return lambda : True
        else:
            timeout = max(float(timeout), 0.01)
            start = time.time()
            return lambda : (time.time()-start) < timeout

    def wait(self, futures, timeout=None, return_when='ANY_COMPLETED'):
        assert return_when.strip() in ['ANY_COMPLETED', 'ALL_COMPLETED']
        waitall = bool(return_when.strip() == 'ALL_COMPLETED')

        num_futures = len(futures)
        active_futures = [f for f in futures if f.active]
        time_isLeft = self._timer(timeout)

        if waitall: can_exit = lambda : len(active_futures) == 0
        else: can_exit = lambda : len(active_futures) < num_futures

        while time_isLeft():
            if can_exit():
                break
            else:
                active_futures = [f for f in futures if f.active]
                time.sleep(0.04)

        if not can_exit():
            raise TimeoutError(f'{timeout} sec timeout expired while '
            f'waiting on {len(futures)} tasks until {return_when}')

        results = defaultdict(list)
        for f in futures: results[f._state].append(f)
        return self.WaitResult(
            active=results['active'],
            done=results['done'],
            failed=results['failed'],
            cancelled=results['cancelled']
        )
