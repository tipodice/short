import os
import argparse
from venv import logger
import pexels
import utils
import effects
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

PEXELS_FOLDER = os.environ.get('PEXELS_FOLDER')
TMP_FOLDER = os.environ.get('TMP_FOLDER')


def main(input_text=None, topic=None, fx=None):
    """
    Main function to generate a short video based on input text and topic.

    Parameters:
    - input_text (str): Input text for the video.
    - topic (str): Topic for the video.
    - fx (list): List of effects to apply to the video.

    Returns:
    None
    """
    try:
        utils.create_folder(PEXELS_FOLDER)
        utils.text_to_speech(input_text, f'{TMP_FOLDER}t2s.wav')
        pexels.download_videos(topic, output_folder=PEXELS_FOLDER, total_pages=1)

        video_paths = [os.path.join(PEXELS_FOLDER, file) for file in os.listdir(PEXELS_FOLDER)]
        utils.merge_videos(video_paths, output_file=f'{TMP_FOLDER}merged.mp4')
        
        if fx:
            # apply effects if any after merging videos
            if 'vintage' in fx and 'grayscale' in fx:
                effects.vintage(f'{TMP_FOLDER}merged.mp4', f'{TMP_FOLDER}vintage.mp4')
                effects.grayscale(f'{TMP_FOLDER}vintage.mp4', f'{TMP_FOLDER}effects.mp4')
            else:
                if 'grayscale' in fx:
                    effects.grayscale(f'{TMP_FOLDER}merged.mp4', f'{TMP_FOLDER}effects.mp4')
                elif 'vintage' in fx:
                    effects.vintage(f'{TMP_FOLDER}merged.mp4', f'{TMP_FOLDER}effects.mp4')
            #
            utils.audio_into_video(f'{TMP_FOLDER}effects.mp4', f'{TMP_FOLDER}t2s.wav', output_file=f'{TMP_FOLDER}merged_and_audio.mp4')
        else:
            utils.audio_into_video(f'{TMP_FOLDER}merged.mp4', f'{TMP_FOLDER}t2s.wav', output_file=f'{TMP_FOLDER}merged_and_audio.mp4')
               
        utils.generate_srt(f'{TMP_FOLDER}t2s.wav', f'{TMP_FOLDER}sub.srt')
        utils.embed_srt_into_video(f'{TMP_FOLDER}merged_and_audio.mp4', f'{TMP_FOLDER}sub.srt', 'video.mp4')
    except Exception as e:
        utils.clean_up()
        raise e
    finally:
        utils.clean_up()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate a short video based on input text and topic.")
    parser.add_argument("-i", "--input", dest="input_text", required=True, help="Input text file for the video")
    parser.add_argument("-t", "--topic", dest="topic", required=True, help="Topic for the video")
    parser.add_argument("-fx", "--effects", dest="fx", help="List of effects to apply to the video")
    args = parser.parse_args()

    # Read input text file
    with open(args.input_text, 'r') as file:
        input_text_content = file.read()

    fxs = args.fx.strip().split(',')
    main(input_text=input_text_content, topic=args.topic, fx=fxs)
