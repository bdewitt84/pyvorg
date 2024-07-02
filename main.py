# Standard Python imports
import os

# Additional imports
from dotenv import load_dotenv

# Docs
# https://pytube.io/en/latest/index.html
# https://www.omdbapi.com/
# https://api.movieposterdb.com/docs/#docs/documentation/
# https://guessit.readthedocs.io/en/latest/

# TODO: Implement http://www.opensubtitles.org/en API
# https://opensubtitles.stoplight.io/docs/opensubtitles-api/e3750fd63a100-getting-started
# There exists python-opensubtitles

# TODO: Moving files needs to take associated subtitles, at the very least.


def organize_collection(collection, path, rem_empty=False):
    # TODO: Implement dest formatting
    for entry in collection:
        video = collection[entry]
        if video_verify(video):
            dest = generate_video_dir_name(video, path)
            make_dir(path)
            video_place(video, dest)
            if rem_empty:
                remove_empty_dir(path)
    metadata_save(collection)


def organize_collection_buffer(collection, path, rem_empty=False):
    buffer = CommandBuffer()
    for entry in collection:
        video = collection[entry]
        if video_verify(video):
            dest = make_dir(video, path)
            video_place(video, dest)
            if rem_empty:
                remove_empty_dir(path)
    metadata_save(collection)


def mimic_folder(src, dest):
    gen = integer_generator()
    for dirpath, _, filenames in os.walk(src):
        for name in filenames:
            src_path = os.path.join(dirpath, name)
            relative_to_src = dirpath[len(src) + 1:]
            file_path = os.path.join(dest, relative_to_src, name)
            new_dir = os.path.join(dest, relative_to_src)
            os.makedirs(new_dir, exist_ok=True)
            print('Creating dummy of ' + src_path + ' at\n' + file_path)
            with open(file_path, 'w') as file:
                file.write(str(next(gen)))
                file.close()


def organize_demo(collection, dest):
    cb = CommandBuffer()
    for entry in collection:
        video = collection[entry]
        vid_dest = generate_video_dir_name(video, dest)
        cmd = MoveVideo(video, vid_dest)
        cb.add_command(cmd)

    return cb


if __name__ == "__main__":
    load_dotenv('./config.env')
    source = os.getenv('SOURCE_PATH')
    dest = os.getenv('DEST_PATH')

    logger_init()

    src = 'C:/Users/User/Desktop/DummyVid'
    dst = 'C:/Users/User/Desktop/TestDir'
    mimic_folder(src, dst)

    # c = Collection()
    # c.load_metadata('./metadata.json.bak')
    # c.organize_files(dest)

    # temp_src = tempfile.TemporaryDirectory()
    # temp_dest = tempfile.TemporaryDirectory()
    # mimic_folder(source, temp_src.name)
    # c = Collection()
    # c.scan_directory(temp_src.name)
    # c.update_guessit()
    # c.update_omdb()
    # c.filter_non_serializable()
    # c.organize_files(temp_dest.name)
    # input(f'Organized test at {temp_dest.name}, press ENTER to quit.')
    # temp_src.cleanup()
    # temp_dest.cleanup()
