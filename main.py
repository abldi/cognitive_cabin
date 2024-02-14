from video_analysis import VideoAnalysis

va = VideoAnalysis(device_index=0)
# va = VideoAnalysis(video_path='/home/tamaya/Documents/cognitive_cabin/test_video_01.mp4')
va.run_forever()
