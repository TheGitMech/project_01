// DOM Elements
const startButton = document.getElementById('startButton');
const timerDisplay = document.getElementById('time');
const mainContent = document.getElementById('mainContent');
const quizContent = document.getElementById('quizContent');
const questionText = document.getElementById('questionText');
const optionsContainer = document.getElementById('options');
const completeTest = document.getElementById('completeTest');

// Global variables
let questions = [];
let currentQuestionIndex = 0;
let answers = [];
let examTimer;
let timeLeft;

// Get URL parameters
const urlParams = new URLSearchParams(window.location.search);
const examId = urlParams.get('exam_id');
const attemptId = urlParams.get('attempt_id');
const userId = urlParams.get('user_id'); // Read userId globally

// Initialize exam when start button is clicked
document.getElementById('startButton').addEventListener('click', startExam);

// Function to start the exam
async function startExam() {
    try {
        // Show loading state
        document.getElementById('welcomeScreen').innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="sr-only">Loading...</span>
                </div>
                <h5 class="mt-3">Loading exam questions...</h5>
            </div>
        `;
        
        // Fetch questions from API
        const response = await fetch(`/api/questions?exam_id=${examId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch questions');
        }
        
        const data = await response.json();
        if (!data.questions || data.questions.length === 0) {
            throw new Error('No questions available for this exam');
        }
        
        // Initialize exam data
        questions = data.questions;
        answers = new Array(questions.length).fill(null);
        timeLeft = data.exam.duration_minutes * 60; // Convert to seconds
        
        // Hide welcome screen and show quiz
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('quizContent').style.display = 'block';
        
        // Initialize question progress dots
        initializeQuestionProgress();
        
        // Show first question
        showQuestion(0);
        
        // Start timer
        startTimer();
        
    } catch (error) {
        console.error('Error starting exam:', error);
        document.getElementById('welcomeScreen').innerHTML = `
            <div class="alert alert-danger">
                <h5>Error Loading Exam</h5>
                <p>${error.message}</p>
                <button onclick="location.reload()" class="btn btn-primary mt-3">Try Again</button>
            </div>
        `;
    }
}

// Function to initialize question progress dots
function initializeQuestionProgress() {
    const progressContainer = document.getElementById('questionProgress');
    progressContainer.innerHTML = '';
    
    for (let i = 0; i < questions.length; i++) {
        const dot = document.createElement('div');
        dot.className = 'question-dot';
        dot.textContent = i + 1;
        dot.onclick = () => showQuestion(i);
        progressContainer.appendChild(dot);
    }
}

// Function to show a question
function showQuestion(index) {
    if (index < 0 || index >= questions.length) return;
    
    currentQuestionIndex = index;
    const question = questions[index];
    
    // Update question number and text
    document.getElementById('questionNumber').textContent = `Question ${index + 1} of ${questions.length}`;
    document.getElementById('questionText').textContent = question.question_text;
    
    // Create option buttons
    const optionsContainer = document.getElementById('options');
    optionsContainer.innerHTML = '';
    
    const options = [
        { key: 'a', text: question.option_a },
        { key: 'b', text: question.option_b },
        { key: 'c', text: question.option_c },
        { key: 'd', text: question.option_d }
    ];
    
    options.forEach(option => {
        const button = document.createElement('button');
        button.className = 'option-btn';
        if (answers[index] === option.key) {
            button.classList.add('active');
        }
        button.textContent = `${option.key.toUpperCase()}. ${option.text}`;
        button.onclick = () => selectAnswer(option.key);
        optionsContainer.appendChild(button);
    });
    
    // Update navigation buttons
    updateNavigation();
    
    // Update progress dots
    updateProgress();
}

// Function to select an answer
function selectAnswer(answer) {
    answers[currentQuestionIndex] = answer;
    
    // Update option button styles
    const buttons = document.querySelectorAll('.option-btn');
    buttons.forEach(button => {
        button.classList.remove('active');
        if (button.textContent.startsWith(answer.toUpperCase() + '.')) {
            button.classList.add('active');
        }
    });
    
    // Update progress dots
    updateProgress();
}

// Function to update progress dots
function updateProgress() {
    const dots = document.querySelectorAll('.question-dot');
    dots.forEach((dot, index) => {
        dot.classList.remove('current', 'answered');
        if (index === currentQuestionIndex) {
            dot.classList.add('current');
        }
        if (answers[index] !== null) {
            dot.classList.add('answered');
        }
    });
}

// Function to update navigation buttons
function updateNavigation() {
    const prevButton = document.getElementById('prevButton');
    const nextButton = document.getElementById('nextButton');
    const submitButton = document.getElementById('submitButton');
    
    prevButton.disabled = currentQuestionIndex === 0;
    
    if (currentQuestionIndex === questions.length - 1) {
        nextButton.style.display = 'none';
        submitButton.style.display = 'block';
    } else {
        nextButton.style.display = 'block';
        submitButton.style.display = 'none';
    }
}

// Navigation button event listeners
document.getElementById('prevButton').onclick = () => showQuestion(currentQuestionIndex - 1);
document.getElementById('nextButton').onclick = () => showQuestion(currentQuestionIndex + 1);
document.getElementById('submitButton').onclick = confirmSubmit;

// Function to start the timer
function startTimer() {
    const timerElement = document.getElementById('time');
    
    examTimer = setInterval(() => {
        timeLeft--;
        
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Add warning classes
        const timer = document.getElementById('timer');
        if (timeLeft <= 300) { // Last 5 minutes
            timer.classList.add('danger');
        } else if (timeLeft <= 600) { // Last 10 minutes
            timer.classList.add('warning');
        }
        
        if (timeLeft <= 0) {
            clearInterval(examTimer);
            submitExam();
        }
    }, 1000);
}

// Function to confirm exam submission
function confirmSubmit() {
    const unanswered = answers.filter(ans => ans === null).length;
    let message = 'Are you sure you want to submit your exam?';
    
    if (unanswered > 0) {
        message = `You have ${unanswered} unanswered question(s). Are you sure you want to submit?`;
    }
    
    if (confirm(message)) {
        submitExam();
    }
}

// Function to submit the exam
async function submitExam() {
    // Clear timer
    clearInterval(examTimer);

    // Display submitting state
    const quizContent = document.getElementById('quizContent');
    quizContent.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary mb-3" role="status">
                <span class="sr-only">Submitting...</span>
            </div>
            <h5>Submitting your exam...</h5>
        </div>
    `;

    // REMOVED: const userId = urlParams.get('user_id'); 

    // Prepare submission data - USE GLOBAL userId
    const submissionData = {
        answers: answers,
        exam_id: examId,         // From global scope
        attempt_id: attemptId,   // From global scope
        user_id: userId          // USE GLOBAL userId variable
    };

    // Add a check for missing IDs before fetching
    if (!examId || !attemptId || !userId) {
        console.error("Missing critical IDs for submission:", { examId, attemptId, userId });
        quizContent.innerHTML = `
            <div class="alert alert-danger">
                <h5>Submission Error</h5>
                <p>Could not retrieve necessary exam information (Exam ID, Attempt ID, or User ID). Please reload and try again.</p>
                <button onclick="location.reload()" class="btn btn-primary mt-3">Reload</button>
            </div>
        `;
        return; // Stop submission
    }

    // --> ADD LOGGING HERE <--
    console.log("Submitting Exam Data:", submissionData);

    try {
        const response = await fetch("/exam", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(submissionData) // Send the complete data object
        });

        const data = await response.json();

        // Check if the submission was successful on the backend
        if (response.ok && data.success) {
            // Redirect to the result page URL provided by the backend
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                console.error('Submission successful, but no redirect URL received.');
                quizContent.innerHTML = '<div class="alert alert-warning">Exam submitted, but failed to load results page.</div>';
            }
        } else {
            // Handle backend error
            console.error('Exam submission failed:', data.message || 'Unknown error');
            quizContent.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error Submitting Exam</h5>
                    <p>${data.message || 'Failed to process exam results. Please try again.'}</p>
                    <button onclick="location.reload()" class="btn btn-primary mt-3">Try Again</button>
                </div>
            `;
        }
    } catch (error) {
        // Handle network or other fetch errors
        console.error('Network error during exam submission:', error);
        quizContent.innerHTML = `
            <div class="alert alert-danger">
                <h5>Network Error</h5>
                <p>Could not submit exam. Please check your connection and try again.</p>
                <button onclick="location.reload()" class="btn btn-primary mt-3">Try Again</button>
            </div>
        `;
    }
}



