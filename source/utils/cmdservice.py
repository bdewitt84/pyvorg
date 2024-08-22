# source/utils/cmdservice.py

# Standard library
from typing import Iterable, Type

# Local imports
from source.command.combuffer import Command, CommandBuffer
from source.command.update_video_data import UpdateVideoData
from source.command.move_video import MoveVideo

# Third-party packages


def clear_exec_buffer(command_buffer: CommandBuffer) -> None:
    command_buffer.clear_exec_buffer()


def execute_cmd_buffer(command_buffer: CommandBuffer) -> None:
    command_buffer.execute_cmd_buffer()


def get_exec_preview(command_buffer):
    return str(command_buffer)


def build_command(cmd: Type[Command], *args, **kwargs):
    # TODO: Consider using a factory pattern
    return cmd(*args, **kwargs)


def build_commands(cmd_name: str, params_list: Iterable[tuple]) -> list[Command]:
    # TODO: Consider using a factory pattern
    cmd = get_command_from_name(cmd_name)
    return [cmd(*params) for params in params_list]


def get_command_from_name(command_name) -> Type:
    # TODO: Use discovery like plugins, or use a registry instead. I think we might try
    #       the registry approach, since it does not imply that the user should be
    #       adding their own commands
    if command_name == 'MoveVideo':
        return MoveVideo
    elif command_name == 'UpdateVideoData':
        return UpdateVideoData
    else:
        raise ValueError(f"'{command_name}' is not a valid command name")


def stage_commands(command_buffer: CommandBuffer, cmds: list[Command]) -> None:
    for cmd in cmds:
        command_buffer.add_command(cmd)
