# ./source/services/stageorganizevideofiles_svc.py

# Standard library
from typing import Optional
from pathlib import Path
from itertools import repeat

# Local imports
from source.commands.cmdbuffer import CommandBuffer
from source.state.col import Collection
from source.utils import \
    collectionutils, \
    configutils, \
    cmdutils


# Third party packages
# n/a


class StageOrganizeVideoFiles:
    def __init__(self):
        pass

    def call(self,
             collection: Collection,
             command_buffer: CommandBuffer,
             destination: Optional[str] = None,
             format_str: Optional[str] = None,
             filter_strings: Optional[list[str]] = None) -> None:

        destination = Path(destination).resolve() or configutils.get_default_organize_path()
        format_str = format_str or configutils.get_default_format_str()

        videos = collectionutils.get_filtered_videos(collection, filter_strings)
        cmd_arg_tuples = zip(videos, repeat(destination), repeat(format_str))
        cmd_kwarg_dicts = repeat({})
        cmds = cmdutils.build_commands('MoveVideoCmd', cmd_arg_tuples, cmd_kwarg_dicts)
        cmdutils.stage_commands(command_buffer, cmds)
