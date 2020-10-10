from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
import os
import shutil
import ibm_boto3
from ibm_botocore.client import Config
from zipfile import ZipFile
from tkinter import *
import tkinter.font as font
from tkinter.filedialog import askdirectory
from PIL import ImageTk, Image
from datetime import date

# set watson vr service credentials
iam = IAMAuthenticator("8u43aL-G3G-dNVCwDRCM8k_G7J_zBFxR3fY3hmSOmsGV")
vr = VisualRecognitionV3(
    version= "2018-03-19",
    authenticator = iam
)
vr.set_service_url("https://api.eu-de.visual-recognition.watson.cloud.ibm.com/instances/f2070f39-5b4b-42c1-a37c-8344e52040e8")

# function to browse, classify local images
def classifyLocal():
    dir = './no-mask/'
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)
    location = askdirectory()
    for file in os.listdir(location):
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')) :
            result=vr.classify(classifier_ids="ClassificationModel_885635333",threshold='0.6',images_file=open(location+"/"+file,"rb")).get_result()
            print(json.dumps(result, indent=2))
            if float(result["images"][0]["classifiers"][0]["classes"][0]["score"]) >= 0.9:
                print("image contains "+result["images"][0]["classifiers"][0]["classes"][0]["class"])
                if result["images"][0]["classifiers"][0]["classes"][0]["class"] == "no mask":
                    shutil.copy(location+"/"+file,dir)
                    print("send to cloud")
            else: print("bad image, cannot classify")
        else: print("not an image file error")
    print("classification complete")
    notif1=Label(text="Classification Complete!",fg="green")
    notif1.pack()

# function to upload classified folder to cloud object storage
def upload():
    cos = ibm_boto3.client(service_name='s3',ibm_api_key_id="TOcnjLwKhBWfhiONJJjoeyQAVLOejD63dHlGzQFlsoah",
    ibm_service_instance_id="crn:v1:bluemix:public:iam-identity::a/b3dd5352f75d455d8b3196a7543276eb::serviceid:ServiceId-5f6c7a2b-9d4a-4ec4-b6a6-cdbce4be228f",
    config=Config(signature_version='oauth'),endpoint_url="https://s3.eu.cloud-object-storage.appdomain.cloud")
    # create a ZipFile object
    with ZipFile('no-mask.zip', 'w') as zipObj:
        for image in os.listdir("./no-mask/"):
            # Add file to zip
            zipObj.write("./no-mask/"+image )
    d1 = date.today().strftime("%d/%m/%Y")
    try:
        res = cos.upload_file('./no-mask.zip',Bucket='maskdetector-donotdelete-pr-2vtgzmmygdbdsb', Key='result-'+d1+'.zip')
    except Exception as e:
        print(Exception, e)
    else:
        print('File Uploaded')
        notif2=Label(text="Upload Complete!",fg="green")
        notif2.pack()

# function to download prev results from cloud
def download():
    cos = ibm_boto3.client(service_name='s3',ibm_api_key_id="TOcnjLwKhBWfhiONJJjoeyQAVLOejD63dHlGzQFlsoah",
    ibm_service_instance_id="crn:v1:bluemix:public:iam-identity::a/b3dd5352f75d455d8b3196a7543276eb::serviceid:ServiceId-5f6c7a2b-9d4a-4ec4-b6a6-cdbce4be228f",
    config=Config(signature_version='oauth'),endpoint_url="https://s3.eu.cloud-object-storage.appdomain.cloud")
    try:
        res2 = cos.download_file(Bucket='maskdetector-donotdelete-pr-2vtgzmmygdbdsb',Key='result-'+resdate.get()+'.zip',Filename='./downloaded-results.zip')
    except Exception as e:
        print(Exception, e)
        notif4=Label(text="Date not found!",fg="red")
        notif4.pack()
    else:
        print('File Downloaded')
        notif3=Label(text="Download Complete!",fg="green")
        notif3.pack()

# >> tkinter gui code from this point >>
root = Tk()
root.title("Mask Detector")

# set app icon
p1 = PhotoImage(file = "icon.png")
root.iconphoto(False, p1)

# set window size
w, h = root.winfo_screenwidth(), root.winfo_screenheight()-70
root.geometry("%dx%d+0+0" % (w/2, h))

img = ImageTk.PhotoImage(Image.open("banner.png"))
panel = Label(root, image = img)
panel.pack(side = "top", fill = "both")

welcome = Label(root,text="Mask Detector")
welcome["font"] = font.Font(family='Courier', size=30, weight='bold')
welcome.pack()

step1 = Label(text="Step1: Browse the folder containg the images for classification",fg="#0F216C",highlightbackground='red')
step1.pack()

button0 = Button(root, text="[ Browse ]", command=classifyLocal) 
button0.pack(side=TOP)

step2 = Label(text="\nStep2: Do you want to upload the results to cloud?",fg="#0F216C")
step2.pack()

button1 = Button(root, text="[ Upload ]", command=upload) 
button1.pack(side=TOP)

step3 = Label(text="\nStep3: Download previous results.\n Please enter the date(dd/mm/yyyy) for which you need results",fg="#0F216C")
step3.pack()

resdate = Entry(root) 
resdate.pack()

button2 = Button(root, text="[ Download ]", command=download) 
button2.pack(side=TOP)

log = Label(text="\nLog:",fg="#0F216C")
log.pack()

root.mainloop()


