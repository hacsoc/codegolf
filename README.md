Code Golf Submission Repo
=========================

We will be using this repo to submit the code for codegolf on Saturday April 21, 2012.

Running the Harness
===================

(not on linux? try harness\_dumb.py)

by Example:

    $ python harness.py -d ../hacsoc_code_golf/ -r /tmp/results/results.micro python index.py /tmp/reviews/reviews.micro 

by Format:
    
    $ python harness.py -d <directory of you code> -r <path to results> [your program] <path to reviews>

Interface
=========

command line arguments:

    program path/to/reviews

example:

    python index.py /tmp/reviews.micro

index phase
-----------

you can write anything you want to stderr and stdout EXCEPT `>` as soon as it
sees a newline character the harness enters "query phase"


query phase
-----------

example code: (python)

    sys.stdout.flush()
    while True:
      sys.stdout.write('> '); sys.stdout.flush()
      try: inpt = sys.stdin.readline()
      except: break;
      if not inpt: continue
      inpt = clean(inpt)
      inpt = inpt.split()
      query(*inpt)
    sys.stdout.flush()

what happens:

- you write a `>` to the stdout this is the "prompt"
- then you read a line from the stdin
- you do your query
- you collect all the revids put them in a list
- encode the list ["revid1", "revid2", ....] eg. as a json list
- write the encoded list to the stdout

Clean Function
==============

    def clean(text):
      return (
          text
          .lower()
          .replace('/', '')
          .replace('(', '')
          .replace(')', '')
          .replace(')', '')
          .replace(':', '')
          .replace('.', '')
          .replace(',', '')
          .replace(';', '')
          .replace(';', '')
          .replace('?', ' ?')
          .replace('!', ' !')
          .replace('-', ' - '))



