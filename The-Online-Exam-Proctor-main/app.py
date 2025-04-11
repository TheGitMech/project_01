import math
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request, jsonify, session,redirect,url_for,Response,flash
import os
import MySQLdb
import MySQLdb.cursors
import json
import io
import numpy as np
from enum import Enum
import warnings
import threading
import utils
import random
import time
import cv2
import keyboard
from config import MYSQL_CONFIG, SECRET_KEY, AUTH_TABLE, AUTH_USERNAME_FIELD, AUTH_PASSWORD_FIELD
from datetime import datetime

#variables
studentInfo=None
camera=None
profileName=None
db = None

#Flak's Application Confguration
warnings.filterwarnings("ignore")
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = SECRET_KEY
# app.config["MONGO_URI"] = "mongodb://localhost:27017/"
os.path.dirname("../templates")

def get_db():
    global db
    if db is None:
        try:
            db = MySQLdb.connect(
                host=MYSQL_CONFIG['HOST'],
                user=MYSQL_CONFIG['USER'],
                passwd=MYSQL_CONFIG['PASSWORD'],
                db=MYSQL_CONFIG['DB'],
                port=int(MYSQL_CONFIG['PORT']),
                charset=MYSQL_CONFIG['charset'],
                init_command=MYSQL_CONFIG['init_command'],
                cursorclass=MYSQL_CONFIG['CURSORCLASS']
            )
            print("MySQL connection successful!")
        except Exception as e:
            print(f"MySQL connection failed: {e}")
            return None
    return db

executor = ThreadPoolExecutor(max_workers=4)

@app.before_request
def before_request():
    global db
    try:
        db = get_db()
        if db:
            db.ping(True)  # Reconnect if connection was lost
    except Exception as e:
        print(f"Database connection error: {e}")
        db = None

@app.teardown_request
def teardown_request(exception):
    if db:
        try:
            db.commit()  # Commit any pending transactions
        except:
            db.rollback()  # Rollback on error

# Function to initialize camera
def init_camera():
    global camera
    try:
        # Release previous camera instance if exists and is open
        if camera is not None and camera.isOpened():
            print("Releasing existing camera instance...")
            camera.release()
        camera = None # Ensure it's reset
            
        # Simplified backend list - Try DSHOW first, then default
        backends_to_try = [
    cv2.CAP_DSHOW,  # Try DirectShow first (often more stable on Windows)
    cv2.CAP_MSMF,   # Try Microsoft Media Foundation next
    cv2.CAP_ANY     # Default backend as fallback
]
        
        for backend in backends_to_try:
            try:
                print(f"Attempting to initialize camera with backend ID: {backend}")
                camera = cv2.VideoCapture(0, backend)
                
                if not camera.isOpened():
                    print(f"Failed to open camera with backend {backend}")
                    if camera is not None: camera.release() # Release if failed
                    camera = None
                    continue # Try next backend
                
                # Basic check: Try to read one frame immediately after opening
                ret, frame = camera.read()
                if ret and frame is not None and frame.size > 0:
                    print(f"Successfully opened and captured initial frame with backend {backend}")
                    # Optionally set properties *after* successful open
                    # camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    return camera # Success!
                else:
                    print(f"Opened camera with backend {backend}, but failed initial frame read.")
                    camera.release() # Release if initial read failed
                    camera = None
                    continue # Try next backend
                    
            except Exception as e:
                print(f"Exception trying backend {backend}: {str(e)}")
                if camera is not None: camera.release()
                camera = None
                continue # Try next backend
                
        # If all backends failed
        print("Failed to initialize camera with any backend.")
        return None
        
    except Exception as e:
        print(f"Outer Camera initialization failed: {str(e)}")
        if camera is not None: camera.release()
        camera = None
        return None

#Function to run Cheat Detection when we start run the Application
# @app.before_request # <<< COMMENTING THIS OUT
def start_loop():
    task1 = executor.submit(utils.cheat_Detection2)
    task2 = executor.submit(utils.cheat_Detection1)
    task3 = executor.submit(utils.fr.run_recognition)
    task4 = executor.submit(utils.a.record)


#Login Related
@app.route('/')
def main():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    global studentInfo
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if not db:
            flash('Database connection error', category='error')
            return redirect(url_for('main'))
            
        cur = db.cursor()
        try:
            # Query Django's user table
            cur.execute(f"SELECT id, first_name, {AUTH_USERNAME_FIELD}, {AUTH_PASSWORD_FIELD} FROM {AUTH_TABLE} WHERE {AUTH_USERNAME_FIELD}=%s", (username,))
            data = cur.fetchone()
            
            if data is None:
                flash('Your Email or Password is incorrect, try again.', category='error')
                return redirect(url_for('main'))
            else:
                # Note: In a production environment, you should use Django's password hasher
                id, name, email, password = data['id'], data['first_name'], data[AUTH_USERNAME_FIELD], data[AUTH_PASSWORD_FIELD]
                studentInfo = {
                    "Id": id,
                    "Name": name or email.split('@')[0],  # Use email username if name is not set
                    "Email": email,
                    "Password": password
                }
                
                # Store user info in session
                session['user_id'] = id
                session['username'] = name or email.split('@')[0]
                session['email'] = email
                
                # Check if user is staff/admin
                cur.execute(f"SELECT is_staff FROM {AUTH_TABLE} WHERE id=%s", (id,))
                is_staff = cur.fetchone()['is_staff']
                
                if is_staff:
                    return redirect(url_for('adminStudents'))
                else:
                    utils.Student_Name = name or email.split('@')[0]
                    return redirect(url_for('rules'))
        finally:
            cur.close()

@app.route('/logout')
def logout():
    return render_template('login.html')

#Student Related
@app.route('/rules')
def rules():
    return render_template('ExamRules.html')

@app.route('/faceInput')
def faceInput():
    return render_template('ExamFaceInput.html')

@app.route('/video_capture')
def video_capture():
    try:
        global camera
        if camera is None or not camera.isOpened():
            print("Initial camera check failed, attempting init...")
            camera = init_camera()
            if camera is None:
                print("Initial camera init failed.")
                return "Camera not available", 500
            else:
                print("Initial camera init successful.")
        
        def generate_frames():
            consecutive_failures = 0
            max_failures = 5 # Try re-initializing after 5 failures
            
            while True:
                global camera # Ensure we're using the global camera object
                try:
                    # Check if camera object exists and is opened
                    if camera is None or not camera.isOpened():
                        print("Stream loop: Camera not open or None, attempting re-initialization...")
                        camera = init_camera()
                        if camera is None or not camera.isOpened():
                            print("Stream loop: Re-initialization failed, stopping stream.")
                            break # Stop if re-init fails
                        else:
                            consecutive_failures = 0 # Reset failures after successful re-init
                            print("Stream loop: Camera re-initialized successfully.")
                            # No need to continue here, proceed to read

                    # Try to read frame
                    ret, frame = camera.read()
                    
                    if ret and frame is not None and frame.size > 0:
                        consecutive_failures = 0 # Reset failures on success
                        # --- Frame processing starts here ---
                        # Load cascade classifier
                        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                        if not os.path.exists(cascade_path):
                            print(f"Cascade file not found at {cascade_path}")
                            # Optionally draw an error on the frame
                        else:
                            face_cascade = cv2.CascadeClassifier(cascade_path)
                            if face_cascade.empty():
                                print("Failed to load cascade classifier")
                                # Optionally draw an error on the frame
                            else:
                                # Convert to grayscale
                                try:
                                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                    gray = cv2.equalizeHist(gray)
                                except Exception as e:
                                    print(f"Color conversion error: {str(e)}")
                                    gray = None # Handle error gracefully

                                if gray is not None:
                                    # Detect faces
                                    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                                    
                                    # Draw rectangles and text
                                    try:
                                        for (x, y, w, h) in faces:
                                            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                                            
                                        if len(faces) > 0:
                                            cv2.putText(frame, 'Face Detected', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                                        else:
                                            cv2.putText(frame, 'No Face Detected', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                                    except Exception as e:
                                        print(f"Drawing error: {str(e)}")

                        # Encode frame to JPEG
                        try:
                            ret_encode, buffer = cv2.imencode('.jpg', frame)
                            if not ret_encode:
                                print("Failed to encode frame")
                                continue # Skip this frame
                                
                            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                        except Exception as e:
                            print(f"Frame encoding error: {str(e)}")
                            continue # Skip this frame
                        # --- Frame processing ends here ---

                    else: # Frame read failed
                        consecutive_failures += 1
                        print(f"Failed to capture frame (Attempt {consecutive_failures}/{max_failures})")
                        
                        if consecutive_failures >= max_failures:
                            print(f"Max consecutive failures reached. Attempting camera re-initialization.")
                            # Release the old camera explicitly before re-initializing
                            if camera is not None:
                                camera.release()
                                camera = None
                            camera = init_camera() # Try to re-initialize
                            if camera is None or not camera.isOpened():
                                print("Re-initialization failed after max failures, stopping stream.")
                                break # Stop if re-init fails
                            else:
                                print("Camera re-initialized successfully after max failures.")
                                consecutive_failures = 0 # Reset counter
                        
                        time.sleep(0.2) # Delay before next attempt
                        continue # Try again in the next loop iteration
                           
                except Exception as e:
                    print(f"Frame processing loop error: {str(e)}")
                    consecutive_failures += 1 # Count generic errors too
                    if consecutive_failures >= max_failures:
                         print(f"Max consecutive failures reached due to processing error. Stopping stream.")
                         break # Stop if errors persist
                    time.sleep(0.5)  # Add longer delay before retrying on general error
                    continue  # Try again
                    
        return Response(generate_frames(),
                       mimetype='multipart/x-mixed-replace; boundary=frame')
                       
    except Exception as e:
        print(f"Video capture route error: {str(e)}")
        # Ensure camera is released if route fails badly
        if camera is not None:
            camera.release()
            camera = None
        return str(e), 500

@app.route('/saveFaceInput')
def saveFaceInput():
    global camera, studentInfo, profileName
    try:
        # Check if student info exists
        if not studentInfo or 'Name' not in studentInfo:
            print("No student info found")
            return redirect(url_for('login'))
            
        # Initialize camera if not already initialized
        if camera is None:
            camera = init_camera()
            
        if camera is None:
            print("Failed to initialize camera")
            return "Camera not available", 500
            
        try:
            # Wait a bit for camera to stabilize
            time.sleep(0.5)
            
            # Read multiple frames to ensure we get a good one
            for _ in range(3):
                ret, frame = camera.read()
                if ret and frame is not None:
                    break
                time.sleep(0.1)
                
            if not ret or frame is None:
                print("Failed to capture frame")
                return "Failed to capture image", 500
                
            # Check for face detection
            detector = cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
            if detector is None:
                print("Failed to load face detector")
                return "Failed to load face detector", 500
                
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.2, 6)
            
            if len(faces) == 0:
                print("No face detected in frame")
                return "No face detected. Please ensure your face is visible in the frame.", 400
                
            # Create Profiles directory if it doesn't exist
            if not os.path.exists('static/Profiles'):
                os.makedirs('static/Profiles')
                
            # Generate profile name and save image
            profileName = f"{studentInfo['Name']}_{utils.get_resultId():03}Profile.jpg"
            save_path = os.path.join('static/Profiles', profileName)
            
            # Save the image
            success = cv2.imwrite(save_path, frame)
            if not success:
                print(f"Failed to save image to {save_path}")
                return "Failed to save captured image", 500
                
            print(f"Successfully saved image to {save_path}")
            session['profile_image'] = profileName  # Store in session as backup
            return redirect(url_for('confirmFaceInput'))
            
        finally:
            # Don't release the camera here, we'll need it for the exam
            pass
            
    except Exception as e:
        print(f"Error in saveFaceInput: {str(e)}")
        return str(e), 500

@app.route('/confirmFaceInput')
def confirmFaceInput():
    global profileName
    # Try to get profile name from global variable or session
    profile = profileName or session.get('profile_image')
    if not profile:
        print("No profile image found")
        return redirect(url_for('faceInput'))
        
    # Verify the file exists
    if not os.path.exists(os.path.join('static/Profiles', profile)):
        print(f"Profile image file not found: {profile}")
        return redirect(url_for('faceInput'))
        
    utils.fr.encode_faces()
    return render_template('ExamConfirmFaceInput.html', profile=profile)

@app.route('/systemCheck')
def systemCheck():
    return render_template('ExamSystemCheck.html')

@app.route('/systemCheck', methods=["POST"])
def systemCheckRoute():
    if request.method == 'POST':
        examData = request.json
        output = 'exam'
        if 'Not available' in examData['input'].split(';'): output = 'systemCheckError'
    return jsonify({"output": output})

@app.route('/systemCheckError')
def systemCheckError():
    return render_template('ExamSystemCheckError.html')

@app.route('/exam') # Handles GET request
def exam():
    # Get parameters from URL
    attempt_id = request.args.get('attempt_id')
    user_id = request.args.get('user_id') # Get user_id from args
    username = request.args.get('username')
    email = request.args.get('email')
    exam_id = request.args.get('exam_id')
    exam_name = request.args.get('exam_name')
    course_id = request.args.get('course_id')
    duration_minutes = 30 # Default or fetch from exam_details later if needed

    # Fetch duration from DB if possible
    try:
        if db and exam_id:
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT duration_minutes FROM courses_proctoredexam WHERE id = %s", (exam_id,))
            exam_details = cursor.fetchone()
            if exam_details and exam_details.get('duration_minutes'):
                duration_minutes = exam_details['duration_minutes']
            cursor.close()
    except Exception as e:
        print(f"Error fetching exam duration: {e}")

    # Store in session for later use (e.g., submission)
    session['exam_attempt_id'] = attempt_id
    session['exam_id'] = exam_id
    session['exam_course_id'] = course_id
    session['user_id'] = user_id # <<< STORE user_id IN SESSION HERE

    print(f"GET /exam: Stored in session - attempt={attempt_id}, exam={exam_id}, user={user_id}") # Debug log

    # Pass data to the exam template
    return render_template('Exam.html',
                           exam_title=exam_name,
                           attempt_id=attempt_id,
                           user_id=user_id,
                           username=username,
                           email=email,
                           exam_id=exam_id,
                           course_id=course_id,
                           duration=duration_minutes)

@app.route('/api/questions')
def get_questions():
    exam_id = request.args.get('exam_id')
    if not exam_id:
        return jsonify({'error': 'exam_id is required'}), 400
        
    if not db:
        return jsonify({'error': 'Database connection error'}), 500
        
    cur = db.cursor()
    try:
        # Get exam details first
        cur.execute("""
            SELECT title, duration_minutes, passing_score 
            FROM courses_proctoredexam 
            WHERE id = %s
        """, (exam_id,))
        exam = cur.fetchone()
        
        if not exam:
            return jsonify({'error': 'Exam not found'}), 404
            
        # Get questions for this exam with simplified answers
        cur.execute("""
            SELECT 
                id,
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                CASE 
                    WHEN option_a = correct_answer THEN 'a'
                    WHEN option_b = correct_answer THEN 'b'
                    WHEN option_c = correct_answer THEN 'c'
                    WHEN option_d = correct_answer THEN 'd'
                END as correct_answer
            FROM courses_examquestion 
            WHERE exam_id = %s
            ORDER BY RAND()
            LIMIT 10
        """, (exam_id,))
        questions = cur.fetchall()
        
        return jsonify({
            'exam': {
                'title': exam['title'],
                'duration_minutes': exam['duration_minutes'],
                'passing_score': exam['passing_score']
            },
            'questions': questions
        })
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return jsonify({'error': 'Failed to fetch questions'}), 500
    finally:
        cur.close()

@app.route('/exam', methods=['POST']) # Handles POST request
def examAction():
    if request.method == 'POST':
        try:
            if not db:
                return jsonify({'success': False, 'message': 'Database connection error'}), 500
            
            cursor = db.cursor(MySQLdb.cursors.DictCursor)
            
            data = request.get_json()
            if not data:
                 data_str = request.form.get('input')
                 if not data_str:
                     return jsonify({'success': False, 'message': 'Missing submission data'}), 400
                 data = json.loads(data_str)
                
            user_answers = data.get('answers', [])
            # Prioritize IDs from session as they are more reliable than JS payload
            exam_id = session.get('exam_id')
            attempt_id = session.get('exam_attempt_id')
            user_id = session.get('user_id') 

            # Basic check - might need refinement based on logging
            if user_answers is None or not exam_id or not attempt_id or not user_id:
                 print(f"Backend Check - Missing data: answers={user_answers is not None}, exam_id={exam_id}, attempt_id={attempt_id}, user_id={user_id}")
                 # Also log what was received from JS if available
                 print(f"Data received from JS: exam_id={data.get('exam_id')}, attempt_id={data.get('attempt_id')}, user_id={data.get('user_id')}")
                 return jsonify({'success': False, 'message': 'Incomplete submission data (Backend Check)'}), 400

            # Fetch exam details (passing score)
            cursor.execute("SELECT passing_score, duration_minutes FROM courses_proctoredexam WHERE id = %s", (exam_id,))
            exam_details = cursor.fetchone()
            if not exam_details:
                return jsonify({'success': False, 'message': 'Exam details not found'}), 404
            passing_score = exam_details.get('passing_score', 40) # Default passing score
            duration_minutes = exam_details.get('duration_minutes')

            # Fetch correct answers for the exam
            cursor.execute("SELECT id, correct_answer FROM courses_examquestion WHERE exam_id = %s ORDER BY id", (exam_id,))
            correct_answers_data = cursor.fetchall()
            
            if not correct_answers_data:
                return jsonify({'success': False, 'message': 'Could not retrieve correct answers for this exam'}), 500

            correct_answers = {row['id']: row['correct_answer'] for row in correct_answers_data}
            total_questions = len(correct_answers_data)
            
            # Calculate score
            score = 0
            if len(user_answers) == total_questions:
                question_ids = sorted(correct_answers.keys())
                for i in range(total_questions):
                    question_id = question_ids[i]
                    if user_answers[i] and str(user_answers[i]).lower() == str(correct_answers[question_id]).lower():
                        score += 1
            else:
                print(f"Warning: Number of user answers ({len(user_answers)}) does not match total questions ({total_questions})")
                # Attempt partial scoring if lengths mismatch but answers are somewhat aligned (less reliable)
                question_ids = sorted(correct_answers.keys())
                for i in range(min(len(user_answers), total_questions)):
                     question_id = question_ids[i]
                     if user_answers[i] and str(user_answers[i]).lower() == str(correct_answers[question_id]).lower():
                         score += 1

            score_percentage = round((score / total_questions) * 100) if total_questions > 0 else 0
            passed = score_percentage >= passing_score

            # Save results to Django's ExamAttempt model
            # Construct the SQL query carefully
            update_sql = """
                UPDATE courses_examattempt 
                SET score = %s,        # The raw score (number correct)
                    status = %s, 
                    end_time = %s      # Use end_time field
                WHERE id = %s AND user_id = %s
            """
            current_time = datetime.now()
            attempt_status = 'COMPLETED'
            
            try:
                cursor.execute(update_sql, (
                    score,          # Pass the raw score (number correct)
                    attempt_status, 
                    current_time,   # Set end_time
                    attempt_id,
                    user_id
                ))
                db.commit()
                print(f"Attempt {attempt_id} updated successfully. Score: {score}/{total_questions} ({score_percentage}%), Passed: {passed}")
            except Exception as db_error:
                db.rollback()
                print(f"Database error updating attempt {attempt_id}: {db_error}")
                return jsonify({'success': False, 'message': 'Failed to save exam results'}), 500
            finally:
                 cursor.close()

            # Prepare result status for redirection (still need calculated values here)
            result_status_data = json.dumps({
                'score': score_percentage,
                'passed': passed,
                'correct': score,
                'total': total_questions,
                'passing': passing_score
            })

            # Determine redirect URL based on calculated pass/fail, even if not stored in DB
            redirect_url = url_for('showResultPass' if passed else 'showResultFail', result_status=result_status_data)
            return jsonify({'success': True, 'redirect_url': redirect_url})

        except json.JSONDecodeError:
            return jsonify({'success': False, 'message': 'Invalid submission format'}), 400
        except Exception as e:
            print(f"Error processing exam submission: {e}") # Log the actual error
            # Optionally rollback transaction if cursor exists and an error occurred before commit
            try:
                if 'cursor' in locals() and cursor:
                    db.rollback()
                    cursor.close()
            except Exception as cleanup_error:
                print(f"Error during cleanup: {cleanup_error}")
                
            return jsonify({
                "message": "You did not follow the rules.",
                "score": score,
                "passed": passed,
                "correct": score,
                "total": total_questions,
                "passing": passing_score
            }), 500
            
    # Handle GET request for /exam (just render template)
    # ... (existing GET handling code remains unchanged) ...

@app.route('/showResultPass/<result_status>')
def showResultPass(result_status):
    return render_template('ExamResultPass.html',result_status=result_status)

@app.route('/showResultFail/<result_status>')
def showResultFail(result_status):
    return render_template('ExamResultFail.html',result_status=result_status)

#Admin Related
@app.route('/adminResults')
def adminResults():
    results = utils.getResults()
    return render_template('Results.html', results=results)

@app.route('/adminResultDetails/<resultId>')
def adminResultDetails(resultId):
    result_Details = utils.getResultDetails(resultId)
    return render_template('ResultDetails.html', resultDetials=result_Details)

@app.route('/adminResultDetailsVideo/<videoInfo>')
def adminResultDetailsVideo(videoInfo):
    return render_template('ResultDetailsVideo.html', videoInfo= videoInfo)

@app.route('/adminStudents')
def adminStudents():
    cur = db.cursor()
    # Query Django's accounts_user table for non-staff users
    cur.execute(f"SELECT id, username, first_name, last_name, email, is_active FROM {AUTH_TABLE} WHERE is_staff=0")
    data = cur.fetchall()
    cur.close()
    return render_template('Students.html', students=data)

@app.route('/insertStudent', methods=['POST'])
def insertStudent():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']  # In production, this should be hashed
        first_name = request.form['username']  # Using username as first_name for now
        
        cur = db.cursor()
        # Insert into Django's accounts_user table
        cur.execute(f"""
            INSERT INTO {AUTH_TABLE} 
            (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) 
            VALUES (%s, 0, %s, %s, '', %s, 0, 1, NOW())
        """, (password, username, first_name, email))
        db.commit()
        cur.close()
        return redirect(url_for('adminStudents'))

@app.route('/deleteStudent/<string:stdId>', methods=['GET'])
def deleteStudent(stdId):
    cur = db.cursor()
    # Delete from Django's accounts_user table
    cur.execute(f"DELETE FROM {AUTH_TABLE} WHERE id=%s AND is_staff=0", (stdId,))
    db.commit()
    cur.close()
    flash("Record Has Been Deleted Successfully")
    return redirect(url_for('adminStudents'))

@app.route('/updateStudent', methods=['POST', 'GET'])
def updateStudent():
    if request.method == 'POST':
        id_data = request.form['id']
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        cur = db.cursor()
        # Update Django's accounts_user table
        cur.execute(f"""
            UPDATE {AUTH_TABLE}
            SET username=%s, first_name=%s, email=%s, password=%s
            WHERE id=%s AND is_staff=0
        """, (username, username, email, password, id_data))
        db.commit()
        cur.close()
        return redirect(url_for('adminStudents'))

if __name__ == '__main__':
    app.run(debug=True)