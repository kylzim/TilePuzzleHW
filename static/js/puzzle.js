// static/js/puzzle.js

document.addEventListener('DOMContentLoaded', () => {
    // Access the configuration data passed from the HTML template
    const { TILE_MAP, GOAL_STATE } = window.PUZZLE_CONFIG;

    const puzzleGrid = document.getElementById('puzzle-grid');
    const shuffleButton = document.getElementById('shuffle-button');
    const winMessage = document.getElementById('win-message');
    const solveButton = document.getElementById('solve-button');
    const statusMessage = document.getElementById('status-message');
    
    let currentGameState = null;

    function renderBoard(state) {
        puzzleGrid.innerHTML = ''; // Clear the grid
        currentGameState = state; // Update global state
        winMessage.style.display = 'none';

        state.flat().forEach(tileValue => {
            const tile = document.createElement('div');
            tile.classList.add('puzzle-tile');
            
            if (tileValue === 0) {
                tile.classList.add('empty');
            } else {
                // The URL from the tile_map should be relative to the static folder root
                const tileImageUrl = TILE_MAP[tileValue]; 
                if (tileImageUrl) {
                    // Correctly form the URL for the background image
                    tile.style.backgroundImage = `url(/static/${tileImageUrl})`;
                }
            }
            puzzleGrid.appendChild(tile);
        });

        // Check for win condition
        if (JSON.stringify(state) === JSON.stringify(GOAL_STATE)) {
            winMessage.style.display = 'block';
        }
    }

    // The rest of your functions (shuffleBoard, handleKeyPress) remain exactly the same.
    // ...
    // ...

    async function shuffleBoard() {
        try {
            const response = await fetch('/api/shuffle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });
            if (!response.ok) throw new Error('Failed to shuffle');
            const data = await response.json();
            renderBoard(data.gameState);
        } catch (error) {
            console.error('Shuffle error:', error);
            alert('Could not shuffle the board. Please try again.');
        }
    }

    async function handleKeyPress(e) {
        // This function doesn't need any changes.
        const validKeys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'];
        if (!validKeys.includes(e.key) || JSON.stringify(currentGameState) === JSON.stringify(GOAL_STATE)) {
            return; // Also stop moves if the puzzle is already solved
        }
        e.preventDefault();

        try {
            const response = await fetch('/api/move', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ direction: e.key })
            });
            if (!response.ok) throw new Error('Move failed');

            const data = await response.json();
            if (data.success) {
                renderBoard(data.gameState);
            }
        } catch (error) {
            console.error('Move error:', error);
        }
    }

    function setControlsEnabled(enabled) {
        shuffleButton.disabled = !enabled;
        solveButton.disabled = !enabled;
        if (enabled) {
            document.addEventListener('keydown', handleKeyPress);
        } else {
            document.removeEventListener('keydown', handleKeyPress);
        }
    }

    function showStatus(message, type = 'info') {
        statusMessage.textContent = message;
        statusMessage.className = `flash ${type}`;
        statusMessage.style.display = 'block';
    }

    function hideStatus() {
        statusMessage.style.display = 'none';
    }

    function animateSolution(path) {
        let step = 0;
        const interval = setInterval(() => {
            if (step < path.length) {
                showStatus(`Solving... Step ${step + 1} of ${path.length}`);
                renderBoard(path[step]);
                step++;
            } else {
                clearInterval(interval);
                hideStatus();
                // The final board state will trigger the win message in renderBoard
                setControlsEnabled(true);
            }
        }, 500); // 500ms delay between steps
    }

    async function solveBoard() {
        setControlsEnabled(false);
        showStatus('Solving... Please wait. This may take a moment.');
        winMessage.style.display = 'none';

        try {
            const response = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });

            const data = await response.json();

            if (response.ok && data.solution) {
                animateSolution(data.solution);
            } else {
                showStatus(data.error || 'Failed to find a solution.', 'error');
                setControlsEnabled(true);
            }

        } catch (error) {
            console.error('Solve error:', error);
            showStatus('An error occurred while contacting the server.', 'error');
            setControlsEnabled(true);
        }
    }

    shuffleButton.addEventListener('click', () => {
        hideStatus();
        shuffleBoard();
    });
    solveButton.addEventListener('click', solveBoard); // Add new listener
    
    document.addEventListener('keydown', handleKeyPress);

    // Initial shuffle to start the game
    shuffleBoard();
});