import subprocess
import os
import torch
import random
from TTS.api import TTS
from vosk import Model, KaldiRecognizer, SetLogLevel
from log import logger


def create_folder(folder_path):
    """
    Create a folder if it does not exist.

    Args:
        folder_path (str): Path of the folder to create.
    Returns:
        None
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.info(f'Folder {folder_path} was created')

def clean_up():
    """
    Remove temporary and cache folders.

    Returns:
        None
    """
    command = ['rm', '-rf', 'tmp', '__pycache__']
    stream = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, _ = stream.communicate()

def text_to_speech(txt, output_file, speaker='p330'):
    """
    Convert text to speech and save it to a file.

    Args:
        txt (str): The text to convert.
        output_file (str): The path to save the speech.
        speaker (str, optional): Speaker identity. Defaults to 'p330'.
    Returns:
        None
    """
    try:
        # Available speakers
        speakers = ['ED', 'p225', 'p226', 'p227', 'p228', 'p229',
                    'p230', 'p231', 'p232', 'p233', 'p234', 'p236',
                    'p237', 'p238', 'p239', 'p240', 'p241', 'p243',
                    'p244', 'p245', 'p246', 'p247', 'p248', 'p249',
                    'p250', 'p251', 'p252', 'p253', 'p254', 'p255',
                    'p256', 'p257', 'p258', 'p259', 'p260', 'p261',
                    'p262', 'p263', 'p264', 'p265', 'p266', 'p267',
                    'p268', 'p269', 'p270', 'p271', 'p272', 'p273',
                    'p274', 'p275', 'p276', 'p277', 'p278', 'p279',
                    'p280', 'p281', 'p282', 'p283', 'p284', 'p285',
                    'p286', 'p287', 'p288', 'p292', 'p293', 'p294',
                    'p295', 'p297', 'p298', 'p299', 'p300', 'p301',
                    'p302', 'p303', 'p304', 'p305', 'p306', 'p307',
                    'p308', 'p310', 'p311', 'p312', 'p313', 'p314',
                    'p316', 'p317', 'p318', 'p323', 'p326', 'p329',
                    'p330', 'p333', 'p334', 'p335', 'p336', 'p339',
                    'p340', 'p341', 'p343', 'p345', 'p347', 'p351',
                    'p360', 'p361', 'p362', 'p363', 'p364', 'p374',
                    'p376']

        if not speaker:
            speaker = random.choice(speakers)

        if speaker in speakers:
            device = "cuda" if torch.cuda.is_available() else "cpu"

            tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False).to(device)
            logger.info('Converting text to speech, please wait...')
            tts.tts_to_file(txt, file_path=output_file, speaker=speaker)

    except Exception as e:
        raise e

def get_duration(file_path):
    """
    Get the duration of a media file using ffprobe.

    Parameters:
        file_path (str): The path to the input media file.

    Returns:
        float: The duration of the media file in seconds.

    Raises:
        subprocess.CalledProcessError: If ffprobe command fails.
        ValueError: If the duration cannot be converted to a float.
    """
    try:
        command = [
            "ffprobe",
            "-i",
            file_path,
            "-show_entries",
            "format=duration",
            "-v",
            "quiet",
            "-of",
            "csv=p=0",
        ]
        result = subprocess.check_output(command, stderr=subprocess.STDOUT)
        return float(result.strip())
    except subprocess.CalledProcessError as e:
        raise e
    except Exception as e:
        raise ValueError("Error - Unable to get duration")

def merge_videos(video_paths, output_file="finish.mp4"):
    """
    Merge multiple videos into a single video file using ffmpeg.

    Args:
        video_paths (list): List of paths to input video files.
        output_file (str): Output file name for the merged video.

    Returns:
        None
    """
    try:
        logger.info("Merging videos, please wait...")
        command = ["ffmpeg"]
        for path in video_paths:
            command.extend(["-i", path])

        filter_complex = "".join([f"[{i}:v]" for i in range(len(video_paths))])
        filter_complex += f"concat=n={len(video_paths)}:v=1:a=0[outv]"
        command.extend(["-filter_complex", filter_complex])
        command.extend(["-map", "[outv]", "-r", "30", output_file])
        stream = subprocess.Popen(command, text=True)
        stdout, stderr = stream.communicate()
        if stream.returncode == 0:
            logger.info(f"Videos successfully merged output => {output_file}") 
    except Exception as e:
        logger.error('Unable to merge videos')
        raise e

def audio_into_video(video, audio, output_file):
    """
    Merge audio into a video file.

    Args:
        video (str): Path to the input video file.
        audio (str): Path to the input audio file.

    Returns:
        None
    """
    try:
        logger.info("Merging audio into video")
        duration_audio = get_duration(audio)
        min_duration = duration_audio + 2

        command = [
            "ffmpeg",
            "-i", video,
            "-i", audio,
            "-filter_complex", f"[0:v]trim=0:{min_duration},setpts=PTS-STARTPTS[v];[1:a]atrim=0:{min_duration},asetpts=PTS-STARTPTS[a]",
            "-map", "[v]",
            "-map", "[a]",
            "-movflags", "+faststart",
            "-r", "30",
            output_file,
        ]

        stream = subprocess.Popen(command, text=True)
        stdout, stderr = stream.communicate()

        if stream.returncode == 0:
            logger.info(f'{audio} was successfully merged to {video} output => {output_file}')
        else:
            logger.error(f'Error merging {audio} into {video}: {stderr}')
    except subprocess.CalledProcessError as e:
        raise e
    except Exception as e:
        logger.error(f'Unable to merge {audio} into {video}: {str(e)}')
        raise e

def generate_srt(audio_file, output_file):
    """
    Generate SRT subtitles from an audio file using Vosk.

    Args:
        audio_file (str): Path to the audio file.
        output_file (str): Output file name for the generated srt file

    Returns:
        None
    """
    try:
        SAMPLE_RATE = 16000

        SetLogLevel(-1)

        model = Model(lang="en-us")
        rec = KaldiRecognizer(model, SAMPLE_RATE)
        rec.SetWords(True)
        logger.info('Generating srt subtitles files')
        with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
                                   audio_file,
                                   "-ar", str(SAMPLE_RATE), "-ac", "1", "-f", "s16le", "-"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout as stream:

            with open(output_file, "w") as file:
                file.write(rec.SrtResult(stream))
            logger.info('SRT file created successfully')
    except Exception as e:
        raise e

def embed_srt_into_video(video_input, srt_file_path, output_file, fps='30'):
    """
    Embed SRT subtitles into a video file.

    Args:
        video_input (str): Path to the input video file.
        output_file (str): Path to the output video file with subtitles.
    Returns:
        None
    """
    try:
        logger.info("Adding subtitles to videos")
        command = [
            "ffmpeg",
            "-i",
            video_input,
            "-vf",
            f"subtitles={srt_file_path}",
            "-r", fps,
            output_file
        ]
        stream = subprocess.Popen(
            command,
            text=True
        )
        stdout, stderr = stream.communicate()
        if stream.returncode == 0:
            logger.info(f'Subtitles successfully added output_file => {output_file}')
        else:
            raise ValueError('Error while merging subtitles to audio: ' + str(stderr))
    except Exception as e:
        raise e


if __name__ == "__main__":
    import sys
    print(generate_srt(sys.argv[1], sys.argv[2]))