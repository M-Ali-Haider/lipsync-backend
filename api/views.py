from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from .transcription import transcription
from .translate import translation
import subprocess

# Create your views here.
class VideoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self,request, format=None):
        file_obj = request.FILES.get('video')
        if not file_obj:
            return Response({"error":"No video file provided."},status=status.HTTP_400_BAD_REQUEST)
        
        # Save video file
        filename = default_storage.save(f"videos/{file_obj.name}",file_obj)
        file_path = default_storage.path(filename)

        # Step 1: Transcription
        transcription_text, full_result, txt_output_path = transcription(file_path)
        if not transcription_text:
            return Response({"error":"Transcription failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 2: Translation
        urdu_text = translation(transcription_text,file_path)
        
        # Step 3: TTS Model Inference
        subprocess.run(["python","interface.py"],check=True)
        
        return Response({
            "message": "Video uploaded successfully",
            "file_path": file_path,
            "transcript":transcription_text,
            "urdu_transcript":urdu_text,
            "speaker_count": len(set(utt.get('speaker') for utt in full_result.get('utterances', [])))
        }, status=status.HTTP_201_CREATED)
