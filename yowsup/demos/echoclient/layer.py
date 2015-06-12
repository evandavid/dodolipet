from yowsup.layers.interface                           import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities  import TextMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities  import ImageDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities  import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_media.protocolentities  import LocationMediaMessageProtocolEntity
from yowsup.layers.protocol_acks.protocolentities      import OutgoingAckProtocolEntity
from yowsup.layers.protocol_media.protocolentities  import VCardMediaMessageProtocolEntity
import unirest


class EchoLayer(YowInterfaceLayer):

    @ProtocolEntityCallback("message")
    def onMessage(self, messageProtocolEntity):

        # if not messageProtocolEntity.isGroupMessage():
        if messageProtocolEntity.getType() == 'text':
            self.onTextMessage(messageProtocolEntity)
        elif messageProtocolEntity.getType() == 'media':
            self.onMediaMessage(messageProtocolEntity)
    
    @ProtocolEntityCallback("receipt")
    def onReceipt(self, entity):
        ack = OutgoingAckProtocolEntity(entity.getId(), "receipt", entity.getType(), entity.getFrom())
        self.toLower(ack)

    def quote(self):
        response = unirest.post("https://andruxnet-random-famous-quotes.p.mashape.com/",
              headers={
                "X-Mashape-Key": "qtmZdTB8lxmsht8sdJz9vLEB0LD9p1CuZovjsnMY6F4PVQyGUK",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json"
              }
            )
        return response.body['quote'] + "\nby " + response.body['author']

    def jokes(self):
        response = unirest.post("http://api.icndb.com/jokes/random")
        return response.body['value']['joke']

    def bible(self):
        response = unirest.post("http://labs.bible.org/api/?passage=random&type=json")
        return response.body[0]['text'] + "\n" + response.body[0]['bookname'] + ' ' + response.body[0]['chapter'] + ':' + response.body[0]['verse']  


    def onTextMessage(self,messageProtocolEntity):

        receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom())
        if 'dave' in messageProtocolEntity.getBody().lower():
            msg = 'Yes Boss'
        elif 'good boy' in messageProtocolEntity.getBody().lower():
            msg = 'Yes, Im a good boy :)'
        elif 'identify yourself' in messageProtocolEntity.getBody().lower():
            msg = 'Im dave, son of David, the most genius person in this room'
        elif 'joke' in messageProtocolEntity.getBody().lower():
            msg = self.jokes()
        elif 'quote' in messageProtocolEntity.getBody().lower():
            msg = self.quote()
        elif 'bible' in messageProtocolEntity.getBody().lower():
            msg = self.bible()
        else:
            msg = messageProtocolEntity.getBody()[::-1]

        outgoingMessageProtocolEntity = TextMessageProtocolEntity(
            msg,
            to = messageProtocolEntity.getFrom())

        print("Echoing %s to %s" % (messageProtocolEntity.getBody(), messageProtocolEntity.getFrom(False)))

        #send receipt otherwise we keep receiving the same message over and over
        self.toLower(receipt)
        self.toLower(outgoingMessageProtocolEntity)

    def onMediaMessage(self, messageProtocolEntity):
        if messageProtocolEntity.getMediaType() == "image":
            
            receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom())

            outImage = ImageDownloadableMediaMessageProtocolEntity(
                messageProtocolEntity.getMimeType(), messageProtocolEntity.fileHash, messageProtocolEntity.url, messageProtocolEntity.ip,
                messageProtocolEntity.size, messageProtocolEntity.fileName, messageProtocolEntity.encoding, messageProtocolEntity.width, messageProtocolEntity.height,
                messageProtocolEntity.getCaption(),
                to = messageProtocolEntity.getFrom(), preview = messageProtocolEntity.getPreview())

            print("Echoing image %s to %s" % (messageProtocolEntity.url, messageProtocolEntity.getFrom(False)))

            #send receipt otherwise we keep receiving the same message over and over
            self.toLower(receipt)
            self.toLower(outImage)

        elif messageProtocolEntity.getMediaType() == "location":

            receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom())

            outLocation = LocationMediaMessageProtocolEntity(messageProtocolEntity.getLatitude(),
                messageProtocolEntity.getLongitude(), messageProtocolEntity.getLocationName(),
                messageProtocolEntity.getLocationURL(), messageProtocolEntity.encoding,
                to = messageProtocolEntity.getFrom(), preview=messageProtocolEntity.getPreview())

            print("Echoing location (%s, %s) to %s" % (messageProtocolEntity.getLatitude(), messageProtocolEntity.getLongitude(), messageProtocolEntity.getFrom(False)))

            #send receipt otherwise we keep receiving the same message over and over
            self.toLower(outLocation)
            self.toLower(receipt)
        elif messageProtocolEntity.getMediaType() == "vcard":
            receipt = OutgoingReceiptProtocolEntity(messageProtocolEntity.getId(), messageProtocolEntity.getFrom())
            outVcard = VCardMediaMessageProtocolEntity(messageProtocolEntity.getName(),messageProtocolEntity.getCardData(),to = messageProtocolEntity.getFrom())
            print("Echoing vcard (%s, %s) to %s" % (messageProtocolEntity.getName(), messageProtocolEntity.getCardData(), messageProtocolEntity.getFrom(False)))
            #send receipt otherwise we keep receiving the same message over and over
            self.toLower(outVcard)
            self.toLower(receipt)
