Code Golf Submission Repo
=========================

We will be using this repo to submit the code for codegolf on Saturday April 21, 2012.


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



