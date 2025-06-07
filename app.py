# app.py

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from utils.image_processor import slice_image
from puzzle_solver.board import Board
from puzzle_solver.algorithms import a_star_solve

# Configuration
UPLOAD_FOLDER = 'uploads'
TILES_FOLDER = 'static/tiles'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your_very_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# This dictionary will act as our simple in-memory session storage for puzzle states
# In a real app, you might use Flask-Session with a proper backend
puzzle_boards = {}

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'image_file' not in request.files:
            flash('No file part in the request.', 'error')
            return redirect(request.url)
        
        file = request.files['image_file']
        
        if file.filename == '':
            flash('No selected file.', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(image_path)
            
            # --- New Logic ---
            # Create a unique directory for this image's tiles
            image_name_without_ext = os.path.splitext(filename)[0]
            tile_dir = os.path.join(TILES_FOLDER, image_name_without_ext)
            
            # Slice the image and get tile paths
            tile_paths = slice_image(image_path, tile_dir)
            
            if tile_paths is None:
                flash('Could not process the image. Please try another one.', 'error')
                return redirect(request.url)
            
            # Create a new Board instance for this session/image
            board = Board()
            puzzle_boards[filename] = board
            
            # Store tile mapping in session. Keys are tile numbers (1-8).
            session['tile_map'] = {i + 1: path for i, path in enumerate(tile_paths)}
            session['current_puzzle_id'] = filename

            flash(f'Image "{filename}" processed. Let\'s play!', 'success')
            return redirect(url_for('puzzle_page', filename=filename))

        else:
            flash('Invalid file type. Allowed types are png, jpg, jpeg, gif.', 'error')
            return redirect(request.url)
            
    return render_template('index.html')

@app.route('/puzzle/<filename>')
def puzzle_page(filename):
    """Displays the puzzle game page."""
    if filename not in puzzle_boards:
        flash('Puzzle not found. Please upload an image first.', 'error')
        return redirect(url_for('upload_image'))
    
    tile_map = session.get('tile_map', {})
    if not tile_map:
        flash('Tile data is missing. Please re-upload.', 'error')
        return redirect(url_for('upload_image'))

    return render_template('puzzle.html', tile_map=tile_map)

# --- API Endpoints for JavaScript ---

@app.route('/api/shuffle', methods=['POST'])
def shuffle_puzzle():
    puzzle_id = session.get('current_puzzle_id')
    if not puzzle_id or puzzle_id not in puzzle_boards:
        return jsonify({'error': 'No active puzzle found'}), 404
    
    board = puzzle_boards[puzzle_id]
    board.shuffle()
    return jsonify({'gameState': board.state})


@app.route('/api/move', methods=['POST'])
def move_tile():
    data = request.get_json()
    puzzle_id = session.get('current_puzzle_id')

    if not puzzle_id or puzzle_id not in puzzle_boards:
        return jsonify({'error': 'No active puzzle found'}), 404
        
    direction = data.get('direction')
    
    board = puzzle_boards[puzzle_id]
    
    if not direction:
        return jsonify({'error': 'Move direction not provided'}), 400
        
   # --- THIS IS THE MODIFIED LOGIC ---
    # We now map the arrow keys directly to the direction of the blank's movement.
    # 'ArrowUp' from the browser now means the blank moves 'up'.
    move_map = {
        'ArrowUp': 'up',
        'ArrowDown': 'down',
        'ArrowLeft': 'left',
        'ArrowRight': 'right'
    }
    board_direction = move_map.get(direction)
    
    if board_direction and board.move(board_direction):
        return jsonify({'gameState': board.state, 'success': True})
    
    return jsonify({'gameState': board.state, 'success': False, 'message': 'Invalid move'})

@app.route('/api/solve', methods=['POST'])
def solve_puzzle():
    puzzle_id = session.get('current_puzzle_id')
    if not puzzle_id or puzzle_id not in puzzle_boards:
        return jsonify({'error': 'No active puzzle found'}), 404
    
    board = puzzle_boards[puzzle_id]
    
    # Run the A* algorithm
    solution_path = a_star_solve(board)
    
    if solution_path:
        return jsonify({'solution': solution_path})
    else:
        # This will be triggered if the is_solvable() check fails
        return jsonify({'error': 'Puzzle is not solvable or no solution found.'}), 400




if __name__ == '__main__':
    app.run(debug=True)