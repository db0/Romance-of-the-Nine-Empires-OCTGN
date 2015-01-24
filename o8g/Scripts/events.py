import re
import collections
import time

def chkTwoSided():
   mute()
   #confirm('test1')
   if not table.isTwoSided(): information(":::WARNING::: This game is designed to be played on a two-sided table. Things will not look right!! Please start a new game and unckeck the appropriate button.")

def chooseSide(): # Called from many functions to check if the player has chosen a side for this game.
   mute()
   global playerside, playeraxis
   if playerside == None:  # Has the player selected a side yet? If not, then...
     if me.hasInvertedTable():
        playeraxis = Yaxis
        playerside = -1
     else:
        playeraxis = Yaxis
        playerside = 1
   
def checkDeck(player,groups):
   mute()
   chooseSide()
   stronghold = None
   castlesList = []
   if player == me:
      #confirm(str([group.name for group in groups]))
      for group in groups:
         if group == me.hand:
            for card in group:
               if card.Type == 'Stronhold': 
                  notify("{} is playing {}".format(player,card.Name))
                  stronghold = card
               if card.Type == 'Castle': 
                  castlesList.append(card)
            if not stronghold: 
               information(":::ERROR::: No Stronghold card found! Please put an stronghold card in your deck before you try to use it in a game!")
               return
            if not len(castlesList): 
               information(":::ERROR::: No castles found! Please put some castles in your deck before you try to use it in a game!")
               return
         castlesCost = 0
         for castle in castlesList:
            castlesCost += num(castle.properties['Point Cost'])
            if castlesCost > num(stronghold.Strength):
               information(":::ERROR::: Your castles cost more than your available castle points! Please remove some castles from your deck before you try to use it in a game!")               
         else:
            counts = collections.defaultdict(int)
            ok = True
            for card in group:
               if counts[card.name] > 3: 
                  ok = False
                  notify(":::ERROR::: More than 3 cards of the same name ({}) found in {}'s deck!".format(card.Name,player))
            deckLen = len(group)
            if deckLen < 55:
               ok = False
               notify(":::ERROR::: {}'s deck is less than 55 cards ({})!".format(player,deckLen))
            if ok: notify("-> Deck of {} is OK!".format(player))
            else: 
               notify("-> Deck of {} is _NOT_ OK!".format(player))
               information("We have found illegal cards in your deck. Please load a legal deck!")
   # WiP Checking deck legality. 
   
def checkMovedCard(player,card,fromGroup,toGroup,oldIndex,index,oldX,oldY,x,y,isScriptMove,highlight = None,markers = None):
   mute()
   debugNotify("isScriptMove = {}".format(isScriptMove))
   if isScriptMove: return # If the card move happened via a script, then all automations should have happened already.
   if fromGroup == me.hand and toGroup == table: 
      if card.Type == 'Stronghold': 
         card.moveTo(me.hand)
         update()
         setup(group = table)
      else: playcard(card, retainPos = True)
   elif fromGroup != table and toGroup == table and card.owner == me: # If the player moves a card into the table from Hand, or Trash, we assume they are installing it for free.
      if card.Type == 'Cohort' or card.Type == 'Item':
         hostCard = findHost(card)
         if hostCard: 
            attachCard(card,hostCard)
            notify(":> {} was attached to {}".format(card,hostCard))
   elif fromGroup == table and toGroup != table and card.owner == me: # If the player dragged a card manually from the table to their discard pile...
      clearAttachLinks(card) # If the card was manually removed from play then we simply take care of any attachments
   elif fromGroup == table and toGroup == table and card.controller == me: # If the player dragged a card manually to a different location on the table, we want to re-arrange the attachments
      if card.Type == 'Hero': orgAttachments(card) 
   