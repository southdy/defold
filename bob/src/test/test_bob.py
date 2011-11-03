import unittest, sys
from os import unlink, mkdir
from os.path import exists
from shutil import rmtree, copytree
from pprint import pprint

sys.path.append('src')
import bob

sys.path.append('build/default')
import test_bob_ddf_pb2

def read_file(name):
    with open(name, 'rb') as f:
        return f.read()

class TestBob(unittest.TestCase):

    def setUp(self):
        if exists('tmp'):
            rmtree('tmp')
        mkdir('tmp')
        mkdir('tmp/build')
        if exists('tmp_build'):
            rmtree('tmp_build')
        copytree('test_data', 'tmp/test_data')

    def assertSetEquals(self, l1, l2):
        self.assertEquals(set(l1), set(l2))

    def test_collect_inputs(self):
        script = '''
from glob import glob
p = project(bld_dir = "tmp_build",
            inputs = glob('tmp/test_data/*.c'),
            includes = ['tmp/test_data/include'])
build(p, run=False, listener = null_listener)
'''
        l = bob.exec_script(script)
        p = l.p
        self.assertEqual(set(['tmp/test_data/main.c', 'tmp/test_data/util.c', 'tmp/test_data/error.c']),
                         set(p['inputs']))


    def test_create_tasks(self):
        script = '''
p = project(bld_dir = "tmp_build",
            inputs = ['tmp/test_data/main.c'],
            includes = ['tmp/test_data/include'])
import bob_cc
bob_cc.config(p)
build(p, run=False, listener = null_listener)
'''
        l = bob.exec_script(script)
        tasks = l.p['tasks']
        self.assertEqual(1, len(tasks))
        t = tasks[0]

        self.assertSetEquals(['tmp/test_data/main.c'], t['inputs'])
        self.assertSetEquals(['tmp_build/tmp/test_data/main.o'], t['outputs'])

    def test_scan(self):
        script = '''
p = project(bld_dir = "tmp_build",
            inputs = ['tmp/test_data/util.c'],
            includes = ['tmp/test_data/include'])
import bob_cc
bob_cc.config(p)
build(p, run=False, listener = null_listener)
'''
        l = bob.exec_script(script)
        t = l.p['tasks'][0]

        self.assertSetEquals(['tmp/test_data/util.h', 'tmp/test_data/include/misc.h'],
                             t['dependencies'])

    def test_task_signatures(self):
        script1 = '''
p = project(bld_dir = "tmp_build",
            inputs = ['tmp/test_data/main.c'],
            includes = ['tmp/test_data/include'])
import bob_cc
bob_cc.config(p)
build(p, run=True, listener = null_listener)
'''
        l1 = bob.exec_script(script1)

        script2 = '''
p = project(bld_dir = "tmp_build",
            inputs = ['tmp/test_data/main.c'],
            includes = ['tmp/test_data/include', '/opt/include'])
import bob_cc
bob_cc.config(p)
build(p, run=True, listener = null_listener)
'''
        l2 = bob.exec_script(script2)

        t1 = l1.p['tasks'][0]
        t2 = l2.p['tasks'][0]
        self.assertNotEquals(t1['sig'], t2['sig'])

    def test_c_compile(self):
        script = '''
p = project(bld_dir = "tmp_build",
            inputs = ['tmp/test_data/main.c'],
            includes = ['tmp/test_data/include'])
import bob_cc
bob_cc.config(p)
r = build(p, listener = null_listener)
'''
        l = bob.exec_script(script)
        info = l.r[0]
        self.assertEquals(True, info['run'])
        self.assertEquals(0, info['code'])

        l = bob.exec_script(script)
        info = l.r[0]
        self.assertEquals(False, info['run'])
        self.assertEquals(0, info['code'])

        unlink('tmp_build/tmp/test_data/main.o')
        l = bob.exec_script(script)
        info = l.r[0]
        self.assertEquals(True, info['run'])
        self.assertEquals(0, info['code'])

        # update header
        with open('tmp/test_data/include/misc.h', 'wb') as f:
            f.write('//some new data')

        l = bob.exec_script(script)
        info = l.r[0]
        self.assertEquals(True, info['run'])
        self.assertEquals(0, info['code'])

    def test_c_compile_error(self):
        script = '''
p = project(bld_dir = "tmp_build",
            inputs = ['tmp/test_data/error.c'],
            includes = ['tmp/test_data/include'])
import bob_cc
bob_cc.config(p)
r = build(p, listener = null_listener)
'''
        l = bob.exec_script(script)
        r = l.r
        info = l.r[0]
        self.assertEquals(True, info['run'])
        self.assert_(info['code'] > 0, 'code > 0')
        self.assertEquals('', info['stdout'])
        self.assertNotEquals('', info['stderr'])

        # run again. File file so it should recompile
        l = bob.exec_script(script)
        r = l.r
        info = l.r[0]
        self.assertEquals(True, info['run'])

        # "fix" file
        with open('tmp/test_data/error.c', 'wb') as f:
            f.write('\n')

        l = bob.exec_script(script)
        r = l.r
        info = l.r[0]
        self.assertEquals(True, info['run'])
        self.assertEquals(0, info['code'])

        self.assertEquals('', info['stdout'])
        self.assertEquals('', info['stderr'])

    def test_proto_task(self):
        script = '''
from glob import glob
def transform_bob(msg):
    msg.resource = msg.resource + 'c'

p = project(bld_dir = "tmp_build",
            inputs = glob('tmp/test_data/*.bob'))
p['task_gens']['.bob'] = make_proto('test_bob_ddf_pb2', 'TestBob', transform_bob)
r = build(p, listener = null_listener)
'''
        l = bob.exec_script(script)

        tb = test_bob_ddf_pb2.TestBob()
        with open('tmp_build/tmp/test_data/test.bobc', 'rb') as f:
            tb.MergeFromString(f.read())

        self.assertEquals(tb.resource, u'some_resource.extc')


    def test_listener(self):
        script = '''

class Listener(object):
    def __init__(self):
        self.invocations = { 'start' : 0, 'done' : 0 }

    def __call__(self, prj, task, evt):
        self.invocations[evt] += 1
        pass

listener = Listener()

def test_file(prj, tsk):
    with open(tsk["outputs"][0], "wb") as f:
        f.write("test data")

def test_factory(prj, input):
    return add_task(prj, task(function = test_file,
                              name = 'test',
                              inputs = [input],
                              outputs = [change_ext(p, input, '.bobc')]))

p = project(bld_dir = "tmp_build",
            inputs = ['tmp/test_data/test.bob'])
p['task_gens']['.bob'] = test_factory
r = build(p, listener = listener)
'''
        l = bob.exec_script(script)

        listener = l.p['listener']
        self.assertEqual(1, listener.invocations['start'])
        self.assertEqual(1, listener.invocations['done'])

        l = bob.exec_script(script)
        listener = l.p['listener']
        self.assertEqual(0, listener.invocations['start'])
        self.assertEqual(0, listener.invocations['done'])

    def test_exception(self):
        script = '''

def test_file(prj, tsk):
    raise Exception("Some error occurred")

def test_factory(prj, input):
    return add_task(prj, task(function = test_file,
                              name = 'test',
                              inputs = [input],
                              outputs = [change_ext(p, input, '.bobc')]))

p = project(bld_dir = "tmp_build",
            inputs = ['tmp/test_data/test.bob'])
p['task_gens']['.bob'] = test_factory
r = build(p, listener = null_listener)
'''
        l = bob.exec_script(script)
        info = l.r[0]
        self.assertEquals(10, info['code'])
        self.assertTrue(info['stderr'].find('Exception:') != -1, 'String "Exception:" not found in stderr')

    def test_dynamic_task(self):
        script = '''

from test_bob_util import dynamic_factory, number_factory

p = project(bld_dir = "tmp_build",
            inputs = ['tmp/test_data/test.dynamic'])
p['task_gens']['.dynamic'] = dynamic_factory
p['task_gens']['.number'] = number_factory
r = build(p, listener = null_listener)
'''
        l = bob.exec_script(script)

        for info in l.r:
            if info['task']['name'] != 'dynamic':
                # assert that number tasks originates from the dynamic task
                self.assertEquals(info['task']['product_of']['inputs'][0], 'tmp/test_data/test.dynamic')

        for i, x in enumerate([10, 20, 30]):
            self.assertEquals(x, int(read_file('tmp_build/tmp/test_data/test_%d.number' % i)))

        scale = 100
        for i, x in enumerate([10, 20, 30]):
            self.assertEquals(x * scale, int(read_file('tmp_build/tmp/test_data/test_%d.numberc' % i)))

    def test_substitute(self):
        d1 = { 'cc' : 'gcc', 'coptim' : '-O2'}
        d2 = { 'inputs' : [ 'a.c', 'b.c'],
               'outputs' : [ 'x.o' ],
               'coptim' : '-O0' }
        lst = bob.substitute('${CC} ${COPTIM} -c ${INPUTS} -o ${OUTPUTS[0]}', d1, d2)
        self.assertEquals('gcc -O0 -c a.c b.c -o x.o'.split(), lst)

if __name__ == '__main__':
    unittest.main()
