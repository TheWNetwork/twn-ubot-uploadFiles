# -*- encoding: utf-8 -*-
"""Main module"""
import os


import config
import datetime
import logging
from pyrogram import Client, enums
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument

logging.basicConfig(level=logging.ERROR)
app = Client(
    name="bot",
    api_id=config.api_id,
    api_hash=config.api_hash,
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


async def main():
    async with app:
        files = os.listdir(config.document_root)
        files = [f for f in files if os.path.isfile(config.document_root + '/' + f)]  # Filtering only the files.

        if config.start_date:
            schedule = datetime.datetime.strptime(config.start_date, '%Y-%m-%d %H:%M:%S')
        else:
            schedule = datetime.datetime.now()
        counter = len(files)
        curr = 0
        in_exe = False
        n_file = []

        order_by_extension = ['jpg', 'jpeg', 'png']
        keys = {k: v for v, k in enumerate(order_by_extension)}
        sorted(files, key=lambda x: keys.get(os.path.splitext(x)[1].strip('.'), float('inf')))

        for x in files:
            if not in_exe:
                if config.interval != 0:
                    schedule = schedule + datetime.timedelta(minutes=config.interval)
                else:
                    schedule = schedule + datetime.timedelta(seconds=60)

            curr = curr + 1
            start_date = datetime.datetime.now()
            size = get_file_size_in_mb(config.document_root + '/' + x)
            print(str(curr) + '/' + str(counter) + ' [' + datetime.datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S") + '][' + str(size) + 'MB] Uploading ' + x + ' at ' + str(schedule))
            extension = x.split('.')[-1]
            try:
                n_extension = files[curr].split('.')[-1]
            except IndexError:
                n_extension = None

            if extension == 'jpg' or extension == 'png' or extension == 'jpeg':
                if n_extension == extension and len(n_file) <= 8:
                    if len(n_file) == 0:
                        n_file.append(InputMediaPhoto(config.document_root + '/' + x, caption=config.caption, parse_mode=enums.ParseMode.HTML))
                    else:
                        n_file.append(InputMediaPhoto(config.document_root + '/' + x))
                    in_exe = True
                else:
                    if len(n_file) > 0:
                        n_file.append(InputMediaPhoto(config.document_root + '/' + x))
                        await app.send_media_group(
                            chat_id=int(config.chat_id),
                            media=n_file,
                            schedule_date=schedule
                        )
                        n_file = []
                    else:
                        await app.send_photo(
                            chat_id=int(config.chat_id),
                            photo=config.document_root + '/' + x,
                            schedule_date=schedule,
                            caption=config.caption,
                            parse_mode=enums.ParseMode.HTML
                        )
            elif extension == 'mp4' or extension == 'mkv' or extension == 'avi' or extension == 'mov':
                if n_extension == extension and len(n_file) <= 3:
                    if len(n_file) == 0:
                        n_file.append(InputMediaVideo(config.document_root + '/' + x, caption=config.caption, parse_mode=enums.ParseMode.HTML))
                    else:
                        n_file.append(InputMediaVideo(config.document_root + '/' + x))
                    in_exe = True
                else:
                    if len(n_file) > 0:
                        n_file.append(InputMediaVideo(config.document_root + '/' + x))
                        await app.send_media_group(
                            chat_id=int(config.chat_id),
                            media=n_file,
                            schedule_date=schedule
                        )
                        n_file = []
                    else:
                        await app.send_video(
                            chat_id=int(config.chat_id),
                            video=config.document_root + '/' + x,
                            schedule_date=schedule,
                            caption=config.caption,
                            progress=progress,
                            parse_mode=enums.ParseMode.HTML
                        )
            else:
                if n_extension == extension and len(n_file) <= 3:
                    if len(n_file) == 0:
                        n_file.append(InputMediaDocument(config.document_root + '/' + x, caption=config.caption, parse_mode=enums.ParseMode.HTML))
                    else:
                        n_file.append(InputMediaDocument(config.document_root + '/' + x))
                    in_exe = True
                else:
                    if len(n_file) > 0:
                        n_file.append(InputMediaDocument(config.document_root + '/' + x))
                        await app.send_media_group(
                            chat_id=int(config.chat_id),
                            media=n_file,
                            schedule_date=schedule
                        )
                        n_file = []
                    else:
                        await app.send_document(
                            chat_id=int(config.chat_id),
                            document=config.document_root + '/' + x,
                            schedule_date=schedule,
                            caption=config.caption,
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
