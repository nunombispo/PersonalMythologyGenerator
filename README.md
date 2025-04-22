# Hero's Journey Story Generator

A Python application that generates personalized mythological stories based on the Hero's Journey structure, incorporating elements from the Thompson Motif Index.

## Features

- Personalized story generation based on user input
- Integration with Ollama API for AI-powered story generation
- Text-to-speech narration of the generated story
- Export to styled Markdown format
- Random motif selection from the Thompson Motif Index

## Prerequisites

- Python 3.8 or higher
- Ollama installed and running locally
- Required Python packages (install using `pip install -r requirements.txt`)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/PersonalMythologyGenerator.git
cd PersonalMythologyGenerator
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure Ollama is installed and running on your system.

## Usage

1. Run the script:

```bash
python hero_journey_generator.py
```

2. Follow the prompts to:
   - Enter your name (or let it generate a random one)
   - Enter your birthdate
   - Wait for the story generation
   - Listen to the narrated story
   - Find your generated story in `myth_story.md`

## Project Structure

- `hero_journey_generator.py`: Main script containing the story generation logic
- `tmi.json`: Thompson Motif Index data
- `requirements.txt`: Python package dependencies
- `myth_story.md`: Generated story output file

## How It Works

1. **User Input**: Collects name and birthdate
2. **Motif Selection**: Randomly selects 3 motifs from the Thompson Motif Index
3. **Story Generation**: Uses Ollama API to generate each part of the Hero's Journey
4. **Narration**: Converts the story to speech using pyttsx3
5. **Export**: Saves the story in a styled Markdown format

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
