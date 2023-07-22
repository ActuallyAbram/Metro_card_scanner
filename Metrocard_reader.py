# Abram Huang
# 050423
# QR Code Module: Metrocard kiosk
import qrcode
import cv2
import numpy as np
import smtplib
import config
from smtplib import SMTP
from smtplib import SMTPException
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#defines an class called metro_card that stores basic info like the user's name, balance, entry status, and the name of the qrcode file
class metro_card:
    def __init__(self,id,balance):
        self.id=id
        self.balance=balance
        self.entry=False
        self.codeStr=""
    # returns a new QR code
    def get_new_card(self):
        self.update_QR_code()
    # returns the balance
    def getBalance(self):
        return self.balance
    # updates QR code with new balance
    def update_QR_code(self):
        msg=self.id+","+str(self.balance)
        code=qrcode.make(msg)
        self.codeStr=str(self.id)+".png"
        code.save(str(self.id)+".png")
    # Adds money to card and updates QR code
    def add_balance(self,money):
        self.balance=str(int(self.balance)+int(money))
        self.update_QR_code()
    # Checks if user has enough money to pass through gate
    def enough_balance(self):
        if self.balance >=1:
            return True
        return False
    # Completes transaction and updates balance accordingly
    def make_transaction(self):
        self.balance=self.balance-1
        self.update_QR_code()
        print("Transaction successful")

# Scans QR code and creates a bounding box around it. Also displays entry status as pass or closed
def scan_QR():
    # Open video capture
    cap = cv2.VideoCapture(0)

    # define detector
    detector = cv2.QRCodeDetector()
    newCard = metro_card(0, 0)
    while True:
        check, img = cap.read()
        data, bbox, _ = detector.detectAndDecode(img)
        if (bbox is not None and len(data)>0):
            msg=data.split(",")
            id = str(msg[0])
            balance = int(msg[1])
            #Stores name and balance into metro_card object
            newCard=metro_card(id,balance)
            color=(0,0,255)
            text=""
            entry=newCard.enough_balance()
            # If user can pass through gate, updates screen overlay and entry status
            if entry:
                text="Pass!"
                color=(0,255,0)
                newCard.entry=True
            else:
                text="Sorry,you are broke"
                newCard.entry=False
            bbox = [bbox[0].astype(int)]

            for i in range(len(bbox[0])):
                cv2.line(img, tuple(bbox[0][i]), tuple(bbox[0][(i + 1) % len(bbox[0])]), color, thickness=4)
                cv2.putText(img, text, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 2,
                            color, 2)
        cv2.imshow("QR Code detector", img)

        if (cv2.waitKey(1) == ord("q")):
            break

    cap.release()
    cv2.destroyAllWindows()
    return newCard

#displays available balance on card
def checkBalance():
    # Open video capture
    cap = cv2.VideoCapture(0)
    # define detector
    detector = cv2.QRCodeDetector()
    newCard=metro_card(0,0)
    while True:
        check, img = cap.read()
        data, bbox, _ = detector.detectAndDecode(img)
        if (bbox is not None and len(data) > 0):
            msg = data.split(",")
            id = str(msg[0])
            balance = msg[1]
            newCard = metro_card(id, balance)
            color = (0, 0, 255)
            bbox = [bbox[0].astype(int)]
            text="$"+balance
            for i in range(len(bbox[0])):
                cv2.line(img, tuple(bbox[0][i]), tuple(bbox[0][(i + 1) % len(bbox[0])]), color, thickness=4)
                cv2.putText(img, text, (int(bbox[0][0][0]), int(bbox[0][0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 2,
                            color, 2)
        cv2.imshow("QR Code detector", img)

        if (cv2.waitKey(1) == ord("q")):
            break

    cap.release()
    cv2.destroyAllWindows()
    return newCard

# emails new QR code, as well as balance and user id information to email.
def emailCode(card):
    img_str=card.codeStr
    # Email Settings
    smtpUser = config.smtpUserKey
    smtpPass = config.smtpPassKey

    toAdd = smtpUser
    fromAdd = smtpUser
    subject = "New QR Code "
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = fromAdd
    msg['To'] = toAdd
    msg.preamble = "Open email for image"
    message="User:"+str(card.id)+" Balance:"+str(card.balance)+"\nSee below for updated card"
    body = MIMEText(message)
    msg.attach(body)

    fp = open(img_str, 'rb')
    imgSent = MIMEImage(fp.read())
    fp.close()
    msg.attach(imgSent)
    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login(smtpUser, smtpPass)
    s.sendmail(fromAdd, toAdd, msg.as_string())
    s.quit()
    print("Updated Card Sent")

def main():
    print("Welcome to Metro! The entry fee is $1\nPlease see the following options:")
    print("1.Scan Metrocard for entry")
    print("2.Read balance")
    print("3.Buy Metrocard")
    print("4.Add money to metro")
    print("5.Exit")
    choice=int(input())
    if choice == 1:
        print("Press Q when done scanning")
        newCard=scan_QR()
        print(newCard," msg")
        if newCard.entry:
            newCard.make_transaction()
            emailCode(newCard)
        else:
            print("insufficient funds")
    elif choice == 2:
        print("Press Q when done scanning")
        checkBalance()
    elif choice == 3:
        print("Name")
        name=input()
        print("Amount (dollars only!")
        money=int(input())
        newCard=metro_card(name,money)
        newCard.get_new_card()
        emailCode(newCard)
        print("Enjoy your card!")
    elif choice == 4:
        print("Scan your card please. Press Q when you are done scanning.")
        newCard=checkBalance()
        print("How much money do you want to add?")
        dollars=int(input())
        newCard.add_balance(dollars)
        print("$"+str(dollars)+" were added to this card")
        emailCode(newCard)
    print("Thanks. Have a nice day!")

if __name__=="__main__":
    main()