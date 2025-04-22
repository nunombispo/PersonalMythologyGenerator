"""
Personal Mythology Generator - Hero's Journey Story Generator

This script generates personalized mythological stories based on the Hero's Journey structure,
incorporating elements from the Thompson Motif Index. It uses the Ollama API for story generation
and includes text-to-speech narration capabilities.

Features:
- Personalized story generation based on user input
- Integration with Ollama API for AI-powered story generation
- Text-to-speech narration of the generated story
- Export to styled Markdown format
- Random motif selection from the Thompson Motif Index
"""

import json
import random
import pyttsx3
from datetime import datetime
from faker import Faker
import os
from ollama import Client
import sys
from tqdm import tqdm
import time

class HeroJourneyGenerator:
    """
    A class to generate personalized Hero's Journey stories using AI.
    
    This class handles the entire story generation process, from collecting user input
    to generating the story, saving it to a markdown file, and narrating it using
    text-to-speech.
    """
    
    def __init__(self):
        """
        Initialize the HeroJourneyGenerator with necessary components.
        
        Sets up:
        - Faker for random name generation
        - Text-to-speech engine with configured properties
        - Ollama client for AI story generation
        """
        self.faker = Faker()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        self.ollama_client = Client()
        self.model_name = 'llama3.2:1b'
        
    def check_model(self):
        """
        Check if the required Ollama model is available and pull it if needed.
        
        This method:
        1. Checks if the model exists in the local Ollama installation
        2. Pulls the model if it's not found
        3. Shows download progress with a progress bar
        4. Handles any errors during the process
        """
        try:
            # Try to list models to check if Mistral is available
            models = self.ollama_client.list()
            model_names = [model.get('name', '') for model in models.get('models', [])]
            
            if self.model_name not in model_names:
                print(f"\nModel '{self.model_name}' not found. Pulling it now...")
                print("This may take a few minutes depending on your internet connection.")
                
                # Create a progress bar
                with tqdm(total=0, desc="Downloading model", unit="B", unit_scale=True, unit_divisor=1024) as pbar:
                    # Start the pull operation
                    pull_operation = self.ollama_client.pull(self.model_name, stream=True)
                    
                    # Update progress bar based on the stream
                    for chunk in pull_operation:
                        if hasattr(chunk, 'status'):
                            # Update progress if we have completed and total values
                            if hasattr(chunk, 'completed') and hasattr(chunk, 'total'):
                                try:
                                    completed = float(chunk.completed)
                                    total = float(chunk.total)
                                    if total > 0:
                                        # Update total if it changes
                                        if pbar.total != total:
                                            pbar.total = total
                                        
                                        # Update completed bytes
                                        pbar.update(completed - pbar.n)
                                except (ValueError, TypeError):
                                    pass
                            
                            # Handle completion
                            if chunk.status == 'success':
                                pbar.update(pbar.total - pbar.n)
                                break
                            
                            # Add a small delay to make the progress visible
                            time.sleep(0.1)
                
                print(f"\nModel '{self.model_name}' has been pulled successfully!")
        except Exception as e:
            print(f"\nError checking/pulling model: {e}")
            print("\nPlease make sure:")
            print("1. Ollama is installed and running")
            print("2. You have an internet connection")
            print("3. You have enough disk space")
            print("\nYou can manually pull the model by running:")
            print(f"ollama pull {self.model_name}")
            sys.exit(1)
        
    def get_user_input(self):
        """
        Collect user information for story customization.
        
        Returns:
            tuple: (name, birthdate) where:
                - name is either user input or a randomly generated name
                - birthdate is a string in YYYY-MM-DD format
        """
        print("\n=== Welcome to the Hero's Journey Story Generator ===")
        
        # Get user input
        name = input("\nEnter your name (or press Enter for a random name): ").strip()
        if not name:
            name = self.faker.name()
            print(f"Generated name: {name}")
            
        # Get birthdate from user
        while True:
            birthdate = input("\nEnter your birthdate (YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(birthdate, '%Y-%m-%d')
                break
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                
        return name, birthdate
    
    def load_motifs(self):
        """
        Load and select random motifs from the Thompson Motif Index.
        
        Returns:
            list: A list of randomly selected motif dictionaries from tmi.json
        """
        try:
            # Load motifs from tmi.json
            with open('tmi.json', 'r', encoding='utf-8') as f:
                motifs = json.load(f)
            # Select 3 random motifs
            selected_motifs = random.sample(motifs, 3)
            return selected_motifs
        except FileNotFoundError:
            print("Error: tmi.json file not found!")
            return []
    
    def generate_story_part(self, prompt):
        """
        Generate a story part using Ollama API.
        
        Args:
            prompt (str): The prompt to generate the story part
            
        Returns:
            str: The generated story part text
        """
        try:
            system_prompt = """You are a master storyteller specializing in mythological narratives. 
                Your task is to create engaging, vivid, and meaningful stories that follow the Hero's Journey structure.
                Focus on:
                - Rich, descriptive language that paints vivid imagery
                - Emotional depth and character development
                - Mythological and symbolic elements
                - A balance of action and reflection
                - Maintaining a consistent narrative voice
                - Incorporating the provided motifs naturally into the story

                Write in a style that is both accessible and profound, suitable for a modern audience while maintaining the timeless quality of mythology.
            """
            # Generate story part using Ollama API
            response = self.ollama_client.chat(model=self.model_name, 
                # Set messages
                messages=[
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }],
                # Set temperature and number of threads
                options={
                    "temperature": 0.7,
                    "num_thread": os.cpu_count() * 0.5
                })
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Error generating story part: {e}")
            return "Error generating this part of the story."
    
    def generate_hero_journey(self, name, birthdate, motifs):
        """
        Generate the complete Hero's Journey story.
        
        Args:
            name (str): The hero's name
            birthdate (str): The hero's birthdate in YYYY-MM-DD format
            motifs (list): List of motif dictionaries to incorporate
            
        Returns:
            list: List of tuples containing (title, content) for each part of the journey
        """
        story_parts = []
        
        # Extract motif descriptions for the prompts
        motif_descriptions = [motif['description'] for motif in motifs]
        
        # Calculate age for story context
        birth_date = datetime.strptime(birthdate, '%Y-%m-%d')
        current_date = datetime.now()
        age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
        
        # Define prompts for each part of the journey
        prompts = {
            "Call to Adventure": f"Create a compelling call to adventure for {name}, who is {age} years old. Born on {birthdate}, their journey begins at a pivotal moment in their life. Incorporate these motifs: {', '.join(motif_descriptions)}. Make it personal and engaging, reflecting their age and life stage.",
            "Supernatural Aid": f"Describe the supernatural aid that comes to {age}-year-old {name}'s assistance. Born on {birthdate}, they receive guidance that resonates with their life experience. Using these motifs: {', '.join(motif_descriptions)}, make it mysterious and powerful, tailored to their age and background.",
            "Road of Trials": f"Narrate the challenging trials that {name}, born on {birthdate}, must face at the age of {age}. These challenges should reflect their life stage and personal growth. Incorporating these motifs: {', '.join(motif_descriptions)}, make it dramatic and transformative.",
            "Apotheosis": f"Describe {name}'s moment of apotheosis or transformation at the age of {age}. Born on {birthdate}, this moment should reflect their accumulated life experience. Using these motifs: {', '.join(motif_descriptions)}, make it profound and meaningful to their personal journey.",
            "The Ultimate Boon": f"Detail the ultimate boon or reward that {age}-year-old {name} obtains. Born on {birthdate}, this reward should be significant to their life stage and personal development. Incorporating these motifs: {', '.join(motif_descriptions)}, make it valuable and meaningful to their journey.",
            "Return": f"Tell the story of {name}'s return and how they use their newfound wisdom at the age of {age}. Born on {birthdate}, their return should reflect their growth and the impact of their journey. Using these motifs: {', '.join(motif_descriptions)}, make it satisfying and complete."
        }
        
        # Generate each part of the journey
        for title, prompt in prompts.items():
            print(f"\nGenerating {title}...")
            story_part = self.generate_story_part(prompt)
            story_parts.append((title, story_part))
            
        return story_parts
    
    def save_to_markdown(self, name, birthdate, motifs, story_parts):
        """
        Save the story to a markdown file.
        
        Args:
            name (str): The hero's name
            birthdate (str): The hero's birthdate
            motifs (list): List of motif dictionaries used in the story
            story_parts (list): List of tuples containing (title, content) for each part
        """
        with open('myth_story.md', 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# {name}'s Hero's Journey\n\n")
            f.write(f"**Birthdate:** {birthdate}\n\n")
            f.write("## Selected Motifs\n")
            for motif in motifs:
                f.write(f"- **{motif['motif']}**: {motif['description']}\n")
                if motif['locations']:
                    f.write(f"  - Locations: {', '.join(motif['locations'])}\n")
                if motif['lemmas']:
                    f.write(f"  - Related terms: {', '.join(motif['lemmas'])}\n")
            f.write("\n## The Hero's Journey\n\n")
            
            # Write story parts
            for title, content in story_parts:
                f.write(f"### {title}\n\n")
                f.write(f"{content}\n\n")
    
    def narrate_story(self, story_parts):
        """
        Narrate the story using text-to-speech.
        
        Args:
            story_parts (list): List of tuples containing (title, content) for each part
        """
        print("\nNarrating the story...")
        for title, content in story_parts:
            # Narrate each part
            self.engine.say(f"{title}. {content}")
            # Wait for the current part to finish
            self.engine.runAndWait()
    
    def run(self):
        """
        Main execution flow of the story generator.
        
        This method:
        1. Checks for the required model
        2. Gets user input
        3. Loads motifs
        4. Generates the story
        5. Saves it to markdown
        6. Narrates it using text-to-speech
        """
        # Check for model availability first
        self.check_model()
        
        # Get user input    
        name, birthdate = self.get_user_input()
        
        # Load motifs
        motifs = self.load_motifs()
        if not motifs:
            print("Unable to proceed without motifs. Please ensure tmi.json is present.")
            return
        
        # Generate the story
        print("\nGenerating your personalized Hero's Journey...")
        story_parts = self.generate_hero_journey(name, birthdate, motifs)
        
        # Save to markdown
        self.save_to_markdown(name, birthdate, motifs, story_parts)
        print("\nStory has been saved to 'myth_story.md'")
        
        # Narrate the story
        self.narrate_story(story_parts)

if __name__ == "__main__":
    generator = HeroJourneyGenerator()
    generator.run() 