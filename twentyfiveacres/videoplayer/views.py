from django.shortcuts import render

# Create your views here.
def play_video(request):
    return render(request, 'videoplayer/video.html')


