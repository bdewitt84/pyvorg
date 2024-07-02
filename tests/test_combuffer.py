# tests/test_combuffer.py

import unittest

from source.combuffer import *


class TestCommand(Command):

    def __init__(self):
        self.exec_is_valid_called = False
        self.undo_is_valid_called = False
        self.execute_called = False
        self.undo_called = False

    def validate_exec(self):
        self.exec_is_valid_called = True

    def validate_undo(self):
        self.undo_is_valid_called = True

    def execute(self):
        self.execute_called = True

    def undo(self):
        self.undo_called = True


class TestCommandBuffer(unittest.TestCase):

    def test_add_command_valid(self):
        buffer = CommandBuffer()
        cmd = TestCommand()
        buffer.add_command(cmd)
        self.assertTrue(cmd in buffer.cmd_buffer.queue)

    def test_add_command_invalid(self):
        buffer = CommandBuffer()
        cmd = False
        with self.assertRaises(ValueError):
            buffer.add_command(cmd)

    def test_exec_command(self):
        buffer = CommandBuffer()
        cmd = TestCommand()
        buffer.cmd_buffer.put(cmd)

        buffer.exec_command()
        self.assertTrue(cmd.execute_called)
        self.assertTrue(buffer.cmd_buffer.empty())
        self.assertTrue(cmd in buffer.undo_buffer)

    def test_undo_cmd(self):
        buffer = CommandBuffer()
        cmd = TestCommand()
        buffer.undo_buffer.append(cmd)

        buffer.undo_cmd()
        self.assertTrue(cmd.undo_called)
        self.assertFalse(buffer.undo_buffer)

    def test_execute_buffer(self):
        cb = CommandBuffer()
        cmd1 = TestCommand()
        cmd2 = TestCommand()
        cmd3 = TestCommand()
        cb.cmd_buffer.put(cmd1)
        cb.cmd_buffer.put(cmd2)
        cb.cmd_buffer.put(cmd3)

        cb.execute_cmd_buffer()
        self.assertTrue(cb.cmd_buffer.empty())
        self.assertTrue(cmd1.execute_called)
        self.assertTrue(cmd2.execute_called)
        self.assertTrue(cmd3.execute_called)
        self.assertTrue(cb.undo_buffer == [cmd1, cmd2, cmd3])
