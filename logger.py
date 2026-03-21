import ntplib
import time
import threading
import atexit

from rich.console import Console
from rich.color import ANSI_COLOR_NAMES


class NetTime:
    def __init__(self):
        self.offset = 0.0
        self.interval = 60 * 30 # sec
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self.servers = [
            "ntp.nict.jp",
            "time.google.com",
            "pool.ntp.org",
            "time.windows.com",
        ]
        self.sync()
        self.thread = threading.Thread(
            target=self._resync_loop,
            daemon=True
        )
        self.thread.start()
        atexit.register(self.stop)

    def sync(self):
        c = ntplib.NTPClient()
        for server in self.servers:
            try:
                r = c.request(server, timeout=3)
                new_offset = r.tx_time - time.time()
                with self._lock:
                    self.offset = new_offset
                return
            except Exception:
                continue

    def _resync_loop(self):
        while not self._stop_event.wait(self.interval):
            self.sync()

    def now(self):
        with self._lock:
            return time.time() + self.offset

    def now_struct(self):
        return time.localtime(self.now())

    def stop(self):
        self._stop_event.set()


ntime = NetTime()
plog = Console(highlight=False,markup=False)

LEVELS=["info ","warn ","error"]
STYLES=["bright_white","bright_yellow","bright_red"]
ERRORSTYLE="dark_red"

def stylecolor() -> None:
    """
    Outputs colors that can be used in styles. 
    """
    for i in ANSI_COLOR_NAMES.keys():
        log(f'color log color: {i}', 'color', i)

def offset() -> float:
    """
    Outputs the offset between the Local and the NTP server.

    Returns
    -------
    float
        _description_
    """
    log(f'Local Time is {time.strftime("%Y:%m:%d:%H:%M:%S")}')
    log(f'{'Lated' if ntime.offset > 0 else 'Early'}: {ntime.offset:.5}sec')
    return ntime.offset

def log2file(text:str) -> None:
    """
    ## work in progress
    Outputs the log to file.

    Parameters
    ----------
    text : str
        The string to be output to the log file.
    """
    pass

def log(text,info:int|str=0,style:str|None=None) -> str:
    """
    Outputs the log.

    Parameters
    ----------
    text : Any
        The string to be output.
    info : int | str, optional
        Sets the info level.  
        If a string is provided, it will be inserted into info.  
        0:info  
        1:warn  
        2:error  
        by default 0
    style : str, optional
        Log color.  
        Only works when info is a string.  
        by default None

    Returns
    -------
    str
        Returns the log contents as a string.  
        Color information will be lost in the process.
    """
    tm=time.strftime("%Y:%m:%d:%H:%M:%S",ntime.now_struct())
    level=LEVELS[0]
    if isinstance(info,int) and len(LEVELS)-1 >= info: level,style=LEVELS[info],STYLES[info]
    text=f'[{tm}] {str(text)}'
    if isinstance(info,str):
        ret=f'[{info }] {text}'
        plog.print(f'[{info }] {text}',style=style)
    elif info>=0 and info<=2:
        ret=f'[{level}] {text}'
        plog.print(f'[{level}] {text}',style=style)
    else:
        ret=f"[CONSOLE ERROR] [{tm}] Unknown info number: {info}  ; {text}"
        plog.print(f"[CONSOLE ERROR] [{tm}] Unknown info number: {info}  ; {text}",style=ERRORSTYLE)
    return ret
    

if __name__=='__main__':
    log('testmessage')
    log('warn log',1)
    log('error log',2)
    log('console error log',3)
    log('text info log','test ')
    offset()
    if input('Show colors that can be used in styles?(y/n)>')=='y':
        stylecolor()
