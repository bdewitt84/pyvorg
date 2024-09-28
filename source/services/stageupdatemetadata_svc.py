# ./source/services/stageupdatemetadata_svc.py

# Standard library
from typing import Optional
from itertools import repeat

# Local imports
import source.datasources
from source.state.col import Collection
from source.commands.cmdbuffer import CommandBuffer
from source.utils import \
    videoutils, \
    collectionutils, \
    pluginutils, \
    cmdutils

# Third party packages
# n/a


class StageUpdateMetadata:
    def __init__(self):
        pass

    def call(self,
             collection: Collection,
             command_buffer: CommandBuffer,
             api_name: str,
             filter_strings: Optional[list[str]] = None) -> None:

        videos = collectionutils.get_filtered_videos(collection, filter_strings)
        api_instance = pluginutils.get_plugin_instance(api_name, source.datasources)
        req_plugin_params = pluginutils.get_required_params(api_instance)
        cmd_args_tuples = zip(videos, repeat(api_instance))
        cmd_kwargs_dicts = videoutils.build_cmd_kwargs(videos, req_plugin_params)
        cmds = cmdutils.build_commands('UpdateVideoData', cmd_args_tuples, cmd_kwargs_dicts)
        cmdutils.stage_commands(command_buffer, cmds)
