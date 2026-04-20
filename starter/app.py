from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    try:
        clues = int(request.args.get('clues', 35))
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
        CURRENT['puzzle'] = puzzle
        CURRENT['solution'] = solution
        return jsonify({'puzzle': puzzle})
    except TimeoutError as e:
        return jsonify({'error': str(e)}), 408
    except ValueError:
        return jsonify({'error': 'Invalid clues parameter. Must be an integer.'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to generate puzzle. Please try again.'}), 500

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)