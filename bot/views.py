from django.shortcuts import render, redirect
from django.http import JsonResponse


ACCESS_TOKEN = '1fe567ad1fe567ad1fe567adf51cce744a11fe51fe567ad785a30ef24c275e663c9b6b6'


def redirect_to_original_url(request):
    return JsonResponse({'error': 'Short link not found'}, status=404)

def shortlink_view(request):
    return JsonResponse({"message": "This is the shortlink view"})