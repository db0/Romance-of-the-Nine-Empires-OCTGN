    # Python Scripts for the Doomtown  CCG definition for OCTGN
    # Copyright (C) 2013  Konstantine Thoukydides

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


import re, time

debugVerbosity = -1 # At -1, means no debugging messages display

Automations = {'Play'                   : True, # If True, game will automatically trigger card effects when playing or double-clicking on cards. Requires specific preparation in the sets.
               'Triggers'               : True, # If True, game will search the table for triggers based on player's actions, such as installing a card, or discarding one.
               'WinForms'               : True, # If True, game will use the custom Windows Forms for displaying multiple-choice menus and information pop-ups
               'Placement'              : True, # If True, game will try to auto-place cards on the table after you paid for them.
               'Start/End-of-Turn/Phase': True # If True, game will automatically trigger effects happening at the start of the player's turn, from cards they control.                
              }                  
                  

CardsAA = {} # Dictionary holding all the AutoAction scripts for all cards
CardsAS = {} # Dictionary holding all the autoScript scripts for all cards
Stored_Keywords = {} # A Dictionary holding all the Keywords a card has.
               
#------------------------------------------------------------------------------
# Card Attachments scripts
#------------------------------------------------------------------------------

def findHost(card):
   # Tries to find a host to attach the gear
   targetedCards = [c for c in table if c.targetedBy and c.targetedBy == me and c.Type == 'Hero' and c.controller == me]
   if not len(targetedCards):
      whisper(":::ERROR::: Please Target a valid Hero for this {}".format(card.Type))
   else: result = targetedCards[0] 
   return result

def attachCard(attachment,host,facing = 'Same'):
   hostCards = eval(getGlobalVariable('Host Cards'))
   hostCards[attachment._id] = host._id
   setGlobalVariable('Host Cards',str(hostCards))
   orgAttachments(host,facing)
   
def clearAttachLinks(card):
# This function takes care to discard any attachments of a card that left play
# It also clear the card from the host dictionary, if it was itself attached to another card
# If the card was hosted by a Daemon, it also returns the free MU token to that daemon
   hostCards = eval(getGlobalVariable('Host Cards'))
   cardAttachementsNR = len([att_id for att_id in hostCards if hostCards[att_id] == card._id])
   if cardAttachementsNR >= 1:
      hostCardSnapshot = dict(hostCards)
      for attachmentID in hostCardSnapshot:
         if hostCardSnapshot[attachmentID] == card._id:
            if Card(attachmentID) in table: 
               discard(Card(attachmentID)) # We always just discard attachments 
            del hostCards[attachmentID]
   if hostCards.has_key(card._id):
      hostCard = Card(hostCards[card._id])
      del hostCards[card._id] # If the card was an attachment, delete the link
      setGlobalVariable('Host Cards',str(hostCards)) # We store it before calling orgAttachments, so that it has the updated list of hostCards.
      orgAttachments(hostCard) 
   else: setGlobalVariable('Host Cards',str(hostCards))


def orgAttachments(card,facing = 'Same'):
# This function takes all the cards attached to the current card and re-places them so that they are all visible
# xAlg, yAlg are the algorithsm which decide how the card is placed relative to its host and the other hosted cards. They are always multiplied by attNR
   if card.controller != me: 
      remoteCall(card.controller,'orgAttachments',[card,facing])
      return
   attNR = 1
   xAlg = 0 # The Default placement on the X axis, is to place the attachments at the same X as their parent
   yAlg = -(cwidth() / 4)
   hostCards = eval(getGlobalVariable('Host Cards'))
   cardAttachements = [Card(att_id) for att_id in hostCards if hostCards[att_id] == card._id]
   x,y = card.position
   for attachment in cardAttachements:
      if facing == 'Faceup': FaceDown = False
      elif facing == 'Facedown': FaceDown = True
      else: # else is the default of 'Same' and means the facing stays the same as before.
         if attachment.isFaceUp: FaceDown = False
         else: FaceDown = True
      attachment.moveToTable(x + (xAlg * attNR), y + (yAlg * attNR),FaceDown)
      if attachment.controller == me and FaceDown: attachment.peek()
      attachment.setIndex(len(cardAttachements) - attNR) # This whole thing has become unnecessary complicated because sendToBack() does not work reliably
      attNR += 1
   card.sendToFront() # Because things don't work as they should :(

#---------------------------------------------------------------------------
# Debug
#---------------------------------------------------------------------------
  
   
def addC(cardModel,count = 1): # Quick function to add custom cards on the table depending on their GUID
# Use the following to spawn a card
# remoteCall(me,'addC',['<cardGUID>'])
   card = table.create(cardModel, 0,0, count, True)
   
def reconnect(group=table,x=0,y=0):
   chooseSide()