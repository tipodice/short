# short video generator

`short.py`, generates a short video based on input text, a specified topic, and optional visual effects. It leverages the Pexels API to download relevant video content, combines them, applies effects, and embeds audio generated from the input text.

## Prerequisites

- Python 3.x
- Pexels API token (Get it from [Pexels](https://www.pexels.com/api/))
- Packages listed in `requirements.txt`

## Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/short.git
   cd short
2. **Create a virtual environment and install dependencies**
   ```
      python3 -m venv venv
      source venv/bin/activate  # On Windows: venv\Scripts\activate
      pip install -r requirements.txt
   ```
3. **Create a .env file in the project root and add your Pexels API token**
   ```
      API_KEY = '3tOXxNd2EMlUydvdpItTV5gYlMa6pIBmwl3hy23SxIzSeb5UMkTYa9Bwq'
      TMP_FOLDER = 'tmp/'
      PEXELS_FOLDER = 'tmp/pexels/'

## Usage
Run the script from the command line with the following options:

   ```
   python3 short.py -i path/to/input_text.txt -t your_topic -fx effect1,effect2
   ```
   -i or --input: Path to the input text file.

   
   -t or --topic: Topic for the video (e.g., "landscape" or "mountains").

   
   -fx or --effects: List of visual effects to apply to the video, separated by commas (e.g., "vintage,grayscale").

## Example
   ```
   python3 short.py -i test.txt -t landscape -fx vintage,grayscale
   ```
   
## Notes
   Ensure the input text file (input_text.txt) and topic are provided.
   Visual effects are optional and can be specified using the -fx option.
   Clean-up is handled in the script's finally block, ensuring temporary files are removed even in case of errors.