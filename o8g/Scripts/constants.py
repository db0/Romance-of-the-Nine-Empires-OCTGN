#---------------------------------------------------------------------------
# Constants
#---------------------------------------------------------------------------
import re

phases = [
    '{} is currently in the Pre-game Setup Phase'.format(me),
    "\n=== It is Spring ===\n",
    "\n=== It is Summer ===\n",
    "\n=== It is Autumn ===\n",
    "\n=== It is Winter ===\n"]

### Highlight Colours ###
BattleColor = "#ff0000"
FateColor = "#000000"
DummyColor = "#005566"


### Deprecated Markers ###

mdict = { # A dictionary which holds all the hard coded markers (in the markers file)
    "+2/+2"           : ("+2/+2"                              "9228e87d-b0ce-4e42-8fc4-45dc2dcaf430"),
    "Undead"          : ("Undead"                             "359a9449-fd99-47e7-a9d4-cdfe792194fb"),
    "-1 Strength"     : ("-1 Strength"                        "3f665156-9b9c-445f-87b3-5b2a0b3d1643"),
    "-1 Will"         : ("-1 Will"                            "9e9e1478-90fd-401b-b12f-f24f9fe53b3a"),
    "Food"            : ("Food"                               "6bc7c60b-4b69-4b19-953d-6c377f8ce41e"),
    "Used Ability"    : ("Used Ability"                       "7209af6b-7e96-4775-874a-1eec4fa25859"),
    "Ordained"        : ("Ordained"                           "0b2676b8-0a66-4e23-b1c7-e29fe109cd66")
}

### Misc ###
CardWidth = 63
CardHeight = 88

loud = 'loud' # So that I don't have to use the quotes all the time in my function calls
silent = 'silent' # Same as above
shootout = 'shootout' # Same as above
Xaxis = 'x'  # Same as above
Yaxis = 'y'	 # Same as above

