
import sys, os, fcntl, subprocess, time, errno, signal, pty, json, random
from getopt import getopt, GetoptError
random.seed()

usage_message = 'harness.py [-d directory] program'
extended_message = ''

MEMLIMIT= int(1.5 * 10**9) # 1.5GB
INDEX_TIME = 6 * 60 # 6 min
QUERY_TIME = 2 * 60 # 2 min
error_codes = {
  'mem': 1,
  'index_time': 2,
  'query_time': 3,
  'usage': 4,
  'input': 5,
  'file_instead_of_dir':6,
}

def loadqueries(path):
  with open(path, 'r') as f:
    Q = json.load(f)
  for k,v in Q.iteritems(): yield k,v 

def _getqueries():
  dic = list()
  with open('en-US.dic', 'r') as f:
    for line in f:
      dic.append(line.strip())
  for x in xrange(200):
    query = list()
    for y in xrange(random.randint(1, 6)):
      word = random.choice(dic).replace("'", '')
      start = random.randint(0, len(word)/2-1)
      end = random.randint(start+1, len(word))
      if end - start < 1: continue
      substr = word[start:end]
      if len(substr) < 3: continue
      query.append(substr)
    if not query: continue
    yield ' '.join(query), set()

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

def avg(g):
  c = 0.0
  s = 0.0
  for i in g:
    c += 1.0
    s += i
  return s/c

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
      stdout=subprocess.PIPE, bufsize=4096)
  #p = pty.spawn(program)
  fd = p.stdout.fileno()
  fl = fcntl.fcntl(fd, fcntl.F_GETFL)
  fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
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
    log("You used to much (index) time, killing")
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
    else:
      time.sleep(.001)
  
def check_query_resources(p, start_time):
  mem = getmem(p)
  if mem > MEMLIMIT: 
    kill(p)
    log("You used to much memory, killing")
    sys.exit(error_codes['mem'])
  if time.time() - start_time > QUERY_TIME:
    kill(p)
    log("You used to much (query) time, killing")
    sys.exit(error_codes['query_time'])

def load_results(buf):
  #log(buf)
  if buf == '[]': return set()
  else: return set(json.loads(buf))

def monitor_query(p, start_time, expected):
  buf = ''
  text = ''
  while '>' not in text:
    check_query_resources(p, start_time)
    text = nb_read(p.stdout, 1)
    if text != '' and '>' not in text: 
      buf += text
    else:
      time.sleep(.001)
  buf = buf.strip()
  #return time.time() - start_time
  return time.time() - start_time, (load_results(buf) == expected)
  
def query(p, text, expected):
  start_time = time.time()
  p.stdin.write(text.encode('utf8'))
  p.stdin.write('\n')
  p.stdin.flush()
  return monitor_query(p, start_time, expected)

def run(directory, program, queries):
  p, start_time = start(directory, program)
  monitor_indexing(p, start_time)
  #times = [query(p,q,set(res)) for q,res in getqueries().iteritems()] 
  #times = [query(p,q,set(res)) for q,res in _getqueries()] 
  times = list()
  for q, res in loadqueries(queries):
    print q, 
    sys.stdout.flush()
    runtime, succ = query(p,q,set(res))
    print runtime, succ
    sys.stdout.flush()
    times.append((runtime, succ))
  os.kill(p.pid, signal.SIGINT)
  p.wait()
  with open(os.path.join(directory, 'times.json'), 'w') as f:
    json.dump(times, f)
  print
  print 'all pass?', all(succ for runtime, succ in times)
  print 'mean time', avg([runtime for runtime, succ in times])
  
def assert_file_exists(path):
  '''checks if the file exists. If it doesn't causes the program to exit.
  @param path : path to file
  @returns : the path to the file (an echo) [only on success]
  '''
  path = os.path.abspath(path)
  if not os.path.exists(path):
    log('No file found. "%(path)s"' % locals())
    usage(error_codes['file_not_found'])
  return path


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
      'hd:r:',
      [
        'help', 'dir=', 'results='
      ]
    )
  except GetoptError, err:
    log(err)
    usage(error_codes['option'])

  program = None
  directory = os.getcwd()
  queries = None
  for opt, arg in opts:
    if opt in ('-h', '--help'):
      usage()
    elif opt in ('-d', '--dir'):
      directory = assert_dir_exists(arg)
    elif opt in ('-r', '--results'):
      queries = assert_file_exists(arg)
  
  if not args:
    log('must supply program')
    usage(error_codes['input'])
  program = args

  run(directory, program, queries)
  print 'finished'

if __name__ == '__main__':
  main(sys.argv[1:])

