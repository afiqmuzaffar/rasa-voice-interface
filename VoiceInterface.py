# Rasa interface with TTS and STT support

# Dependencies
import requests
import speech_recognition as sr
import random
import string
from os import path
from gtts import gTTS
from audioplayer import AudioPlayer

print("\nRASA voice interface\n")
  
# Begin general setup
print("General setup =============")

# Get sender_id (aka name)
if path.exists("rememberme.txt"):
    f = open("rememberme.txt", "r") 
    id = f.read()
    f.close()
else: 
    name = input("Please enter your name: ")
    letters = string.ascii_letters
    id = name + "-" + ''.join(random.choice(letters) for i in range(15))
    f = open("rememberme.txt", "w")
    f.write(id)
    f.close()

print("Sender ID: " + id)

# Get language
language_type = int(input("Please enter language (1 = english, 2 = indonesian): "))
if language_type == 1:
    language_code_stt = "en-US"
    language_code_tts = "en"
elif language_type == 2:
    language_code_stt = "id-ID"
    language_code_tts = "id"
else:
    print("Please select a valid language!")
    exit()

# Display microphone list and get selected microphone
mic_list = sr.Microphone.list_microphone_names()
num = 0
print("Mic list: ")
for x in mic_list:
    print("[{0}] {1}".format(str(num), x))
    num += 1

selected_mic = int(input("Select a microphone to use in the voice recognition: "))

# End general setup

# Start conversation
print("\nConversation started, type 'quit' to end conversation\n")

loop = True

# Loop conversation
while loop == True:
    # Get message input method (text/microphone)
    message_method = int(input("Please enter message input method (1 = text, 2 = microphone): "))

    if message_method == 1: # Text input
        message = input("Please enter message: ")
    elif message_method == 2: # Microphone input

        # Get microphone and setup recognizer variable
        r = sr.Recognizer()
        mic = sr.Microphone()

        print("You make speak through the microphone now")
        # Listen to user input
        mic = sr.Microphone(device_index=selected_mic)
        with mic as source:
            audio = r.listen(source)

        try:
            message = r.recognize_google(audio, language=language_code_stt)
            print("Detected voice input: " + message)
        except sr.UnknownValueError:
            print("Voice recognition cannot understand what you speak, please try again")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
    else:
        print("Please select a valid message input method!")
        exit()

    if message == "quit":
        loop = False
        print("User exitted the conversation.")
        break

    # Send POST request to RASA webhook endpoint
    response = requests.post("http://localhost:5005/webhooks/rest/webhook", json={"sender": id, "message": message})
    response_json = response.json()

    for i in range(len(response_json)):
        for g in response_json[i]:
            if response_json[i][g] != id:   
                message = response_json[i][g]
                print("Message: {0}".format(message))

                obj = gTTS(text=message, lang=language_code_tts, slow=False)
                obj.save("tts.mp3")
                AudioPlayer("tts.mp3").play(block=True)

    print("\n")
    # x = response_json[0]
    # print(x["text"])
    # json_load = json.loads(response_json)
    # for i in json_load:
    #     if json_load[i]["text"] is not None:
    #         print("Message: {0}".format(json_load[i]["text"]))
    #     if json_load[i]["image"] is not None:
    #         print("Image: {0}".format(json_load[i]["image"]))