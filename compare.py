import sys, os, json, math

from scipy import stats
import matplotlib.pyplot as plt
import warnings
from anovalib import *

def compute(observations):
  boxplot('compare/box.png', *(t
    for k, t in sorted(observations.iteritems(), key=lambda x: x[0])))
  #scatterplot('compare/scatter.png',
      #observations.keys(), [np.mean(t) for t in observations.values()],
      #'Cotton Percentage', 'Average Breaking Strength')
  residualplots('compare/', [(k,t) for k, t in sorted(observations.iteritems(),
    key=lambda x: x[0])])
  anova = f_oneway(*observations.values())
  for line in anova:
    print '\t'.join(str(col) for col in line)
 
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
  assert_dir_exists('compare')
  paths = [assert_file_exists(path) for path in args]
  times = dict()
  for path in paths:
    with open(path, 'r') as f:
      ptimes = json.load(f)
    ptimes = [math.log(x[0]) for x in ptimes]
    #print ptimes
    times[os.path.splitext(os.path.basename(path))[0]] = ptimes
  n = min(len(v) for v in times.values())
  for k,v in times.iteritems():
    times[k] = v[:n]
  compute(times)

if __name__ == '__main__':
  main(sys.argv[1:])
