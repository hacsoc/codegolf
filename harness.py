
import sys, os, fcntl, subprocess, time, errno, signal, pty, json
from getopt import getopt, GetoptError

usage_message = 'harness.py [-d directory] program'
extended_message = ''

MEMLIMIT= int(1.5 * 10**9) # 1.5GB
INDEX_TIME = 10.5 # 6 * 60 # 6 min
QUERY_TIME = 1 * 60 # 1 min
error_codes = {
  'mem': 1,
  'index_time': 2,
  'query_time': 3,
  'usage': 4,
  'input': 5,
  'file_instead_of_dir':6,
}


def log(*msgs):
  for msg in msgs:
    print >>sys.stderr, msg,
  print >>sys.stderr
  sys.stderr.flush()

def output(*msgs):
  for msg in msgs:
    print >>sys.stdout, msg,
  print >>sys.stdout
  sys.stdout.flush()

def usage(code=None):
    '''Prints the usage and exits with an error code specified by code. If code
    is not given it exits with error_codes['usage']'''
    log(usage_message)
    if code is None:
        log(extended_message)
        code = error_codes['usage']
    sys.exit(code)

def _eintr_retry_call(func, *args):
  while True:
    try: 
      return func(*args)
    except (OSError, IOError) as e:
      if e.errno == errno.EINTR:
        continue
      if e.errno == errno.EAGAIN:
        return ''
      raise

def nb_read(output, amt):
  return _eintr_retry_call(output.read, amt)

def start(directory, program):
  cwd = os.getcwd()
  os.chdir(directory)
  print program
  #p = subprocess.Popen(' '.join(program), shell=True, stdin=subprocess.PIPE, 
  p = subprocess.Popen(program, stdin=subprocess.PIPE, 
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1)
  #p = pty.spawn(program)
  ##fd = p.stdout.fileno()
  #fl = fcntl.fcntl(fd, fcntl.F_GETFL)
  #fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
  os.chdir(cwd)
  return p, time.time()

def getmem(p):
  path = '/proc/%s/statm' % str(p.pid)
  with open(path, 'r') as f: statm = f.read()
  total = int(statm.split(' ', 1)[0])
  return total

def kill(p):
  os.kill(p.pid, signal.SIGTERM)

def check_indexing_resources(p, start_time):
  mem = getmem(p)
  if mem > MEMLIMIT: 
    kill(p)
    log("You used to much memory, killing")
    sys.exit(error_codes['mem'])
  if time.time() - start_time > INDEX_TIME:
    kill(p)
    log("You used to much time, killing")
    sys.exit(error_codes['index_time'])

def monitor_indexing(p, start_time):
  text = ''
  while '>' not in text:
    check_indexing_resources(p, start_time)
    text = nb_read(p.stdout, 1)
    if text != '': 
      sys.stderr.write(text)
      sys.stderr.flush()
      sys.stdout.flush()
  
def check_query_resources(p, start_time):
  mem = getmem(p)
  if mem > MEMLIMIT: 
    kill(p)
    log("You used to much memory, killing")
    sys.exit(error_codes['mem'])
  if time.time() - start_time > QUERY_TIME:
    kill(p)
    log("You used to much time, killing")
    sys.exit(error_codes['index_time'])

def monitor_query(p, start_time):
  text = ''
  while '>' not in text:
    check_query_resources(p, start_time)
    text = nb_read(p.stdout, 1)
    if text != '': 
      sys.stderr.write(text)
      sys.stderr.flush()
      sys.stdout.flush()
  return time.time() - start_time
  
def query(p, text):
  start_time = time.time()
  p.stdin.write(text)
  p.stdin.write('\n')
  p.stdin.flush()
  return monitor_query(p, start_time)

def run(directory, program):
  p, start_time = start(directory, program)
  monitor_indexing(p, start_time)
  queries = ['never', 'have', 'was in the world']
  times = [query(p,q) for q in queries] 
  os.kill(p.pid, signal.SIGINT)
  #print p.communicate()
  p.stdin.close()
  print times
  print 'finished'
  
def assert_dir_exists(path):
    '''checks if a directory exists. if not it creates it. if something exists
    and it is not a directory it exits with an error.
    '''
    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.mkdir(path)
    elif not os.path.isdir(path):
        log('Expected a directory found a file. "%(path)s"' % locals())
        usage(error_codes['file_instead_of_dir'])
    return path

def main(args):
  try:
    opts, args = getopt(
      args,
      'hd:',
      [
        'help', 'dir='
      ]
    )
  except GetoptError, err:
    log(err)
    usage(error_codes['option'])

  program = None
  directory = os.getcwd()
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
    elif opt in ('-d', '--dir'):
      directory = assert_dir_exists(arg)
  
  if not args:
    log('must supply program')
    usage(error_codes['input'])
  program = args

  run(directory, program)

if __name__ == '__main__':
  main(sys.argv[1:])

