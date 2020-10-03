from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json

iam = IAMAuthenticator("8u43aL-G3G-dNVCwDRCM8k_G7J_zBFxR3fY3hmSOmsGV")
vr = VisualRecognitionV3(
    version="2018-03-19",
    authenticator=iam
)
vr.set_service_url("https://api.eu-de.visual-recognition.watson.cloud.ibm.com/instances/f2070f39-5b4b-42c1-a37c-8344e52040e8")
# vr.set_disable_ssl_verification(True)
classes=vr.classify(classifier_ids="ClassificationModel_885635333",
threshold='0.6',url="https://upload.wikimedia.org/wikipedia/commons/a/a0/Pierre-Person.jpg").get_result()
print(json.dumps(classes, indent=2))