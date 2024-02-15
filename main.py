from video_analysis import VideoAnalysis

va = VideoAnalysis(device_index=0)
# va = VideoAnalysis(video_path='/home/tamaya/Documents/cognitive_cabin/test_video_01.mp4')
# va = VideoAnalysis(video_path='/home/tamaya/Documents/cognitive_cabin/test_stuff/14.02.2024/portrait_video_sample_2.mp4')

va.run_forever()
