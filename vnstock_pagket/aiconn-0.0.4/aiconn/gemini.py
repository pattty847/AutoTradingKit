import os
import google.generativeai as genai
# import pathlib
import importlib.metadata
import PIL.Image
import ipywidgets as widgets
from IPython.display import display, Image, Markdown #, HTML
try:
    from google.colab import userdata, files
except ImportError:
    pass
from tqdm import tqdm
import time
from typing import Optional
from .utils import *

IMAGE_MEME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/heic', 'image/heif']
AUDIO_MEME_TYPES = ['audio/wav', 'audio/mp3', 'audio/aiff', 'audio/aac', 'audio/ogg', 'audio/flac']
TEXT_MEME_TYPES = ["text/plain", "text/html", "text/css", "text/javascript", "application/x-javascript", "text/x-typescript", "application/x-typescript", "text/csv", "text/markdown", "text/x-python", "application/x-python-code", "application/json", "text/xml", "application/rtf", "text/rtf"]
ALL_MEME_TYPES = IMAGE_MEME_TYPES + AUDIO_MEME_TYPES + TEXT_MEME_TYPES

class GeminiAI:
    """
    A class to interface with the Gemini AI model, allowing configuration, image handling, and interaction 
    within Google Colab environments.

    Attributes:
        api_key (str): API key for Gemini AI.
        gemini_model (str): The model name for Gemini AI.
        is_colab (bool): Flag indicating if the environment is Google Colab.
        model (GenerativeModel): Configured Gemini AI generative model.
        chat_session (ChatSession): Chat session with the model.
        response (Response): The response object from the model.
    """

    def __init__(self, api_key: str, gemini_model: str = 'gemini-1.5-flash-latest'):
        """
        Initialize GeminiAI with an API key and model name.

        Args:
            api_key (str): API key for Gemini AI.
            gemini_model (str): The model name for Gemini AI. Defaults to 'gemini-1.5-flash-latest'.
        """
        required_packages = ['google-generativeai']
        # check if the package google-generativeai is installed
        for pkg in required_packages:
            try:
                importlib.metadata.version(pkg)
            except ImportError:
                raise ImportError(f"Please install the package '{pkg}' to use this class.")
            
        self.api_key = api_key
        self.gemini_model = gemini_model
        genai.configure(api_key=api_key)
        self.is_colab = self._colab_verify()
        self.config()

    def config(self, temp: Optional[int] = 1, top_p: Optional[float] = 0.95, top_k: Optional[int] = 64,
               max_output_tokens: Optional[int] = 8192, response_mime_type: str = "text/plain",
               stream: bool = True, silent: bool = True):
        """
        Configure the generative model settings.

        Args:
            temp (Optional[int]): Temperature setting for model generation. Defaults to 1.
            top_p (Optional[float]): Top-p sampling setting. Defaults to 0.95.
            top_k (Optional[int]): Top-k sampling setting. Defaults to 64.
            max_output_tokens (Optional[int]): Maximum output tokens. Defaults to 8192.
            response_mime_type (str): MIME type for the response. Defaults to "text/plain".
            stream (bool): Flag to stream responses. Defaults to True.
            silent (bool): Flag to suppress session return. Defaults to True.

        Returns:
            ChatSession: Chat session if not silent.
        """
        generation_config = {
            "temperature": temp,
            "top_p": top_p,
            "top_k": top_k,
            "max_output_tokens": max_output_tokens,
            "response_mime_type": response_mime_type,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]

        self.model = genai.GenerativeModel(
            model_name=self.gemini_model,
            safety_settings=safety_settings,
            generation_config=generation_config,
        )
        self.chat_session = self.model.start_chat(history=[])
        if not silent:
            return self.chat_session

    def _colab_verify(self) -> bool:
        """
        Verify if the environment is Google Colab.

        Returns:
            bool: True if running in Google Colab, else False.
        """
        if 'COLAB_JUPYTER_IP' in os.environ:
            print("Running on Colab")
            return True
        else:
            print("Not running on Colab")
            return False

    def _dir_cleanup(self):
        """
        Cleanup files in the Google Colab environment, excluding 'sample_data'.
        """
        if self.is_colab:
            path = '/content/'
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if os.path.isfile(file_path) and filename != "sample_data":
                    os.remove(file_path)
                    print(f'Deleted: {file_path}')

    def open_image(self, image_path: str, preview_size: int = 300, preview=False):
        """
        Open and display an image.

        Args:
            image_path (str): Path to the image file.
            preview_size (int): Size to display the preview. Defaults to 300.

        Returns:
            PIL.Image.Image: The opened image object.
        """
        img = PIL.Image.open(image_path)
        if preview:
            display(Image(image_path, width=preview_size))
        return img

    def upload(self) -> str:
        """
        Upload a file in Google Colab environment.

        Returns:
            str: The path to the uploaded file.

        Raises:
            ValueError: If not running in Google Colab environment.
        """
        if self.is_colab:
            uploaded_file = files.upload()
            if uploaded_file:
                filename = list(uploaded_file.keys())[0]
                current_directory = os.getcwd()
                file_path = os.path.join(current_directory, filename)
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    self.open_image(file_path)
                return file_path
        else:
            raise ValueError("This function is only applicable in Google Colab environment.")

    def history(self):
        """
        Display the chat history.
        """
        for message in self.chat_session.history:
            display(Markdown(f'**{message.role}**: {message.parts[0].text}'))

    def _stream(self, chunk_size: int = 80):
        """
        Stream the response in chunks.

        Args:
            chunk_size (int): The size of each chunk. Defaults to 80.
        """
        for chunk in self.response:
            display(Markdown(chunk.text))
            display(Markdown("_" * chunk_size))

    def _token_counts(self):
        """
        Count tokens in the entire chat history.
        """
        token_count = self.model.count_tokens(self.chat_session.history)
        display(Markdown(f"Total tokens: {token_count}"))

    def upload_to_gemini(self, path, mime_type=None):
        """Uploads the given file to Gemini.

        See https://ai.google.dev/gemini-api/docs/prompting_with_media
        """
        self.file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{self.file.display_name}' as: {self.file.uri}")
        return self.file
    
    def wait_for_files_active(self, files):
        """Waits for the given files to be active.

        Some files uploaded to the Gemini API need to be processed before they can be
        used as prompt inputs. The status can be seen by querying the file's "state"
        field.

        This implementation uses a simple blocking polling loop. Production code
        should probably employ a more sophisticated approach.
        """
        print("Waiting for file processing...")
        for name in (file.name for file in files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(10)
                file = genai.get_file(name)
            if file.state.name != "ACTIVE":
                raise Exception(f"File {file.name} failed to process")
        print("...all files ready")

    def start_chat(self, instruction: [str], file_path: Optional[str] = None, meme_type: Optional[str]="text/plain"):
        if file_path:
            files = [
                    self.upload_to_gemini(file_path, mime_type=meme_type),
                    ]

            # Some files have a processing delay. Wait for them to be ready.
            self.wait_for_files_active(files)

            instruction = {"role":"user",
                        "parts":[instruction,
                                    files[0]
                                    ]
                        }
            self.chat_session = self.model.start_chat(history=[instruction])
        else:
            instruction = {"role":"user",
                        "parts":[instruction]
                        }
            self.chat_session = self.model.start_chat(history=[instruction])

    def send_message(self, prompt: str, stream: bool = False):
        """
        Send a prompt to the AI model and receive a response.

        Args:
            prompt (str): The prompt to send to the model.
            stream (bool): Flag to stream the response. Defaults to True.

        Returns:
            None
        """
        try:
            tokens = self.model.count_tokens(prompt)
            display(Markdown(f"Tokens in prompt: {tokens}"))
        except Exception as e:
            print(f"Error counting tokens: {e}")

        self.response = self.chat_session.send_message(prompt)
        if stream:
            self._stream()
        else:
            display(Markdown(self.response.text))

    def generate(self, prompt: str, stream: bool = False, chunk_size: int = 80):
        """
        Generate content from a prompt.

        Args:
            prompt (str): The prompt to generate content from.
            stream (bool): Flag to stream the response. Defaults to True.
            chunk_size (int): The size of each chunk. Defaults to 80.

        Returns:
            None
        """
        try:
            tokens = self.model.count_tokens(prompt)
            display(Markdown(f"Tokens in prompt: {tokens}"))
        except Exception as e:
            print(f"Error counting tokens: {e}")

        if stream:
            self.response = self.model.generate_content(prompt, stream=stream)
            self._stream(chunk_size)
        else:
            self.send_message(prompt, stream=False)

    def candidates(self):
        """
        Display all response candidates.

        Returns:
            None
        """
        display(Markdown("Response Candidates:"))
        for candidate in self.response.candidates:
            display(Markdown(candidate.content.parts[0].text))

    # def feedback(self):
    #     """
    #     Display feedback on the prompt if the result was not returned.

    #     Returns:
    #         None
    #     """
    #     display(Markdown("Prompt Feedback:"))
    #     for feedback in self.response.prompt_feedback:
    #         display(Markdown(feedback.text))
