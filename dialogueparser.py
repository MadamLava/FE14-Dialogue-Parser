from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import font
import pyperclip
import textwrap
import os

root = Tk()

root.title("FE14 Dialogue Parser")
#root.iconbitmap("Quill.ico")

root.geometry("720x640")
normal_font = font.Font(family="Segue UI", size=8, weight=font.NORMAL)

# Icon bs
basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "Madam.FE14DialogueParser.Parser.1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

root.iconbitmap(os.path.join(basedir, "Quill.ico"))

text = StringVar()
result_text = StringVar()

def clear():
    text_entry.delete("0.0", "end")

# Evil ass music dictionary
MusicDictionary = {
    "Homesick (Light)": "STRM_EVT_AMB_A1",
    "Paradise (Light)": "STRM_EVT_AMB_A2",
    "Homesick (Dark)": "STRM_EVT_AMB_B1",
    "Paradise (Dark)": "STRM_EVT_AMB_B2",
    "Oblivescence": "STRM_EVT_AMB_C1",
    "Vacant Cradle": "STRM_EVT_AMB_C2",
    "As All Stars Fall": "STRM_EVT_DISHEARTEN_E1",
    "Prelude to Dispute": "STRM_EVT_STRAIN_E1",
    "Prelude to Disaster": "STRM_EVT_STRAIN_E2",
    "Guest of Light": "STRM_EVT_PARTY_A1",
    "Guest of Shade": "STRM_EVT_PARTY_B1",
    "Pale Star": "STRM_EVT_BRAVE_A1",
    "Lingering Clouds": "STRM_EVT_BRAVE_A2",
    "Dim Moonlight": "STRM_EVT_BRAVE_B1",
    "Raging Dark Winds": "STRM_EVT_BRAVE_B2",
    "Implore the Dawn": "STRM_EVT_SERIOUS_A1",
    "Pray to the Dark": "STRM_EVT_SERIOUS_B1",
    "The Wistful Wilds": "STRM_EVT_SERIOUS_E1",
    "Shine in the Light": "STRM_EVT_DAILY_A1",
    "Dance in the Dark": "STRM_EVT_DAILY_B1",
    "The Path to You": "STRM_EVT_DAILY_E1",
    "Unfamiliar Streets": "STRM_EVT_DAILY_E2",
    "Light on a Window": "STRM_EVT_DAILY_E3",
    "Destiny, Help Us": "STRM_EVT_RESOLVE_E1",
    "How Can That Be?": "STRM_EVT_UNEASY_E1",
    "Advance Confusion": "STRM_EVT_EMERGENCY_E1",
    "The Truth-Teller": "STRM_EVT_WISEMAN_C1",
    "Coming Demise": "STRM_EVT_EVIL_C1",
    "Obsidian Ruler": "STRM_EVT_EVIL_C1",
    "The Dim Abyss": "STRM_EVT_UNCANNY_E1",
    "True Form of Evil": "STRM_EVT_UNCANNY_C1",
    "Spreading Shadow": "STRM_EVT_ENEMY_E1",
    "Flickering Illusion": "STRM_EVT_DIFFERENT_C1",
    "What Can You Do?": "STRM_EVT_GAG_E1",
    "Are You Listening?": "STRM_EVT_GAG_E2",
    "No Cure For...": "STRM_EVT_FOOL_E1",
    "Rejoice in Love": "STRM_EVT_LOVE_E1",
    "Petals in the Wind": "STRM_EVT_KINDLY_E1",
    "Reminiscence": "STRM_EVT_KINDLY_E2",
    "The Water Maiden": "STRM_EVT_AQUA_C1",
    "Premonition": "STRM_EVT_AQUA_C2",
    "Return to Elegance": "STRM_EVT_AQUA_C3",
    "Ember of Hope": "STRM_EVT_PEACE_E1",
    "New Power": "STRM_EVT_UNITE_C1",
    "Warmth Is Gone": "STRM_EVT_SAD_E1"
}

# Flags
ConversationType = StringVar(value="Standard")
MusicSelection = StringVar(value = "")
ReplaceCorrin = BooleanVar(value=True)
S_Support = BooleanVar(value=False)

# actual conversion
def convert(*args):
    print("Converting...")
    text = text_entry.get("1.0", "end")

    processedText = ""
    
    # Preprocessing
    # We all HATE google docs
    text = text.replace("’", "'")
    text = text.replace("…", "...")

    text = text.rstrip()
    
    ## Check if the avatar's information is required
    if ReplaceCorrin.get() == True:
        if text.find("username") != -1 or text.find("$G") != -1 or text.find("$Nu") != -1 or text.find("Corrin") != -1:
            processedText += "$HasPermanents\n"
            print("Text contains reference to Corrin")

    ## Get conversationtype
    match ConversationType.get():
        case "Standard" | "Support":
            val = 1
            print("Standard/Support Dialogue")
        case "BattleTalk":
            val = 0
            print("BattleTalk Dialogue")
    processedText += f"$SetConversationType({val})\n"

    # Music override
    if MusicSelection.get() != "" and MusicSelection.get() != "(None)":
        mus = MusicDictionary[MusicSelection.get()]
        processedText += f"$PlayMusic({mus},0)\n"
    
    # State Variables

    SpeakerA = {
        "name" : "",
        "position" : ""
    }

    SpeakerB = {
        "name" : "",
        "position" : ""
    }
    
    previousSpeaker = ""
    lastCommandedPosition = ""
    nextDialogueIsPanicked = False
    emotionInsert = ""
    
    # Load the text into lines and process each
    count = 0
    for line in text.splitlines():
        count += 1

        line = line.rstrip()
        
        # Sanity test
        text = text.rstrip() # Strip the trailing newlines
        if text == "":
            messagebox.showerror("Dialogue Parsing Error", "No dialogue provided!")
            break
        
        # Is this line a control character or dialogue?
        if line[0] == "$":
            commandType = line.split("$")[1].split("(")[0]
            
            match commandType:
                case "Left" | "Right" | "Top" | "Bottom":
                    lastCommandedPosition = commandType
                    print(f"Shifting speaker position to {commandType} on line {count}")

                case "FadeInOut":
                    processedText += f"$ScrollIn\n$SetVolume(40,1000)\n$FadeOut(1000)\n$SetVolume(100,1000)\n$FadeIn(1000)\n\n"
                    print(f"Fading in and out on line {count}")

                case "Emotions":
                    #processedText += line + "\n"
                    emotionInsert = line + "\n"

                    print(f"Adding emotion {line}")

                case "Panicked":
                    nextDialogueIsPanicked = True
                    print(f"Dramatic bubble on line {count}")

                case "SFX":
                    foo = line.split("(")[1].split(")")[0]
                    if foo == "":
                        messagebox.showerror("Dialogue Parsing Error", f"Empty SFX command on line {count}")
                        break
                    processedText += f"$ScrollIn\n$Wait(200)\n$PlaySoundEffect({foo})\n$Wait(800)\n\n"

                case "DeleteSpeaker":
                    processedText += f"$ScrollIn\n$DeleteSpeaker\n$Wait(800)\n\n"
                
                case _: # default
                    messagebox.showerror("Dialogue Parsing Error", f"Invalid control statement on line {count}")
                    break
        
        # Regular dialogue processing    
        else:
            # Verify character name
            if line.find(":") == -1 or line.split(":")[0] == "":
                messagebox.showerror("Dialogue Parsing Error", f"No speaker defined on line {count}")
                break
            
            # Name of character in line
            lineSpeaker = line.split(":")[0]

            if lineSpeaker == "Corrin" and ReplaceCorrin.get() == True:
                lineSpeaker = "username"
            
            # Is speaker already loaded?
            if lineSpeaker == SpeakerA["name"] or lineSpeaker == SpeakerB["name"]:
                # Are they already the one speaking?
                if lineSpeaker == previousSpeaker:
                    processedText += "$Clear\n"
                else:
                    processedText += f"\\n\n$SetSpeaker({lineSpeaker})\n$Synchronize\n"
                    
            # Speaker needs to be loaded
            else:
                # Case for support dialogue
                if ConversationType.get() == "Support":
                    if SpeakerA["name"] == "":
                        SpeakerA["name"] = lineSpeaker
                        SpeakerA["position"] = "left"
                        newPosition = 3
                        
                    else:
                        SpeakerB["name"] = lineSpeaker
                        SpeakerB["position"] = "right"
                        newPosition = 7
                # Manual positioning
                else:
                    if lastCommandedPosition == SpeakerA["position"]:
                        SpeakerA["name"] = lineSpeaker
                        SpeakerA["position"] = lastCommandedPosition
                    elif lastCommandedPosition == SpeakerB["position"]:
                        SpeakerB["name"] = lineSpeaker
                        SpeakerB["position"] = lastCommandedPosition
                    else:
                        if SpeakerA["name"] == "":
                            SpeakerA["name"] = lineSpeaker
                            SpeakerA["position"] = lastCommandedPosition

                        elif SpeakerB["name"] == "":
                            SpeakerB["name"] = lineSpeaker
                            SpeakerB["position"] = lastCommandedPosition

                    match lastCommandedPosition.lower():
                        case "top":
                            newPosition = 6
                        case "bottom":
                            newPosition = 0
                        case "left":
                            newPosition = 3
                        case "right":
                            newPosition = 7
                        case _:
                            messagebox.showerror("Dialogue Parsing Error", f"No position defined for new character at line {count}")
                            break
                        
                
                processedText += f"$LoadAssets({lineSpeaker}, {newPosition})\n$Wait(0)\n"
                processedText += f"$SetSpeaker({lineSpeaker})\n$Synchronize\n"
            previousSpeaker = lineSpeaker
            lastCommandedPosition = ""
                    
            # Obtain what they said
            spokenText = line.split(":")[1].lstrip()

            if ReplaceCorrin.get() == True:
                spokenText = spokenText.replace("Corrin", "$Nu")
            
            if spokenText == "":
                messagebox.showerror("Dialogue Parsing Error", f"Character dialogue empty at line {count}")
                break
            # Perform auto line splitting
            wrapper = textwrap.TextWrapper(width=42)
            wrappedText = wrapper.wrap(text=spokenText)
            
            spokenText = ""

            if nextDialogueIsPanicked:
                panicText = "$Panicked\n"
            else:
                panicText = ""
            
            lineCount = 0
            for line in wrappedText:
                if lineCount < 2:
                    spokenText += emotionInsert + panicText + line
                    if len(wrappedText) >= 2 and lineCount == 0:
                        spokenText += f"\\n"
                else:
                    spokenText += emotionInsert + panicText + "$Pause\n\n$Clear\n" + line

                spokenText += f"\n"
                lineCount += 1
            
            processedText += spokenText
            nextDialogueIsPanicked = False
            emotionInsert = ""
            
            # Finally, close the line with a $Pause
            processedText += "$Pause\n\n"
    
    # S-support postprocessing
    if S_Support.get() == True:
        a = SpeakerA["name"]
        b = SpeakerB["position"]
        processedText += f"$StopMusic(4000)\n$FadeWhite(3000)\n$SetSpeaker({a})\n$DeleteSpeaker\n$SetSpeaker({b})\n$DeleteSpeaker\n$Wait(0)\n$FadeIn(1000)\n$Wait(0)\n"
              
    text_result['state'] = 'normal'
    text_result.delete("0.0", "end")
    text_result.insert("1.0", processedText)
    text_result['state'] = 'disabled'
            
    print(count)
    
def clipboard():
    print("Saving to clipboard")
    pyperclip.copy(text_result.get("1.0", "end"))
    

mainframe = ttk.Frame(root, padding =(3, 3, 12, 12))
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

# input
ttk.Button(mainframe, text="Convert", command=convert).grid(column=0, row=4, sticky=W)
ttk.Button(mainframe, text="Copy to Clipboard", command=clipboard).grid(column=0, row=4, sticky=W, padx=300)

ttk.Button(mainframe, text="Clear", command=clear).grid(column=0, row=4, sticky=W, padx=80)

# ConvoType
ttk.Label(mainframe, text="Conversation Type:").grid(column=0,row=0,sticky=W)

ConvoType = ttk.Combobox(mainframe, textvariable=ConversationType)
ConvoType.grid(column=0, row=0, sticky=W, padx=120)
ConvoType['values'] = ("Standard", "BattleTalk", "Support")
ConvoType.current()

# Music Selection
ttk.Label(mainframe, text="Music Override:").grid(column=0,row=0,sticky=W, padx = 280)
MusicType = ttk.Combobox(mainframe, textvariable=MusicSelection)
MusicType.grid(column=0, row=0, sticky=W, padx=380)

bar = ["(None)"]
for value in MusicDictionary:
    bar.append(value)

bar = tuple(bar)

MusicType['values'] = bar
MusicType.current()

# Toggles
CorrinToggle = ttk.Checkbutton(mainframe, text=f"Replace \'Corrin\'", variable=ReplaceCorrin)
CorrinToggle.grid(column=0, row=1, sticky=W)

S_Toggle = ttk.Checkbutton(mainframe, text="Is S-Support", variable=S_Support)
S_Toggle.grid(column=0, row=2, sticky=W)

# Text fields
text_entry = Text(mainframe, height = 100, width = 40, font=normal_font, wrap=WORD, padx=0)
text_entry.grid(column=0, row=5, sticky=W)

text_result = Text(mainframe, height = 100, width = 40, state=DISABLED, font=normal_font, wrap=NONE)
text_result.grid(column=0, row=5, sticky=W, padx=300)

root.mainloop()