# source/service/cmd_svc.py

# Standard library
from typing import Iterable, Type

# Local imports
from source.state.combuffer import CommandBuffer
from source.state.command import Command
from source.state.update_video_data import UpdateVideoData
from source.state.move_video import MoveVideo

# Third-party packages


def clear_exec_buffer(command_buffer: CommandBuffer) -> None:
    command_buffer.clear_exec_buffer()


def execute_cmd_buffer(command_buffer: CommandBuffer) -> None:
    command_buffer.execute_cmd_buffer()


def get_exec_preview(command_buffer):
    return str(command_buffer)


def build_command(cmd_name: str, *args, **kwargs):
    cmd = get_command_from_name(cmd_name)
    return cmd(*args, **kwargs)


def build_commands(cmd_name: str, cmd_arg_tuples: Iterable[tuple], cmd_kwarg_dicts: Iterable[dict]) -> list[Command]:
    cmd = get_command_from_name(cmd_name)
    return [cmd(*cmd_arg_tuple, **cmd_kwarg_dict)
            for cmd_arg_tuple, cmd_kwarg_dict
            in zip(cmd_arg_tuples, cmd_kwarg_dicts)]


def get_command_from_name(command_name) -> Type:
    # TODO: Use discovery like plugins, or use a registry instead. I think we might try
    #       the registry approach, since it does not imply that the user should be
    #       adding their own commands. It also means we don't have to modify this
    #       class when adding a new command.
    if command_name == 'MoveVideo':
        return MoveVideo
    elif command_name == 'UpdateVideoData':
        return UpdateVideoData
    else:
        raise ValueError(f"'{command_name}' is not a valid command name")


def stage_commands(command_buffer: CommandBuffer, cmds: list[Command]) -> None:
    for cmd in cmds:
        command_buffer.add_command(cmd)


def execute_undo_buffer(command_buffer: CommandBuffer):
    command_buffer.execute_undo_buffer()
