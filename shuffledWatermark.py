import subprocess
import uuid
import cv2
import pytesseract
import json
import random
import ffmpeg

# getting the video length
cap = cv2.VideoCapture('input.mp4')
total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
fps = cap.get(cv2.CAP_PROP_FPS)
duration = total_frames / fps


textOverlayA = 'XYZ'

textOverlayA = 'XYZ'

applyWatermarkA = (f'ffmpeg -y -i input.mp4 -filter_complex '
              f'"[0:v]drawtext=fontfile=arial.ttf:fontsize=45*trunc(h/720):'
              f'text=\'{textOverlayA}\':x=10:y=10:fontcolor=white@1.0:box=1:boxcolor=black@1.0,'
              f'format=yuva444p[text];[0:v][text]overlay=10:10"'
              f' -c:a copy watermarkedVideoA.mp4')

subprocess.run(applyWatermarkA, shell=True)

textOverlayB = 'UVW'

applyWatermarkB = (f'ffmpeg -y -i input.mp4 -filter_complex '
              f'"[0:v]drawtext=fontfile=arial.ttf:fontsize=45*trunc(h/720):'
              f'text=\'{textOverlayB}\':x=10:y=10:fontcolor=white@1.0:box=1:boxcolor=black@1.0,'
              f'format=yuva444p[text];[0:v][text]overlay=10:10"'
              f' -c:a copy watermarkedVideoB.mp4')

subprocess.run(applyWatermarkB, shell=True)

lowestResolutionB = f'ffmpeg -y -i watermarkedVideoB.mp4 -vf "scale=-2:420:force_original_aspect_ratio=decrease" lowWatermarkedVideoB.mp4'

subprocess.run(lowestResolutionB, shell=True)

lowestResolutionA = f'ffmpeg -y -i watermarkedVideoA.mp4 -vf "scale=-2:420:force_original_aspect_ratio=decrease" lowWatermarkedVideoA.mp4'

subprocess.run(lowestResolutionA, shell=True)

fragmentA = f'ffmpeg -y -i watermarkedVideoA.mp4 -c:v h264 -flags +cgop -g 30 -hls_time 1 fragA.m3u8'
subprocess.run(fragmentA, shell=True)

fragmentB = f'ffmpeg -y -i watermarkedVideoB.mp4 -c:v h264 -flags +cgop -g 30 -hls_time 1 fragB.m3u8'

subprocess.run(fragmentB, shell=True)

with open("db.json", "r") as infile:
    db = json.load(infile)

userCombo = db["user1"]

frags = []

tempUserCombo = []
for i in range(0,int(duration)):
    selectChoice = random.choice([textOverlayA,textOverlayB])
    if(selectChoice == textOverlayA):
        selectedFragment = 'fragA'+ str(i) +'.ts'
    else:
        selectedFragment = 'fragB'+ str(i) +'.ts'

    userCombo.append(selectChoice)
    frags.append(selectedFragment)

with open("db.json", "w") as outfile:
    json.dump(db, outfile)

with open("out.m3u8", "w") as f:
    f.write("#EXTM3U\n")
    f.write("#EXT-X-VERSION:3\n")
    f.write("#EXT-X-MEDIA-SEQUENCE:0\n")
    f.write("#EXT-X-INDEPENDENT-SEGMENTS\n")
    f.write("#EXT-X-DISCONTINUITY-SEQUENCE:1\n")
    for i in range(0,int(duration)):
        f.write("#EXTINF:1.000000,\n")
        f.write(frags[i]+ '\n')

    f.write("#EXT-X-ENDLIST\n")
f.close()

shuffleFrags = f'ffmpeg -y -protocol_whitelist "file,http,https,tcp,tls" -i out.m3u8 -c copy shuffledWatermarkOutput.mp4'
subprocess.run(shuffleFrags, shell=True)
