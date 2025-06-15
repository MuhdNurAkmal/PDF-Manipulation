import base64
import io
from django.shortcuts import render
import os
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from PyPDF2 import PdfReader, PdfWriter

@csrf_exempt
def split_pdf(request):
    """
    Handles PDF file uploads, splits the PDF into individual pages,
    and returns an array of base64-encoded PDF pages.
    """
    if request.method == 'POST':
        # Check if a file named 'pdf_file' was included in the request
        if 'pdf_file' not in request.FILES:
            return HttpResponseBadRequest("No PDF file provided in the request. Please upload a file with the key 'pdf_file'.")

        pdf_file = request.FILES['pdf_file']

        # Validate if the uploaded file is a PDF
        if not pdf_file.name.lower().endswith('.pdf'):
            return HttpResponseBadRequest("Uploaded file is not a PDF. Please upload a .pdf file.")

        try:
            # Use BytesIO to read the uploaded file content in memory
            # This avoids saving the entire file to disk first
            pdf_bytes = io.BytesIO(pdf_file.read())
            
            # Create a PdfReader object to read the PDF
            reader = PdfReader(pdf_bytes)
            num_pages = len(reader.pages)
            
            split_pages_base64 = []

            # Iterate through each page of the PDF
            for i in range(num_pages):
                writer = PdfWriter()
                # Add the current page to a new PdfWriter
                writer.add_page(reader.pages[i])

                # Save the single page PDF to a new BytesIO object
                # This keeps the split page in memory
                output_pdf_stream = io.BytesIO()
                writer.write(output_pdf_stream)
                output_pdf_stream.seek(0) # Rewind the stream to the beginning for reading

                # Base64 encode the bytes of the single-page PDF
                # The 'data:application/pdf;base64,' prefix is for embedding in web pages (data URI scheme)
                encoded_pdf = base64.b64encode(output_pdf_stream.read()).decode('utf-8')
                split_pages_base64.append(f"data:application/pdf;base64,{encoded_pdf}")
            
            # Return a JSON response with the base64-encoded pages and the total number of pages
            return JsonResponse({
                'pages': split_pages_base64, 
            })

        except Exception as e:
            # Catch any unexpected errors during PDF processing
            return JsonResponse({'status': 'error', 'message': f"An error occurred during PDF processing: {str(e)}"}, status=500)
    else:
        # If the request method is not POST, return a bad request response
        return HttpResponseBadRequest("Only POST requests are allowed for this endpoint.")


# create a simple JSON response for testing
def index(request):
    dummy_data = {
        "message": "This is a dummy response.",
        "status": "success",
        "data": [1, 2, 3, 4, 5]
    }
    return JsonResponse(dummy_data)
