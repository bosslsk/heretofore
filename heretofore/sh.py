# -*- coding: utf-8 -*-
"""
create on 2018-01-11 下午3:45

author @heyao
"""

import psutil
import signal


class MonitProcess(object):
    def __init__(self):
        signals = [s for s in vars(signal) if s.startswith('SIG') and '_' not in s]
        self.sig_mapping = {getattr(signal, k): getattr(signal, k) for k in signals}
        self.sig_mapping.update({k: getattr(signal, k) for k in signals})

    def get_pids(self, short_command):
        pids = []
        for process in psutil.process_iter():
            try:
                cmd = process.cmdline()
            except psutil.AccessDenied:
                continue
            if short_command in ' '.join(cmd):
                pids.append(process.pid)
        return pids

    def send_signal(self, pids, sig='SIGINT'):
        sig = self.sig_mapping.get(sig, None)
        if sig is None:
            raise ValueError("signal '%s' not support" % sig)
        for pid in pids:
            if psutil.pid_exists(pid):
                psutil.Process(pid).send_signal(sig)

    def process_exists(self, pids):
        """pid对应的进程是否存在"""
        return any(psutil.pid_exists(pid) for pid in pids)

    def cup_state(self, interval=1):
        return psutil.cpu_percent(interval)

    def memory_state(self):
        return psutil.virtual_memory()
