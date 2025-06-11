document.addEventListener('DOMContentLoaded', () => {
    // access the configuration data passed from the HTML template
    const { TILE_MAP, GOAL_STATE } = window.PUZZLE_CONFIG;

    // element selectors
    const puzzleGrid = document.getElementById('puzzle-grid');
    const shuffleButton = document.getElementById('shuffle-button');
    const winMessage = document.getElementById('win-message');
    const statusMessage = document.getElementById('status-message');
    
    // all three solver buttons
    const aStarButton = document.getElementById('a-star-button');
    const bfsButton = document.getElementById('bfs-button');
    const dfsButton = document.getElementById('dfs-button');
    
    let currentGameState = null;

    function renderBoard(state) {
        puzzleGrid.innerHTML = '';
        currentGameState = state;
        winMessage.style.display = 'none';

        state.flat().forEach(tileValue => {
            const tile = document.createElement('div');
            tile.classList.add('puzzle-tile');
            
            if (tileValue === 0) {
                tile.classList.add('empty');
            } else {
                const tileImageUrl = TILE_MAP[tileValue];
                if (tileImageUrl) {
                    tile.style.backgroundImage = `url(/static/${tileImageUrl})`;
                }
            }
            puzzleGrid.appendChild(tile);
        });

        if (JSON.stringify(state) === JSON.stringify(GOAL_STATE)) {
            winMessage.style.display = 'block';
        }
    }

    async function shuffleBoard() {
        hideStatus();
        try {
            const response = await fetch('/api/shuffle', { method: 'POST' });
            if (!response.ok) throw new Error('Failed to shuffle');
            const data = await response.json();
            renderBoard(data.gameState);
        } catch (error) {
            console.error('Shuffle error:', error);
            showStatus('Could not shuffle the board.', 'error');
        }
    }

    async function handleKeyPress(e) {
        const validKeys = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'];
        if (!validKeys.includes(e.key) || JSON.stringify(currentGameState) === JSON.stringify(GOAL_STATE)) {
            return; // also stop moves if the puzzle is already solved
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
        aStarButton.disabled = !enabled;
        bfsButton.disabled = !enabled;
        dfsButton.disabled = !enabled;
        
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

    function animateSolution(path, algorithm) {
        let step = 0;
        const totalSteps = path.length - 1;
        showStatus(`Solution found with ${algorithm} in ${totalSteps} steps. Playing animation...`);

        const interval = setInterval(() => {
            if (step < path.length) {
                renderBoard(path[step]);
                step++;
            } else {
                clearInterval(interval);
                setControlsEnabled(true);
            }
        }, 400);
    }

    async function solveBoard(algorithm) {
        setControlsEnabled(false);
        const algoName = algorithm.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        showStatus(`Solving with ${algoName}... Please wait.`);
        winMessage.style.display = 'none';

        try {
            const response = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // sends the chosen algorithm to the backend
                body: JSON.stringify({ algorithm: algorithm })
            });

            const data = await response.json();

            if (response.ok && data.solution) {
                animateSolution(data.solution, algoName);
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
    
    // listeners for each solve button
    aStarButton.addEventListener('click', () => solveBoard('a_star'));
    bfsButton.addEventListener('click', () => solveBoard('bfs'));
    dfsButton.addEventListener('click', () => solveBoard('dfs'));
    
    document.addEventListener('keydown', handleKeyPress);

    // initial shuffle
    shuffleBoard();
});