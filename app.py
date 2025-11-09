import sys
import logging

# Configure logging FIRST
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("=" * 50)
logger.info("🚀 Starting application initialization...")
logger.info("=" * 50)

from flask import Flask, request, jsonify, render_template_string,render_template
import os
import uuid
from datetime import datetime

logger.info("✅ Flask imports successful")
try:
    import db
    import model
    logger.info("✅ Database module imported and model")
except Exception as e:
    logger.error(f"❌ Failed to import db: {e}", exc_info=True)
    raise

app = Flask(__name__,template_folder="templates")
logger.info("✅ Flask app created")
filepath = ""
# Configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
@app.route('/')
def index():
    """Serve the main HTML page"""
    # In production, serve your HTML file here
    return render_template("index.html")

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
    global filepath
    """Handle image upload and trigger AI processing"""
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            db.create_table()
            
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

logger.info("✅ Application initialization complete!")
# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 8000))
#     print(f"🚀 Starting Flask on port {port}")
#     print(f"📍 Binding to 0.0.0.0:{port}")
#     app.run(host='0.0.0.0', port=port, debug=False, threaded=True)