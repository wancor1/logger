import threading
import ntplib
import atexit
import time
import os

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
class Logger:
    LEVELS=["info ","warn ","error"]
    ERRORSTYLE="dark_red"
    STYLES=["bright_white","bright_yellow","bright_red"]

    def __init__(self,logstyle:str|None=None,outputfile:bool=False,file_path:str|None=None) -> None:
        """Initialize the Logger object.
        
        Parameters
        ----------
        logstyle : str | None, optional
            logstyle  
                i: info  
                t: time  
                e: text  
            by default None
        outputfile : bool, optional
            Whether to output to a file  
            by default False
        file_path : str | None, optional
            file_path  
            by default None
        """
        self.logstyle=logstyle

        ts=time.strftime("%Y-%m-%d-%H")
        self.outputfile=outputfile
        if not self.outputfile:
            self.file_path="Unexpected_log.log"
        else:
            if file_path is None: file_path=os.getcwd()
            filename=ts+".log"
            full_path=os.path.join(file_path, filename)
            if os.path.exists(full_path):
                i=1
                while True:
                    new_name=ts+f"({i}).log"
                    new_path=os.path.join(file_path, new_name)
                    if not os.path.exists(new_path):
                        full_path=new_path
                        break
                    i+=1
            self.file_path = full_path
            self.offset()

    def stylecolor(self) -> None:
        """
        Outputs colors that can be used in styles. 
        """
        for i in ANSI_COLOR_NAMES.keys():
            self.log(f'color log color: {i}', 'color', i)

    def offset(self,logput:bool=True,level:int|str=0)  -> tuple[float | str, list[str]]:
        """
        Outputs the offset between the Local and the NTP server.
        
        Parameters
        ----------
        logput : bool, optional
            Whether to output to the log  
            by default True
        level : int | str, optional
            info level  
            by default 0

        Returns
        -------
        tuple[float | str, list[str]]
            rawoffset,[text1,text2]
        """
        if logput:
            self.log(f'Local Time is {time.strftime("%Y:%m:%d:%H:%M:%S")}',level)
            self.log(f'{'Late' if ntime.offset > 0 else 'Early'}: {abs(ntime.offset):.5f}sec',level)
        return ntime.offset, [f'Local Time is {time.strftime("%Y:%m:%d:%H:%M:%S")}',f'{'Late' if ntime.offset > 0 else 'Early'}: {abs(ntime.offset):.5f}sec']

    def log2file(self,text:str) -> None:
        """
        ## work in progress
        Outputs the log to file.

        Parameters
        ----------
        text : str
            The string to be output to the log file.
        """
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def log(self,text,info:int|str=0,style:str|None=None) -> str:
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
        tm=time.strftime("%H:%M:%S",ntime.now_struct()) # %Y:%m:%d:%H:%M:%S
        level=self.LEVELS[0]
        if isinstance(info,int) and len(self.LEVELS)-1 >= info: level,style=self.LEVELS[info],self.STYLES[info]
        ftext=f'[{tm}] {str(text)}'
        if isinstance(info,str):
            ret=f'[{info }] {ftext}'
            plog.print(f'[{info }] {ftext}',style=style)
        elif info>=0 and info<=2:
            ret=f'[{level}] {ftext}'
            plog.print(f'[{level}] {ftext}',style=style)
        else:
            ret=f"[CONSOLE ERROR] [{tm}] Unknown info number: {info}  ; {text}"
            plog.print(f"[CONSOLE ERROR] [{tm}] Unknown info number: {info}  ; {text}",style=self.ERRORSTYLE)
        if self.outputfile: self.log2file(ret)
        return ret

if __name__=='__main__':
    logger=Logger(outputfile=True)
    logger.log('testmessage')
    logger.log('warn log',1)
    logger.log('error log',2)
    logger.log('console error log',3)
    logger.log('text info log','test ')
    logger.offset()
    if input('Show colors that can be used in styles?(y/n)>')=='y':
        logger.stylecolor()
