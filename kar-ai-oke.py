import os
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
from html.parser import HTMLParser
import re
import random

api_key = os.getenv('OPENAI_API_KEY')

if api_key is None:
    raise EnvironmentError(
        "The OPENAI_API_KEY environment variable is not set. "
        "Please set it before running the script. For example, in Linux or macOS terminal: "
        "export OPENAI_API_KEY='your_api_key_here', or in Windows Command Prompt: "
        "set OPENAI_API_KEY=your_api_key_here"
    )

client = OpenAI(api_key=api_key)


n_image=0

JS_FILE="""
let currentSlide = 0;

function showSlide(index) {
    const slides = document.querySelectorAll('.slide');
    if (index >= slides.length) index = 0;
    if (index < 0) index = slides.length - 1;
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
    currentSlide = index;
}

function nextSlide() {
    showSlide(currentSlide + 1);
}

function previousSlide() {
    showSlide(currentSlide - 1);
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'ArrowRight') {
        nextSlide();
    } else if (event.key === 'ArrowLeft') {
        previousSlide();
    }
});

setInterval(nextSlide, 20000); // Auto-advance every 20 seconds

window.onload = () => {
    showSlide(0); // Show the first slide on load
};
"""

CSS_FILE="""
body, html {
    margin: 0;
    padding: 0;
    height: 100%;
    width: 100%;
    font-family: 'Arial', sans-serif; /* Ensuring the whole page uses a sans-serif font */
}

.presentation {
    display: flex;
    flex-direction: column; /* Adjusted to column to ensure slides fill the screen */
    align-items: center;
    justify-content: center;
    height: 100vh;
    width: 100vw; /* Ensures full viewport width */
    color: white;
    overflow: hidden;
}

.slide {
    width: 100%; /* Ensures slide fills the width */
    height: 100vh; /* Ensures slide fills the viewport height */
    display: none; /* Start with slides not displayed */
    align-items: center;
    justify-content: center;
    text-align: center;
    position: relative; /* Needed for absolute positioning of child elements */
}

.slide img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover; /* Ensures image covers slide without losing aspect ratio */
    z-index: -1; /* Image goes behind text */
}

.slide p {
    z-index: 2; /* Ensure text appears above the background image */
    font-size: 4em; /* Larger text size */
    color: white;
    padding: 20px;
    background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent background for readability */
    border-radius: 10px; /* Rounded corners for text background */
}

.active {
    display: flex; /* Active slide is displayed */
    animation: fadeIn 1s; /* Fade-in animation for transitions */
}

@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

"""

PROMPT="""
Generate a funny and zany presentation title and 20 slides about {description}.
Please use HTML tags to format bold and italic text if needed. DO NOT USE MARKDOWN.
The first line should be a catchy title for the presentation. 
Then follow with 18 slide topics that are funny and zany. Each should be 5-15 words ending in a newline.
Finally conclude with a funny or zany closing slide.
Try to make it a coherent funny weird lecture with beginning, middle and end.
Do not begin any line with a bullet point, any numbering, quotation marks, or any other text. Each line will be displayed verbatim. 
Thank you!
"""

IMG_PROMPT="""
Please create a photo representing the following topic: {description}.  
This will be used as background, so it should be a clear, photorealistic image with a dark background.
Do not include any text, it will be added later. Just include the image. 
Make it look like a high-grade professional stock photo with a dark background, vibrant colors, and high-quality artistic bold elements.
Make it simple, professional, and visually appealing.
DO NOT INCLUDE ANY TEXT, NUMBERS, OR LETTERS.
Thank you!
"""

def clean_chatgpt_response(text):
    # Remove Markdown elements like ** (bold)
    text = re.sub(r"\*\*", "", text)
    
    # Remove "Slide: <number>" or "Slide <number>" patterns anywhere in the line
    # It may either have a colon or not
    text = re.sub(r"Slide: \d+", "", text)
    text = re.sub(r"Slide[:\s]*\d+", "", text)
    text = re.sub(r"Slide\s*[:\s]*\d+", "", text)

    
    # Remove initial numbers like "1:"
    text = re.sub(r"^\d+:\s*", "", text, flags=re.MULTILINE)
    
    # Remove initial hyphens "-" or asterisks "*"
    text = re.sub(r"^[*-]\s*", "", text, flags=re.MULTILINE)

    # Remove "<br>" tags
    text = re.sub(r"<br>", "", text, flags=re.MULTILINE)

    # Remove quotes
    text = re.sub(r"\"", "", text, flags=re.MULTILINE)

    # Remove leftover colon or tags (often there)
    text = re.sub(r"^:", "", text, flags=re.MULTILINE)
    text = re.sub(r"<b>: </b>", "", text, flags=re.MULTILINE)
    text = re.sub(r"<b>:</b>", "", text, flags=re.MULTILINE)
    text = re.sub(r"^<b>:", "<b>", text, flags=re.MULTILINE)
    text = re.sub(r"<b> </b>", "", text, flags=re.MULTILINE)
    text = re.sub(r"<b></b>", "", text, flags=re.MULTILINE)

    return text.strip()

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_data(self):
        return ''.join(self.text)

def strip_html(html):
    stripper = MLStripper()
    stripper.feed(html)
    return stripper.get_data()


def generate_presentation_content(description):
    print ("About to generate content")
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You are a creative assistant."},
            {"role": "user", "content": PROMPT.format(description=description)}
        ]
    )
    print ("Done generating content")
    print(response)
    if response and len(response.choices) > 0:
        content = response.choices[0].message.content.strip().split('\n')
        #title = content[0]
        bullet_points = content[0:]
        print("content", content)
        return {"bullet_points": bullet_points}
    else:
        print('choices' in response)
        print(response['choices'])
        raise Exception("Failed to generate presentation content")


def generate_image_for_bullet_point(bullet_point):
    global n_image
    try:
        # Generate an image using DALL-E
        print("Generating image for:", bullet_point)
        response = client.images.generate(prompt=IMG_PROMPT.format(description=strip_html(bullet_point)),
        n=1,
        size="1024x1024")
        
        # Assuming the response includes an image URL or binary data
        # This example will treat it as if a URL is returned
        image_url = response.data[0].url
        print("Retrieved image URL:", image_url)
        # Download the image
        image_response = requests.get(image_url)
        print("Downloaded image response")
        image = Image.open(BytesIO(image_response.content))
        print("Downloaded image")
        # Save the image locally as JPEG
        image_path = f"images/image_{n_image}.jpg"
        print("Saving image to:", image_path)
        image = image.convert("RGB")  # Convert to RGB if not already in this mode
        image.save("presentation/"+image_path, "JPEG")
        print("Saved image to:", image_path)
        n_image+=1
        return image_path
        
    except Exception as e:
        print(f"An error occurred: {e}")
        # Return a placeholder or error image path in case of failure
        return "path_to_error_image.jpg"

def create_slide_html(image_path, text):
    return f'''
        <div class="slide">
            <img src="{image_path}" alt="">
            <p>{text}</p>
        </div>
    '''

def create_presentation_html(slides):
    slides_html = "\n".join(slides)
    return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>PowerPoint Karaoke</title>
            <link rel="stylesheet" type="text/css" href="style.css">
        </head>
        <body>
            <div id="presentation">
                {slides_html}
            </div>
            <script src="script.js"></script>
        </body>
        </html>
    '''


def generate_topic():
    parts_a = [
        "A Brief History of", "The Secret Life of", "The Unbelievable World of",
        "Exploring the Mystery of", "The Hidden Dangers of", "Why You Should Fear",
        "The Untold Story of", "The Rise and Fall of", "How to Cook", "The Art of",
        "Surviving", "The Economics of", "The Philosophy of", "The Science Behind",
        "Dancing with", "Singing with", "The Global Impact of", "The Future of",
        "Befriending", "Avoiding"
    ]
    
    parts_b = [
        "Walruses", "Bananas", "Aliens", "Garden Gnomes", "Dust Bunnies", "Robotic Vacuum Cleaners",
        "Left Socks", "Tea Leaves", "Quantum Mechanics", "Pirate Ghosts", "Invisible Cats",
        "Chocolate Fountains", "Time Travelers", "Underwater Basket Weaving", "Lawn Gnomes",
        "Moon Cheese", "Sock Puppets", "The Internet", "Reality TV Stars", "Haunted Houses"
    ]
    
    parts_c = [
        "in Outer Space", "in Your Backyard", "in Virtual Reality", "during the Renaissance",
        "at the End of the World", "in France", "in Ancient Egypt", "in the Digital Age",
        "without Leaving Your House", "on Mars", "in the Deep Sea", "in the Future",
        "in a Parallel Universe", "in Your Dreams", "in the Middle Ages", "in a Dystopian Future",
        "in the Wild West", "in High School", "on a Desert Island", "at the North Pole"
    ]
    
    # Randomly select one element from each list
    part_a = random.choice(parts_a)
    part_b = random.choice(parts_b)
    part_c = random.choice(parts_c)
    
    # Combine the parts into a single string
    topic = f"{part_a} {part_b} {part_c}"
    
    return topic

def main(description):
    os.makedirs("presentation", exist_ok=True)
    os.makedirs("presentation/images", exist_ok=True)
    content = generate_presentation_content(description)
    
    slides = [] #create_slide_html("", content["title"])]  # Title slide
    
    for bullet_point in content["bullet_points"]:
        if bullet_point.strip() == "":
            continue
        print("Bullet point is", bullet_point)
        bullet_point = clean_chatgpt_response(bullet_point)
        print("Cleaned bullet point is", bullet_point)
        image_path = generate_image_for_bullet_point(bullet_point)
        slide_html = create_slide_html(image_path, bullet_point)
        slides.append(slide_html)
    
    presentation_html = create_presentation_html(slides)
    
    with open("presentation/index.html", "w") as file:
        file.write(presentation_html)
    with open("presentation/script.js", "w") as file:
        file.write(JS_FILE)
    with open("presentation/style.css", "w") as file:
        file.write(CSS_FILE)

def generate_topic_prompt():
    topic = generate_topic()
    print("Randomly generated topic:", topic)
    i=input("Press y to continue, or other key to generate a new topic: ")
    if i=="y":
        return topic
    else:
        return generate_topic_prompt()

if __name__ == "__main__":
    description = input("Enter a one-line description for the presentation, or return for random: ")
    if description.strip() == "":
        description = generate_topic_prompt()
    main(description)
