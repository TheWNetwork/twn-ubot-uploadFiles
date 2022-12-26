# -*- encoding: utf-8 -*-
"""Main module"""
import os
import config
import datetime
import logging
from pyrogram import Client, enums

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

        for x in files:
            if config.interval != 0:
                schedule = schedule + datetime.timedelta(hours=config.interval)
            else:
                schedule = schedule + datetime.timedelta(seconds=60)

            startedat = datetime.datetime.now()
            size = get_file_size_in_mb(config.document_root + '/' + x)
            curr = curr + 1
            print(str(curr) + '/' + str(counter) + ' [' + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + '][' + str(size) + 'MB] Uploading ' + x + ' at ' + str(schedule))
            extension = x.split('.')[-1]

            if extension == 'jpg' or extension == 'png' or extension == 'jpeg':
                await app.send_photo(
                    chat_id=int(config.chat_id),
                    photo=config.document_root + '/' + x,
                    schedule_date=schedule,
                    caption=config.caption,
                    parse_mode=enums.ParseMode.HTML
                )
            elif extension == 'mp4' or extension == 'mkv' or extension == 'avi' or extension == 'mov':
                await app.send_video(
                    chat_id=int(config.chat_id),
                    video=config.document_root + '/' + x,
                    schedule_date=schedule,
                    caption=config.caption,
                    progress=progress,
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await app.send_document(
                    chat_id=int(config.chat_id),
                    document=config.document_root + '/' + x,
                    schedule_date=schedule,
                    caption=config.caption,
                    progress=progress,
                    parse_mode=enums.ParseMode.HTML
                )

            difference = datetime.datetime.now() - startedat
            if difference.total_seconds() != 0:
                speed = round(size / round(difference.total_seconds(), 4), 2)
            else:
                speed = 1

            print("\r", 'Finished: ' + x
                  + '. Size: ' + str(size)
                  + 'MB ' + str(round(difference.total_seconds(), 4)) + 's at '
                  + str(speed) + ' MB/s')

app.run(main())
