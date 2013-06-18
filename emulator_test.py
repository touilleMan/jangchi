#! /usr/bin/env python

import unittest
from emulator import Cpu, Memory


class Test_memory(unittest.TestCase):
    mem = 0

    class FakeMem():
        def __init__(self, array, indice):
            self.array = array
            self.indice = indice
        def setter(self, val):
            self.array[self.indice] = val
        def getter(self):
            return self.array[self.indice]

    def testBind(self):
        bind = [0, 1, 2, 3, 4]
        memory = Memory()

        fm = self.FakeMem(bind, 0x3)
        memory.bind(0x3, callback=)
        memory[0x3] = 0x11
        self.assertEqual(memory[0x3], bind[0x3], 'IO bind setter failed')

        memory.bind(0x3, setter=None, getter=fm.getter)
        self.assertEqual(0x11, bind[0x3], 'IO bind getter failed')

        fm = self.FakeMem(bind, 0x0)
        memory.bind(0x0, bitmask=0b101, setter=fm.setter, getter=fm.getter)
        memory[0x0] = 0b111
        self.assertEqual(bind[0x0], 0b101, 'IO bind with bitmask failed')

        memory[0x0] = 0
        bind[0x0] = 0b111111
        self.assertEqual(memory[0x0], 0b101, 'IO bind with bitmask failed')

        memory[0x0] = 0b010
        bind[0x0] = 0b111111
        self.assertEqual(memory[0x0], 0b111, 'IO bind with bitmask failed')


    def testMemory(self):
        memory = Memory()
        memory[0x42] = 1
        self.assertEqual(memory[0x42], 1)


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


class Test_execute_I(unittest.TestCase):

    def testBEQ(self):
        cpu = Cpu()
        cpu.execute_I_BEQ(0, 0, 0x42)
        self.assertEqual(cpu.pc, 0x42 << 2, 'BEQ $0, $0, 0x42 failed')
        cpu.execute_I_BEQ(0, 0, -0x42)
        self.assertEqual(cpu.pc, 0, 'BEQ $0, $0, 0x42 failed')


class Test_execute_J(unittest.TestCase):

    def testJump(self):
        cpu = Cpu()
        cpu.execute_J_JUMP(0x4)
        self.assertEqual(cpu.fake_pc, 0x4, 'JUMP 0x4 failed')

        cpu.execute_J_JUMP(-0x44)
        # Must make and overflow on the uint32_t pc
        self.assertEqual(cpu.fake_pc, -(1<<31)-0x44, 'JUMP -0x44 failed')
        cpu.execute_J_JUMP(0x4)


if __name__ == '__main__':
    unittest.main()