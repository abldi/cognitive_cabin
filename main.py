from video_analysis import VideoAnalysis

if __name__ == '__main__':
    # audio_analysis.test_compatibility()
    # audio_analysis.list_audio_devices()

    # aa = AudioAnalysis(10)
    # va = VideoAnalysis(device_index=0, window_sec=3, grid_img_nb=9)
    va = VideoAnalysis(video_path='/home/tamaya/Documents/cognitive_cabin/test_stuff/14.02.2024/landscape_video_sample_1.mp4',
                       window_sec=15,
                       grid_img_nb=4,
                       width=200)
    va.run_forever()

    # video_thread = threading.Thread(target=va.run_forever)
    # audio_thread = threading.Thread(target=aa.run_forever)

    # video_thread.start()
    # audio_thread.start()
