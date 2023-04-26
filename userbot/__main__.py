import os
import cv2
import logging
import pathlib
import imageio
import datetime
from PIL import Image
from .config import Config
from pyrogram import Client, enums
from moviepy.video.io.VideoFileClip import VideoFileClip
from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaDocument


logging.basicConfig(level=logging.ERROR)
app = Client(
    name="bot",
    api_id=Config.api_id,
    api_hash=Config.api_hash,
)


def progress(current, total):
    percent = 100 * (current / total)
    bar = '▋' * int(percent) + '-' * (100 - int(percent))
    print("\r", f'\r[{bar}] {round(percent, 2)}%', end='')


def get_file_size_in_mb(file_path):
    stat_info = os.stat(file_path)
    size = stat_info.st_size / 1024 / 1024
    return int(round(size, 2))


def file_list(path, sett):
    pathlib.Path(path)
    for filepath in pathlib.Path(path).glob("**/*"):
        if os.path.isdir(filepath):
            file_list(filepath, sett)
        else:
            sett.add(str(filepath.parent) + "/" + str(filepath.name))
    return sett


def resizer2(_image_):
    img = Image.open(_image_)
    path_, ext_ = os.path.splitext(_image_)
    newname = path_+"lite"+ext_
    # newname = str(_image_).split('.')[0] + "_resize." + str(_image_).split('.')[1]
    img.save(newname, optimize=True, quality=85)
    return newname


def resizer(_image_):
    with Image.open(_image_) as img:
        width, height = img.size
        print(f"Width={width} - Height={height}")
        img = img.convert("RGB")

    if width * height > 5242880 or width > 4096 or height > 4096:
        new_width, new_height = width, height
        while new_width * new_height > 5242880 or new_width > 4096 or new_height > 4096:
            new_width = int(new_width * 0.9)
            new_height = int(new_height * 0.9)

        resized_img = img.resize((new_width, new_height))
    else:
        resized_img = img

    path_, ext_ = os.path.splitext(_image_)
    newname = path_+"lite"+ext_
    resized_img.save(newname)
    return newname


def thumbail_(_video_):
    path_, ext_ = os.path.splitext(_video_)
    namethumb = path_+".jpg"
    if ext_.lower() == ".mp4":
        print("mp4")
        # Abrir el video
        cap = cv2.VideoCapture(_video_)
        # Obtener el número de fotogramas
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Establecer el fotograma alrededor del cual queremos tomar la miniatura
        frame_to_capture = int(total_frames / 3)
        # Establecer la posición del fotograma
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_to_capture)
        # Leer el fotograma
        ret, frame = cap.read()
        # Guardar la miniatura como imagen
        cv2.imwrite(namethumb, frame)
        # Liberar los recursos
        cap.release()
    elif ext_.lower() == ".mkv":
        print("mkv")
        # Abrir el archivo MKV
        video = VideoFileClip(_video_)
        # Obtener la miniatura en el segundo 5 del video
        thumbnail = video.get_frame(20)
        # Guardar la miniatura como imagen
        imageio.imwrite(namethumb, thumbnail)
        # Liberar los recursos
        video.close()
    elif ext_.lower() == ".mov":
        print("mov")
        # Abrir el archivo MOV
        try:
            video = VideoFileClip(_video_)
            # Obtener la miniatura en el segundo 5 del video
            thumbnail = video.get_frame(5)
            # Guardar la miniatura como imagen
            #thumbnail.save_frame(newname)
            #np.savetxt('thumbnail.jpg', thumbnail)
            imageio.imwrite(namethumb, thumbnail)
            video.write_videofile(path_+".mp4")
            # Liberar los recursos
            video.close()
            print("El archivo MOV parece estar bien.")
        except:
            print("El archivo MOV parece estar dañado.")
            return None
    return namethumb

async def main():
    async with app:

        filename = sorted(list(file_list(Config.document_root, set())))

        if Config.start_date:
            schedule = datetime.datetime.strptime(Config.start_date, '%Y-%m-%d %H:%M:%S')
        else:
            schedule = datetime.datetime.now()

        counter = len(filename)
        curr = 0
        in_exe = False
        n_file = []
        n_file_raw = []

        order_by_extension = ['jpg', 'jpeg', 'png']
        keys = {k: v for v, k in enumerate(order_by_extension)}
        filename = sorted(filename, key=lambda y: keys.get(str(y).split('.')[1], float('inf')))

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
            if extension.lower() in {'jpg', 'png', 'jpeg'}:
                x_resize = resizer(x)
                if n_extension == extension and len(n_file) <= 8:
                    if len(n_file) == 0:
                        n_file.append(InputMediaPhoto(x_resize, caption=Config.caption, parse_mode=enums.ParseMode.HTML))
                        n_file_raw.append(InputMediaDocument(x, parse_mode=enums.ParseMode.HTML))
                    else:
                        n_file.append(InputMediaPhoto(x_resize))
                        n_file_raw.append(InputMediaDocument(x))
                    in_exe = True
                else:
                    if len(n_file) > 0:
                        n_file.append(InputMediaPhoto(x_resize))
                        n_file_raw.append(InputMediaDocument(x))
                        await app.send_media_group(
                            chat_id=int(Config.chat_id),
                            media=n_file,
                            schedule_date=schedule
                        )
                        await app.send_media_group(
                            chat_id=int(Config.chat_id),
                            media=n_file_raw,
                            schedule_date=schedule
                        )
                        n_file = []
                        n_file_raw = []
                    else:
                        await app.send_photo(
                            chat_id=int(Config.chat_id),
                            photo=x_resize,
                            schedule_date=schedule,
                            caption=Config.caption,
                            parse_mode=enums.ParseMode.HTML
                        )
                        await app.send_document(
                            chat_id=int(Config.chat_id),
                            document=x,
                            schedule_date=schedule,
                            parse_mode=enums.ParseMode.HTML
                        )
            elif extension.lower() in {'mp4', 'mkv', 'avi', 'mov'}:
                _thumbs_ = thumbail_(x)
                if extension.lower()=="mov":
                    if _thumbs_ == None:
                        print(f"pass video corrupted:{x}")
                        continue
                    path_, ext_ = os.path.splitext(x)
                    x = path_+".mp4"
                if n_extension == extension and len(n_file) <= 8:
                    if len(n_file) == 0:
                        n_file.append(InputMediaVideo(x, thumb=_thumbs_, caption=Config.caption, parse_mode=enums.ParseMode.HTML))
                    else:
                        n_file.append(InputMediaVideo(x, thumb=_thumbs_))
                    in_exe = True
                else:
                    if len(n_file) > 0:
                        n_file.append(InputMediaVideo(x, thumb=_thumbs_))
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
                            thumb=_thumbs_,
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
