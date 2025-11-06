from flask import Flask, request, jsonify, render_template_string,render_template
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime


import db

app = Flask(__name__,template_folder="templates")

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@app.route('/')
def index():
    """Serve the main HTML page"""
    # In production, serve your HTML file here
    return render_template("index.html")

# Store results in memory (use database in production)
db.create_table()
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image_with_ai(image_path):
    """
    Replace this function with your actual AI model processing
    Example: Use TensorFlow, PyTorch, or any AI model API
    """
    # Simulated AI processing
    # In production, load your model and process the image here
    
    # Example with a hypothetical model:
    # model = load_model('your_model.h5')
    # prediction = model.predict(image_path)
    import model
    emotion = model.analyze_emotion(image_path=image_path)
    # Simulated result
    result = {
        'status': 'success',
        'prediction': emotion,
        'processed_at': datetime.now().isoformat()
    }
    
    return result

@app.route('/upload', methods=['POST'])
def upload_image():
    """Handle image upload and trigger AI processing"""
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Generate unique filename
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Print debug information
            print(f"File info - Name: {file.filename}, Size: {len(file.read())} bytes")
            file.seek(0)  # Reset file pointer after reading
            
            # Save the uploaded file
            file.save(filepath)
            print(f"File saved successfully to: {filepath}")
            
            # Generate result ID
            result_id = str(uuid.uuid4())
            
            # Process image with AI model
            ai_result = process_image_with_ai(filepath)
            
            # Store result
            import json
            db.save_result(result_id=str(result_id),
                           image_path=str(filepath),
                           filename=str(unique_filename),
                           result=json.dumps(ai_result),
                           uploaded_at=str(datetime.now().isoformat()))
            # Store result in database
            import json
            try:
                db.save_result(
                    result_id=str(result_id),
                    image_path=str(filepath),
                    filename=str(unique_filename),
                    result=json.dumps(ai_result),
                    uploaded_at=str(datetime.now().isoformat())
                )
            except Exception as db_error:
                print(f"Database error: {str(db_error)}")
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': f'Database error: {str(db_error)}'}), 500

            return jsonify({
                'success': True,
                'result_id': result_id,
                'message': 'Image uploaded and processed successfully'
            }), 200
            
        except Exception as e:
            print(f"Processing error: {str(e)}")
            # Clean up file if processing fails
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Processing failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/result/<result_id>', methods=['GET'])
def get_result(result_id):
    """Display the AI processing result"""
    
    if not db.is_id_present(result_id):
        return "Result not found", 404
    
    data = db.get_id_data(result_id)
    
    # return render_template_string(
    #     result_template,
    #     filename=data['filename'],
    #     result=data['result']
    # )
    return render_template("result.html",filename=data['filename'],result=data['result'])
@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded images"""
    from flask import send_from_directory
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=port, debug=False)