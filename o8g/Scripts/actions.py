    # Python Scripts for the Doomtown CCG definition for OCTGN
    # Copyright (C) 2012  Konstantine Thoukydides

    # This python script is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this script.  If not, see <http://www.gnu.org/licenses/>.

#---------------------------------------------------------------------------
# Global variables
#---------------------------------------------------------------------------

playerside = None # Variable to keep track on which side each player is
playeraxis = None # Variable to keep track on which axis the player is

#---------------------------------------------------------------------------
# Phases
#---------------------------------------------------------------------------
   
def showCurrentPhase(phase = 1): # Just say a nice notification about which phase you're on.
   notify(phases[phase].format(me))
   
def nextPhase(group = table, x = 0, y = 0):  
# Function to take you to the next phase. 
   mute()
   if getGlobalVariable('Battle') == 'True':
      if not confirm("There's still a battle ongoing. Do you want to end it and move to the next phase?"): return
      else: goToAttack()
   phase = int(getGlobalVariable('Phase'))
   if phase == 4: phase = 1 # In case we're on the last phase (Nightfall), go back to the first game phase (Gamblin')
   else: phase += 1 # Otherwise, just move up one phase
   if phase == 1: goToSpring()
   elif phase == 2: goToSummer()
   elif phase == 3: goToAutumn()
   elif phase == 4: goToWinter()

def goToSpring(group = table, x = 0, y = 0): # Go directly to the gamblin' phase
   mute()
   setGlobalVariable('Phase','1')
   showCurrentPhase(1)
   clearBattle() 

def goToSummer(group = table, x = 0, y = 0): # Go directly to the Upkeep phase
   mute()
   setGlobalVariable('Phase','2')
   clearBattle() # For clearing any leftover lowball draw hands.
   showCurrentPhase(2)

def goToAutumn(group = table, x = 0, y = 0): # Go directly to the High Noon phase
   mute()
   setGlobalVariable('Phase','3')
   showCurrentPhase(3)

def goToWinter(group = table, x = 0, y = 0): # Go directly to the Nightfall phase
   mute()
   setGlobalVariable('Phase','4')
   showCurrentPhase(4)   

def goToAttack(group = table, x = 0, y = 0, silent = False): # Start or End a Shootout Phase
   mute()
   if getGlobalVariable('Battle') == 'False': # The shootout phase just shows a nice notification when it starts and does nothing else.
      if not silent: notify("{} is attacking!".format(me))
      setGlobalVariable('Battle','True')
   else: # When the shootout ends however, any card.highlights for attacker and defender are quickly cleared.
      notify("The battle has ended.".format(me))
      clearBattle()

#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def defaultAction(card, x = 0, y = 0):
   mute()
   if card.highlight == FateColor:
      if card.isFaceUp: revealFate(card)
      else: discard(card)
   if getGlobalVariable('Battle') == 'True' and card.highlight != BattleColor and card.Type == 'Hero': joinBattle(card)
   else: bow(card)
   
def revealFate(card):
   mute()
   notify("{} reveals {} for a fate value of {}".format(me,card,card.Fate))
   
   
def setup(group,x=0,y=0):
   mute()
   me.Deck.shuffle() # First let's shuffle our deck now that we have the chance.
   stronghold = None
   castles = []
   motteBailey = None
   for card in me.hand: # For every card in the player's hand... (which should be an outfit and a bunch of dudes usually)
      if card.Type == "Stronghold" : 
         placeCard(card,'SetupHome')
         stronghold = card
      elif card.Type == "Castle" : 
         placeCard(card,'SetupCastle')
         castles.append(card)
      elif card.Name == "Motte and Bailey" : 
         placeCard(card,'SetupM&B')
         motteBailey = card
      else: notify(":::ERROR:: Illegal card found in your hand: {}\n(Only Strongholds, Castles and Motte and Bailey allowed".format(card))
   if not stronghold or not len(castles):  
      information("I said you need castles and stronghold to play this game. Remake your deck!")
      return
   if not motteBailey: 
      motteBailey = table.create("b1402505-7f6e-49b6-9be0-44bd55bdffbb", 0,0, 1, True) # The OK Button
      placeCard(motteBailey,'SetupM&B')
   notify("{} is playing {} with the following castles: {}.".format(me, stronghold, [castle.Name for castle in castles]))
   
def Pass(group, x = 0, y = 0): # Player says pass. A very common action.
   notify('{} Passes.'.format(me))

def Ready(group, x = 0, y = 0): # Player says ready. A very common action.
   notify('{} is Ready!'.format(me))

def clearBattle(remoted = False):
   if not remoted:
      setGlobalVariable('Battle','False')
      for player in getActivePlayers():
         if player != me: remoteCall(player,'clearBattle',[True])
   for card in table:
      if card.controller == me:
         if card.highlight == BattleColor: card.highlight = None
      
def bow(card, x = 0, y = 0, silent = False, forced =  None): # Boot or Unboot a card. I.e. turn it 90 degrees sideways or set it straight.
   mute()
   if card.controller != me: 
      remoteCall(card.controller,'bow',[card,0,0,silent,forced])
      return
   result = 'OK'
   if forced == 'bow':
      if card.orientation == Rot90: 
         if not silent: notify(":> Tried to bow {} but it was already bowed.".format(card))
         result = 'FAIL'
      else: card.orientation = Rot90
   elif forced == 'straighten':
      if card.orientation == Rot0: 
         if not silent: notify(":> Tried to straighten {} but it was already straight.".format(card))
         result = 'FAIL'
      else: card.orientation = Rot0
   else: card.orientation ^= Rot90 # This function rotates the card +90 or -90 degrees depending on where it was.
   if card.orientation == Rot90: # if the card is now at 90 degrees, then announce the card was booted
      if not silent: notify('{} bows {}'.format(me, card))
   else: # if the card is now at 0 degrees (i.e. straight up), then announce the card was unbooted
      if not silent: notify('{} straightens {}'.format(me, card))
   return result

def discard(card, x = 0, y = 0, silent = False): # Discard a card.
   if card.controller != me: 
      remoteCall(card.controller,"discard",[card])
      return
   debugNotify(">>> discard()") #Debug
   mute()
   cardowner = card.owner
   clearAttachLinks(card)
   card.moveTo(cardowner.piles['Discard Pile']) 
   if not silent: notify("{} discarded {}".format(me,card))

def bury(card, x = 0, y = 0, silent = False): # Bury a card.
   if card.controller != me: 
      remoteCall(card.controller,"bury",[card])
      return
   mute()
   cardowner = card.owner
   clearAttachLinks(card)
   card.moveTo(cardowner.piles['Bury Pile']) 
   if not silent: notify("{} buried {}".format(me,card))

def discardTarget(table = table, x = 0, y = 0, silent = False, targetCards = None):
   mute()
   if not targetCards: targetCards = [c for c in table if c.targetedBy and c.targetedBy == me]
   if not len(targetCards): notify(":::ERROR::: You need to target the card you're trying to discard with this action")
   for card in targetCards:
      if card.controller != me: remoteCall(card.controller,'discard',[card,0,0,silent])
      else: discard(card,silent = silent)
   
def useAbility(card, x = 0, y = 0): 
   mute()
   if not card.markers[mdict['Used Ability']] or (card.markers[mdict['Used Ability']] and confirm("You seem to have already used the ability of {} this turn. Bypass?".format(card.Name))):
      card.markers[mdict['Used Ability']] += 1
      notify("{} uses the ability of {}".format(me,card))
   
def springStraighten(group, x = 0, y = 0):
   mute()
   if getGlobalVariable('Phase') != '1': #One can only call for refresh during the Nighfall phase
      if not confirm(":::WARNING::: It is not yet the Spring phase. Do you want to jump to Spring now?"): return
      goToSpring()
   cards = (card for card in table
                 if card.controller == me)
   for card in cards: card.orientation = Rot0
   notify("Sundown refreshes {} cards and refills their hand back to {}.".format(me, handsize))

def winterRefill(group, x=0,y=0):
   mute()
   drawMany(me.Deck,4,silent = True)
   handlimit = 4 + len([card for card in table if card.controller == me and card.Type =='Castle'])
   if me.hand > handlimit:
      whisper(":::WARNING::: You are above your handlimit of {}. Please discard {} cards before proceeding to Spring".format(handlimit,len(me.hand) - handlimit))
   cards = (card for card in table
                 if card.controller == me)
   for card in cards: card.markers[mdict['Used Ability']] = 0
   
def inspectCard(card, x = 0, y = 0): # This function shows the player the card text, to allow for easy reading until High Quality scans are procured.
   if card.Text == '': information("{} has no text".format(card.name))
   else: information("{}".format(card.Text))
   
def inspectTarget(table, x = 0, y = 0): # This function shows the player the card text, to allow for easy reading until High Quality scans are procured.
   for c in table:
      if c.targetedBy and c.targetedBy == me: 
         if c.Text == '': information("{} has no text".format(c.name))
         else: information("{}".format(c.Text))
   
def setOrdained(winner):
   strongholds = (card for card in table
              if card.Type == 'Stronghold')
   for stronghold in strongholds:
      if stronghold.owner == winner: outfit.markers[mdict['Ordained']] = 1
      else: outfit.markers[mdict['Ordained']] = 0

#---------------------------------------------------------------------------
# Marker functions
#---------------------------------------------------------------------------


def addFood(card, x = 0, y = 0): 
   mute()
   notify("{} adds a food counter on {}".format(me, card))
   card.markers[mdict['Food']] += 1
    
def delFood(card, x = 0, y = 0): 
   mute()
   if card.markers[mdict['Food']]:
      notify("{} removes a food counter from {}".format(me, card))
      card.markers[mdict['Food']] -= 1
   else: whisper(":::ERROR::: There is no more food to remove from this card")
    
def addTwoTwo(card, x = 0, y = 0): 
   mute()
   notify("{} adds a +2/+2 counter on {}".format(me, card))
   card.markers[mdict['+2/+2']] += 1
    
def addMinusSTR(card, x = 0, y = 0):
   mute()
   notify("{} adds a -1 Strength counter on {}".format(me, card))
   card.markers[mdict['-1 Strength']] += 1
    
def addMinusWILL(card, x = 0, y = 0): 
   mute()
   notify("{} adds a -1 Will counter on {}".format(me, card))
   card.markers[mdict['-1 Will']] += 1
    
def addMarker(cards, x = 0, y = 0): # A simple function to manually add any of the available markers.
   mute()
   marker, quantity = askMarker() # Ask the player how many of the same type they want.
   if quantity == 0: return
   for card in cards: # Then go through their cards and add those markers to each.
      card.markers[marker] += quantity
      notify("{} adds {} {} counter to {}.".format(me, quantity, marker[0], card))	
      
def addUndeadMarker(card, x = 0, y = 0):
   mute()
   if card.Type == "Dude":
      if card.markers[mdict['Undead']] == 1 or re.search(r'Undead.', card.Keywords):
         notify("{} is already undead!".format(card))
      else:
         notify("{} has come back from the grave as one of the undead.".format(card))
         card.markers[mdict['Undead']] += 1

#---------------------------------------------------------------------------
# Battle actions
#---------------------------------------------------------------------------        

def joinBattle(card, x = 0, y = 0): 
   if card.Type == "Hero" : 
       mute () 
       notify("{} is joining the battle.".format(card))
       card.highlight = BattleColor
      
def leaveBattle(card, x = 0, y = 0): # Same as above pretty much but also clears the shootout highlights.
   if card.controller != me:
      remoteCall(card.controller,'leaveBattle',[card,x,y])
      return
   if card.highlight == BattleColor: 
      card.highlight = None
      notify("{} left the battle.".format(card))
      
#---------------------------------------------------------------------------
# Hand and Deck actions
#---------------------------------------------------------------------------
      
def playcard(card,retainPos = False): 
   mute()
   chkcards = [] # Create an empty list to fill later with cards to check
   uniquecards = [tablecard for tablecard in table # Lets gather all the cards from the table that may prevent us from playing our card
                  if tablecard.name == card.name # First the card need to be the same as ours
                  and tablecard != card # In case they played the card by drag & dropping it
                  and tablecard.owner == me # Cards are unique only for each owner.
                  and re.search('Unique', tablecard.Keywords)]
   if len(uniquecards): # Now we check the combined list to see if anything will block us from playing our card from the hand.
      notify ("{} wanted to bring {} into play they but already have a copy of it in play".format(me,card))     
      return
   if card.Type == "Item" or card.Type == "Cohort": 
      hostCard = findHost(card)
      if not hostCard:
         whisper("You need to target the card which is going to attach the card")
         if retainPos: card.moveTo(me.hand)
         return
      else:
         notify("{} has attached a {}.".format(hostCard, card))
         attachCard(card,hostCard)
   else: 
      placeCard(card)
      notify("{} plays {} from their hand.".format(me, card))
   
def shuffle(group): # A simple function to shuffle piles
   group.shuffle()

def reshuffle(group = me.piles['Discard Pile']): # This function reshuffles the player's discard pile into their deck.
   mute()
   Deck = me.Deck # Just to save us some repetition
   for card in group: card.moveTo(Deck) # Move the player's cards from the discard to their deck one-by-one.
   Deck.shuffle() # Then use the built-in shuffle action
   notify("{} reshuffled their {} into their Deck.".format(me, group.name)) # And inform everyone.

def draw(group = me.Deck): # Draws one card from the deck into the player's hand.
   mute()
   if len(group) == 0: # In case the deck is empty, invoke the reshuffle function.
      notify("{}'s Deck empty. Will reshuffle discard pile".format(me))
      reshuffle()
   group.top().moveTo(me.hand)
   notify("{} draws a card.".format(me))   
   
def drawMany(group, count = None, destination = None, silent = False): # This function draws a variable number cards into the player's hand.
   mute()
   if destination == None: destination = me.hand
   if count == None: count = askInteger("Draw how many cards to your Play Hand?", 5) # Ask the player how many cards they want.
   if count == None: return
   for i in range(0, count): 
      if len(group) == 0: reshuffle() # If before moving a card the deck is empty, reshuffle.
      group.top().moveTo(me.hand) # Then move them one by one into their play hand.
   if not silent: notify("{} draws {} cards to their play hand.".format(me, count)) # And if we're "loud", notify what happened.

def setHandSize(group): # A function to modify a player's hand size. This is used during nighfall when refilling the player's hand automatically.
   global handsize
   handsize = askInteger("What is your current hand size?", handsize)
   if handsize == None: handsize = 5
   notify("{} sets their hand size to {}".format(me, handsize))
   
def handDiscard(card, x = 0, y = 0): # Discard a card from your hand.
   mute()
   card.moveTo(me.piles['Discard Pile'])
   notify("{} has discarded {}.".format(me, card))  

def handBury(card, x = 0, y = 0): # Bury a card from your hand.
   mute()
   card.moveTo(me.piles['Bury Pile'])
   notify("{} has buried {}.".format(me, card))  

def handShuffle(group, x = 0, y = 0): # Shuffle your hand back into your deck
   if not confirm("Are you sure you want to shuffle your hand into your deck?"): return
   notify("{} is shuffling their hand back into their deck...".format(me))
   groupToDeck(group,silent = True)
   whisper("Shuffling...")
   shuffle(me.Deck) # We do a good shuffle this time.
   whisper("Shuffle completed.")
       
def groupToDeck (group = me.hand, player = me, silent = False):
   debugNotify(">>> groupToDeck(){}".format(extraASDebug())) #Debug
   mute()
   deck = player.Deck
   count = len(group)
   for c in group: c.moveTo(deck)
   if not silent: notify ("{} moves their whole {} to their {}.".format(player,group.name,deck.name))
   if debugVerbosity >= 3: notify("<<< groupToDeck() with return:\n{}\n{}\n{}".format(group.name,deck.name,count)) #Debug
   else: return(group.name,deck.name,count) # Return a tuple with the names of the groups.
   

def randomDiscard(group): # Discard a card from your hand randomly.
   mute()
   card = group.random() # Select a random card
   if card == None: return # If hand is empty, do nothing.
   notify("{} randomly discards a card.".format(me)) # Inform that a random card was discarded
   card.moveTo(me.piles['Discard Pile']) # Move the card in the discard pile.

def moveIntoDeck(group): 
   mute()
   Deck = me.Deck
   for card in group: card.moveTo(Deck)
   notify("{} moves their {} into their Deck.".format(me, group.name))
   