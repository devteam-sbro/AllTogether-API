import time
import traceback
from threading import Thread


class LoggedThread(Thread):

    def __init__(self, wait=0, **kwargs):
        super().__init__(**kwargs)
        self.wait = wait

    def run(self):
        '''
        '''
        from backend.libs.logger import fill_temp_log
        from backend.libs.logger import create_temp_log

        try:
            time.sleep(self.wait)
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception:
            fill_temp_log(create_temp_log('exception while async'), traceback.format_exc())
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs


