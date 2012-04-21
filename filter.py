
import os, sys, json

def assert_file_exists(path):
  '''checks if the file exists. If it doesn't causes the program to exit.
  @param path : path to file
  @returns : the path to the file (an echo) [only on success]
  '''
  path = os.path.abspath(path)
  if not os.path.exists(path):
    raise Exception, 'file doesnt exist'
  return path

def main(args):
  assert args
  path = assert_file_exists(args[0])
  with open('reviews', 'w') as fo:
    with open(path, 'r') as fi:
      for line in fi:
        line = json.loads(line)
        if line['type'] == 'review':
          out = ' : '.join((line['review_id'], line['text'].replace('\n', ' ')))
          fo.write(out.encode('utf8'))
          fo.write('\n')

if __name__ == '__main__':
  main(sys.argv[1:])

