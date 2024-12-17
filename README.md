# AI Powered Communication Improvement Platform

# AI models used and their purpose:
- Grammar model: This was made using gramformer to score the user's grammar while communicating. Also, the model gives the user, the corrected sentences so that the user can learn from his mistakes.
- Text to speech: This is the foundation model, which uses whisper, in the pipeline. The audio file received from the frontend is given to this TTS model for conversion into text and then this text is given to the other models for further processing.
- Speech to text: This model converts the output of the text to speech model back to speech. It uses SpeechBrain. This STT output audio and the original audio are then compared to find the pronunciation score of the user.
- Fluency model: This model uses Vosk. This model is used to judge the flunecy of the user and assigns a score to the user.
- Facial emotion detection model: This model uses OpenCV and MediaPipe to detect the facial emotion of the user in the video file received by the frontend. The model classifies the emotion from a set of 9 emotion labels like happy, angry, depressed etc.
