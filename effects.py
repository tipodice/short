import subprocess
from log import logger  # Assuming logger is properly configured in the 'log' module

def vintage(input_video, output_file, fps='10'):
    """
    Apply a vintage effect to a video.

    Parameters:
    - input_video (str): Path to the input video file.
    - output_file (str): Path to the output video file.
    - fps (str): Frames per second for the output video.

    Returns:
    - None
    """
    logger.info('Applying vintage effect to video')

    # Adjust frame rate
    framerate_process = subprocess.Popen(['ffmpeg', '-i', input_video, '-filter:v', f'fps={fps}', 'tmp/td-fast.mp4'], text=True)
    stdout, stderr = framerate_process.communicate()

    if framerate_process.returncode == 0:
        # Apply vintage effect
        vintage_process = subprocess.Popen(['ffmpeg', '-i', 'tmp/td-fast.mp4', '-vf', 'curves=vintage', 'tmp/td-vintage-fast.mp4'], text=True)
        stdout, stderr = vintage_process.communicate()

        if vintage_process.returncode == 0:
            # Overlay vintage effect on an old film template
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
    """
    Apply a grayscale effect to a video.

    Parameters:
    - input_video (str): Path to the input video file.
    - output_file (str): Path to the output video file.

    Returns:
    - None
    """
    try:
        # Apply grayscale effect
        process = subprocess.Popen(['ffmpeg',
                                    '-i', input_video,
                                    '-vf', 'hue=s=0', output_file],
                                    text=True)
        _, stderr = process.communicate()

        if process.returncode == 0:
            logger.info('Video successfully filtered with grayscale effect')

    except Exception as e:
        logger.error(f'An error occurred: {e}')
        raise e
