import unittest
from cpu import Cpu

class Test_execute(unittest.TestCase):

    def testGeneric(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 1
        cpu.execute(0b00000000001000000000100000100100)
        self.assertEqual(cpu.r, good_r, 'AND $1, $1, $0 failed')

        cpu.r[1] = 1
        good_r[1] = 1
        cpu.execute(0b00000000001000000000100000100101)
        self.assertEqual(cpu.r, good_r, 'OR $1, $1, $0 failed')

        cpu.r[1] = 42
        cpu.r[6] = 42 | 111
        good_r[1] = 42
        good_r[6] = 42 | 111
        good_r[3] = 42
        cpu.execute(0b00000000001001100001100000100100)
        self.assertEqual(cpu.r, good_r, 'AND $3, $1, $6 failed')

class Test_execute_R(unittest.TestCase):

    def testAND(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 11
        cpu.r[2] = 10
        good_r[1] = 11
        good_r[2] = 10
        good_r[3] = 10
        cpu.execute_R(1, 2, 3, 0, 0x24)
        self.assertEqual(cpu.r, good_r, 'AND $1, $2, $3 failed')

        good_r[3] = 0
        cpu.execute_R(0, 2, 3, 0, 0x24)
        self.assertEqual(cpu.r, good_r, 'AND $0, $2, $3 failed')

    def testOR(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 11
        cpu.r[2] = 10
        good_r[1] = 11
        good_r[2] = 10
        good_r[3] = 11
        cpu.execute_R(1, 2, 3, 0, 0x25)
        self.assertEqual(cpu.r, good_r, 'OR $1, $2, $3 failed')

        cpu.r[31] = 0xFFFFFFFF
        good_r[31] = 0xFFFFFFFF
        cpu.execute_R(31, 31, 31, 0, 0x25)
        self.assertEqual(cpu.r, good_r, 'OR $31, $31, $31 failed')

    def testSLL(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 0x00000001
        good_r[1] = 0x1 << 16
        cpu.execute_R(0, 1, 1, 16, 0x00)
        self.assertEqual(cpu.r, good_r, 'SLL $1, $1, 16 failed')

        good_r[3] = 0
        cpu.execute_R(1, 3, 0, 32, 0x24)
        self.assertEqual(cpu.r, good_r, 'SLL $1, $3, 32 failed')

    def testSLR(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 0x80000000
        good_r[1] = 0x1 << 15
        cpu.execute_R(0, 1, 1, 16, 0x02)
        self.assertEqual(cpu.r, good_r, 'SLR $1, $1, 16 failed')

        good_r[3] = 0
        cpu.execute_R(1, 3, 0, 32, 0x24)
        self.assertEqual(cpu.r, good_r, 'SLR $1, $3, 32 failed')



if __name__ == '__main__':
    unittest.main()