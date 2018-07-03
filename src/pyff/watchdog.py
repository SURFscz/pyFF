from pyff.logs import log
import threading
import time
import inotify.adapters

class WatchDog(object):
  def __init__(self, server, watch):
    self.server = server
    self.watch = watch
    t = threading.Thread(target=self.check, name='check')
    t.daemon = True
    t.start()

  def check(self):
    i = inotify.adapters.Inotify()
    i.add_watch(self.watch)

    try:
      for event in i.event_gen():
        if event is not None:
          (header, type_names, watch_path, filename) = event
          if "IN_CLOSE_WRITE" in type_names:
            self.server.refresh.run(self.server)
            log.debug("WD=(%d) MASK=(%d) COOKIE=(%d) LEN=(%d) MASK->NAMES=%s "
                  "WATCH-PATH=[%s] FILENAME=[%s]" %
                  (header.wd, header.mask, header.cookie, header.len, type_names,
                  watch_path.decode('utf-8'), filename.decode('utf-8')))
    finally:
      i.remove_watch(self.watch)

