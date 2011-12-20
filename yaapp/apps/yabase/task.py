import sys
from celery.task import task


@task
def test(a):
    print 'testing task'
    f = open('/Users/meeloo/Desktop/prout.txt', 'w')
    f.write(a)
    f.close()
    print 'testing task done YAY!'
