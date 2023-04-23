import os
import pathlib

from .config import Config
import datetime
import logging
from pyrogram import Client, enums
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument

logging.basicConfig(level=logging.ERROR)
app = Client(
    name="bot",
    api_id=Config.api_id,
    api_hash=Config.api_hash,
)

# Keep track of the progress while uploading
def progress(current, total):
    percent = 100 * (current / total)
    bar = '▋' * int(percent) + '-' * (100 - int(percent))
    print("\r", f'\r[{bar}] {round(percent, 2)}%', end='')

def get_file_size_in_mb(file_path):
    stat_info = os.stat(file_path)
    size = stat_info.st_size / 1024 / 1024
    return int(round(size, 2))

def file_list(path, setT):
    pathlib.Path(path)
    for filepath in pathlib.Path(path).glob("**/*"):
        if os.path.isdir(filepath):
            file_list(filepath, setT)
        else:
            setT.add(str(filepath.parent)+"/"+str(filepath.name))
    return setT

# Variables
#DOCUMENT_ROOT="../downloads/"
filename = []
async def main():
    async with app:
        filename = sorted(list(file_list(Config.document_root, set())))
        print(len(filename))

        for f in filename:
            print(f)

        if Config.start_date:
            schedule = datetime.datetime.strptime(Config.start_date, '%Y-%m-%d %H:%M:%S')
        else:
            schedule = datetime.datetime.now()

        counter = len(filename)
        curr = 0
        in_exe = False
        n_file=[]

        order_by_extension = ['jpg', 'jpeg', 'png']
        keys = {k: v for v, k in enumerate(order_by_extension)}
        sorted(filename, key=lambda x: keys.get(os.path.splitext(x)[1].strip('.'), float('inf')))

        for x in filename:
            if not in_exe:
                if Config.interval != 0:
                    schedule = schedule + datetime.timedelta(minutes=Config.interval)
                else:
                    schedule = schedule + datetime.timedelta(seconds=60)

            curr += 1
            start_date = datetime.datetime.now()
            size = get_file_size_in_mb(x)
            print(str(curr) + '/' + str(counter) + ' [' + datetime.datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S") + '][' + str(size) + 'MB] Uploading ' + x + ' at ' + str(schedule))
            extension = x.split('.')[-1]

            try:
                n_extension = filename[curr].split('.')[-1]
            except IndexError:
                n_extension = None

            if extension == 'jpg' or extension == 'png' or extension == 'jpeg':
                if n_extension == extension and len(n_file) <= 8:
                    if len(n_file) == 0:
                        n_file.append(InputMediaPhoto(x, caption=Config.caption, parse_mode=enums.ParseMode.HTML))
                    else:
                        n_file.append(InputMediaPhoto(x))
                    in_exe = True
                else:
                    if len(n_file) > 0:
                        n_file.append(InputMediaPhoto(x))
                        await app.send_media_group(
                            chat_id=int(Config.chat_id),
                            media=n_file,
                            schedule_date=schedule
                        )
                        n_file = []
                    else:
                        await app.send_photo(
                            chat_id=int(Config.chat_id),
                            photo=x,
                            schedule_date=schedule,
                            caption=Config.caption,
                            parse_mode=enums.ParseMode.HTML
                        )

            elif extension == 'mp4' or extension == 'mkv' or extension == 'avi' or extension == 'mov':
                if n_extension == extension and len(n_file) <= 8:
                    if len(n_file) == 0:
                        n_file.append(InputMediaVideo(x, caption=Config.caption, parse_mode=enums.ParseMode.HTML))
                    else:
                        n_file.append(InputMediaVideo(x))
                    in_exe = True
                else:
                    if len(n_file) > 0:
                        n_file.append(InputMediaVideo(x))
                        await app.send_media_group(
                            chat_id=int(Config.chat_id),
                            media=n_file,
                            schedule_date=schedule
                        )
                        n_file = []
                    else:
                        await app.send_video(
                            chat_id=int(Config.chat_id),
                            video=x,
                            schedule_date=schedule,
                            caption=Config.caption,
                            progress=progress,
                            parse_mode=enums.ParseMode.HTML
                        )
            else:
                if n_extension == extension and len(n_file) <= 8:
                    if len(n_file) == 0:
                        n_file.append(InputMediaDocument(x, caption=Config.caption, parse_mode=enums.ParseMode.HTML))
                    else:
                        n_file.append(InputMediaDocument(x))
                    in_exe = True
                else:
                    if len(n_file) > 0:
                        n_file.append(InputMediaDocument(x))
                        await app.send_media_group(
                            chat_id=int(Config.chat_id),
                            media=n_file,
                            schedule_date=schedule
                        )
                        n_file = []
                    else:
                        await app.send_document(
                            chat_id=int(Config.chat_id),
                            document=x,
                            schedule_date=schedule,
                            caption=Config.caption,
                            progress=progress,
                            parse_mode=enums.ParseMode.HTML
                        )

            if not in_exe:
                difference = datetime.datetime.now() - start_date
                if difference.total_seconds() != 0:
                    speed = round(size / round(difference.total_seconds(), 4), 2)
                else:
                    speed = 1

                print("\r", 'Finished: ' + x
                      + '. Size: ' + str(size)
                      + 'MB ' + str(round(difference.total_seconds(), 4)) + 's at '
                      + str(speed) + ' MB/s')
                in_exe = False


app.run(main())
