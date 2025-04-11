-- Create questions table if it doesn't exist
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT check_correct_answer CHECK (correct_answer IN ('a', 'b', 'c', 'd'))
);

-- Create exam_results table if it doesn't exist
CREATE TABLE IF NOT EXISTS exam_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL,
    exam_id INT NOT NULL,
    attempt_id INT NOT NULL,
    score INT NOT NULL,
    status VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample questions for exam_id 1 (C Programming Final Exam)
INSERT INTO questions (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer) VALUES
(1, 'What is the purpose of break statement in C?', 'To continue with next iteration', 'To exit from program', 'To skip the current iteration', 'To terminate the loop or switch statement', 'd'),
(1, 'Which of the following is not a valid variable name in C?', 'my_var', '_myvar', '2myvar', 'myVar', 'c'),
(1, 'What is the size of int data type in C?', '2 bytes', '4 bytes', 'Depends on compiler/architecture', '8 bytes', 'c'),
(1, 'Which operator is used for pointer declaration in C?', '&', '*', '#', '@', 'b'),
(1, 'What is the correct way to declare a constant in C?', 'constant int x = 5', 'const int x = 5', '#constant x = 5', 'let const x = 5', 'b'),
(1, 'Which header file should be included to use malloc() function?', 'memory.h', 'stdlib.h', 'string.h', 'alloc.h', 'b'),
(1, 'What does the sizeof() operator return?', 'Value of variable', 'Address of variable', 'Size of variable in bytes', 'None of above', 'c'),
(1, 'Which of the following is true about static variables in C?', 'They are destroyed when function returns', 'They can be accessed outside function', 'They retain their value between function calls', 'They are stored on stack', 'c'),
(1, 'What is the purpose of void pointer in C?', 'To point to functions', 'To point to any data type', 'To point to void variables', 'To create null pointers', 'b'),
(1, 'Which is the correct way to declare an array in C?', 'array[10] int', 'int array(10)', 'int[10] array', 'int array[10]', 'd'); 