# kar-ai-oke
powerpoint karaoke slide generator using chatgpt and dall-e

## Introduction

The kar-ai-oke is a fun and interactive Python script designed to generate humorous and whimsical presentations for PowerPoint Karaoke.

## Installation

To get started with the Silly Presentation Topic Generator, follow these simple installation steps:

1. Ensure that Python 3.6 or later is installed on your system. You can download Python [here](https://www.python.org/downloads/).
2. Clone this repository to your local machine. Open a terminal and run:
git clone https://github.com/dfeldman/kar-ai-oke.git
3. Navigate to the cloned repository's directory:
cd kar-ai-oke
4. Install dependencies with pip3 install -r requirements.txt .

## Usage

First, generate an OpenAI API key in the OpenAI console. Set it in the environment like export OPENAI_API_KEY=<your unique code here>.

To generate a silly presentation topic, simply run the script from the command line:

python3 kar-ai-oke.py

You can either specify a topic, or press enter to get a randomly generated topic.

The script will output a randomly generated presentation in the presentation/ folder. Open presentation/index.html in your web browser.

Slides advance automatically every 20 seconds, or you can use arrow keys to go back and forth. 

## Bugs/Improvements

It would be nice to have a different template for the title vs. the other slides, or other random templates. 

It might be fun to have some slides that just have the image alone to make the player scramble.

Some randomly generated charts might be fun. 

If the bullet point is one censored by OpenAI (like "Dark Web"), image generation may fail. It will appear as a white background.

The number of slides may vary a bit depending on ChatGPT's mood.

The output always goes to presentation/. It will overwrite anything that's already there. 

It would be fun to make this a web app. 

## Cost

The text generation cost is trivial.

As of this writing, OpenAI charges $0.04 cents per image, and each generated deck has around 20 images. So it costs about $0.80 to run this script. 

Other image generation providers may be cheaper.

## Examples

Explore our examples to see the kind of fun and quirky presentation topics you can generate:

- [Example: Walrus](https://dfeldman.github.io/kar-ai-oke/examples/example_walrus/index.html)
- [Example: Chocolate](https://dfeldman.github.io/kar-ai-oke/examples/example_chocolate/index.html)
- [Example: Gnome](https://dfeldman.github.io/kar-ai-oke/examples/example_gnome/index.html)
- [Example: Pumpkin](https://dfeldman.github.io/kar-ai-oke/examples/example_pumpkin/index.html)

