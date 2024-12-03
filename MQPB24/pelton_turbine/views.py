# pelton_turbine/views.py
from django.shortcuts import render
from .utils import get_chat_completion,execute_pelton_turbine_function,generate_pelton_turbine_image,get_pelton_turbine_review

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def calculate_parameters(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug('Received data: %s', data)
            description = data['description']
            parameters = data['parameters']
            
            # Call the backend function to calculate results
            results = execute_pelton_turbine_function(description, parameters['flowRate'], parameters['nozzleDiameter'], parameters['distance'])
            logger.debug('Calculated results: %s', results)
            
            # Store results in session
            request.session['turbine_results'] = results
            
            return JsonResponse(results)
        
        except KeyError as e:
            logger.error('Missing parameter: %s', e)
            return JsonResponse({'error': f'Missing parameter: {e}'}, status=400)
        except json.JSONDecodeError:
            logger.error('Invalid JSON')
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        logger.error('Invalid request method')
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def generate_review(request):
    if request.method == 'GET':
        # Retrieve parameters from session
        turbine_results = request.session.get('turbine_results', {})
        bucket_depth = turbine_results.get('bucket_depth')
        bucket_angle = turbine_results.get('bucket_angle')
        bucket_spacing = turbine_results.get('bucket_spacing')
        nozzle_alignment = turbine_results.get('nozzle_alignment')
        
        # Add error handling if necessary
        if not all([bucket_depth, bucket_angle, bucket_spacing, nozzle_alignment]):
            return JsonResponse({'error': 'Missing parameters in session'}, status=400)

        review = get_pelton_turbine_review(bucket_depth, bucket_angle, bucket_spacing, nozzle_alignment)
        image_url = generate_pelton_turbine_image()
        return JsonResponse({'review': review, 'imageUrl': image_url})

def welcome(request):
    return render(request, 'pelton_turbine/welcome.html')

def step2(request):
    return render(request, 'pelton_turbine/step2.html')

def loading(request):
    return render(request, 'pelton_turbine/loading.html')

def results(request):
    return render(request, 'pelton_turbine/result.html')