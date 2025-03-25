As part of the assignment I am submitting the following files:

1. A main script in python file ocr5.py with 3 endpoints in it
		
	POST /image-sync:
	Description: This endpoint is used for synchronous image processing.
	Method: POST
	Input: JSON payload containing the base64-encoded image data.
	Output: JSON response containing the recognized text extracted from the image.

	POST /image:
	Description: This endpoint is used for asynchronous image processing.
	Method: POST
	Input: JSON payload containing the base64-encoded image data.
	Output: JSON response containing a unique task ID for the asynchronous processing task.
	
	GET /image:
	Description: This endpoint is used to retrieve result of asynchronous image processing task.
	Method: GET
	Input: JSON payload containing the task ID.
	Output: JSON response with the recognized text result corresponding to the provided task ID.

2. Folder named ocr which is a virtual environment created for the project
3. File named requirements.txt which has the basic requirements including:
	1. Flask==2.1.1
	2. Celery==5.1.2
	3. redis==4.1.1
	4. Pillow==8.4.0
	5. pytesseract==0.3.8
4. Folder named ocr_results that stores the text recognised by pytesseract in asynchronous mode.
5. File image_base64.txt that is created after converting any given image into base64.
6. A few images on which ocr was performed.


///////////////////////////////////////////
The execution and testing in steps given below should not take more than a few minutes:

1. Installing the requirements and activating the virtual environment.
2. Run the redis server in terminal window by running
	redis-server
3. Run the celery server as
	celery -A ocr5.celery worker
4. Run the main script as 
	python ocr5.py
	
5. Once all are running, we can test by sending requests from another terminal window as
	
	1. Synchronous Task
	
	// converting the image.jpg into base64
	base64 -b 0 -i image.jpg -o image_base64.txt 
	
	// sending POST request to image-sync
	 curl -X POST -H "Content-Type: application/json" -d '{"image_data": "'$(cat image_base64.txt)'"}' http://localhost:5000/image-sync
	
	// that returns the recognised text as
	{"text":"Requirements\nMore concretely, we would like you to implement:\n\n1. Aweb service that implements the above API.\n\n2. For the \"asyne\" API (POST /image and GET /image), itis expected that the actual OCR is run through\n\u2018some background worker(s), that do not block the web server implementing the web API.\n\n3. For the actual OCR, we recommend you to use tesseract.\n\n(One way to use tesseract is to use a Ubuntu docker container defined as follows:\n"}
	
	2. Asynchronous Task

	// sending POST request to image
	curl -X POST -H "Content-Type: application/json" -d '{"image_data": "'$(cat image_base64.txt)'"}' http://localhost:5000/image

	// response is as
	{"task_id":"-3723420779073315134"}
	
	// sending GET request to image
	curl -X GET -H "Content-Type: application/json" -d '{"task_id": "-3723420779073315134"}' "http://localhost:5000/image"
	
	// the response is as
	{"-3723420779073315134":"Requirements\nMore concretely, we would like you to implement:\n\n1. Aweb service that implements the above API.\n\n2. For the \"asyne\" API (POST /image and GET /image), itis expected that the actual OCR is run through\n\u2018some background worker(s), that do not block the web server implementing the web API.\n\n3. For the actual OCR, we recommend you to use tesseract.\n\n(One way to use tesseract is to use a Ubuntu docker container defined as follows:\n"}
	
	// if the task is not finished & the task id is not present in the file, returns null
	curl -X GET -H "Content-Type: application/json" -d '{"task_id": "-372342077907331513"}' "http://localhost:5000/image" 
	// response
	{"-372342077907331513":null}

///////////////////////
