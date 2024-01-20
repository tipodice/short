import subprocess
from log import logger


def vintage(input_video, output_file, fps='10'):
    logger.info('Applying vintage effect to video')
    framerate_process = subprocess.Popen(['ffmpeg', '-i', input_video, '-filter:v', f'fps=fps={fps}', 'tmp/td-fast.mp4'], text=True)
    stdout, stderr = framerate_process.communicate()
    if framerate_process.returncode == 0:
        vintage_process = subprocess.Popen(['ffmpeg', '-i', 'tmp/td-fast.mp4', '-vf', 'curves=vintage', 'tmp/td-vintage-fast.mp4'], text=True)
        stdout, stderr = vintage_process.communicate()
        if vintage_process.returncode == 0:
            overlay_process = subprocess.Popen(['ffmpeg',
                                                '-i', 'templates/oldFilm1080.mp4',
                                                '-i', 'tmp/td-vintage-fast.mp4',
                                                '-filter_complex', '[0]format=rgba,colorchannelmixer=aa=0.25[fg];[1][fg]overlay[out]',
                                                '-map', '[out]',
                                                '-pix_fmt', 'yuv420p',
                                                '-c:v', 'libx264',
                                                '-crf', '23',
                                                output_file], text=True)
            _, stderr = overlay_process.communicate()
            if overlay_process.returncode == 0:
                logger.info('Video successfully filtered with vintage effect')
            
def grayscale(input_video, output_file):
    try:
        process =  subprocess.Popen(['ffmpeg',
                                    '-i', input_video,
                                    '-vf', 'hue=s=0', output_file],
                                    text=True)
        _, stderr = process.communicate()

        if process.returncode == 0:
            logger.info(f'Video succesfully filter with with grayscale')
    except Exception as e:
        raise e
