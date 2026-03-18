from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import boto3
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import AWS_REGION, SNS_TOPIC_ARN
import logging
import json
from collections import defaultdict

# Updated: Configure logging for debugging and compliance monitoring
logging.basicConfig(filename='/home/ec2-user/EventMingle/backend/app.log', level=logging.DEBUG)

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
# Updated: Set secret key and session persistence
app.secret_key = "seckey12345"  # Replace with a secure key
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session lifetime

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
sns = boto3.client('sns', region_name=AWS_REGION)

users_table = dynamodb.Table('Users')
events_table = dynamodb.Table('Events')
rsvps_table = dynamodb.Table('RSVPs')
feedback_table = dynamodb.Table('Feedback')
attendance_table = dynamodb.Table('Attendance')  # Updated: Added for attendance tracking
communication_log_table = dynamodb.Table('CommunicationLog')  # Updated: Added for communication oversight

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def index_redirect():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response = users_table.get_item(Key={'email': email})
        user = response.get('Item')
        if user and check_password_hash(user['password'], password):
            # Updated: Set permanent session
            session.permanent = True
            session['email'] = email
            session['role'] = user['role']
            logging.info(f"User {email} logged in successfully")
            if user['role'] == 'attendee':
                return redirect(url_for('attendee_dashboard'))
            elif user['role'] == 'organizer':
                return redirect(url_for('organizer_dashboard'))
            elif user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
        logging.error(f"Failed login attempt for {email}")
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/create_profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        users_table.put_item(
            Item={
                'email': email,
                'name': name,
                'password': password,
                'role': role
            },
            ConditionExpression='attribute_not_exists(email)'
        )
        return redirect(url_for('login'))
    return render_template('create_profile.html')

@app.route('/attendee_dashboard')
def attendee_dashboard():
    if 'email' not in session or session['role'] != 'attendee':
        logging.warning("No email in session or role mismatch, redirecting to login")
        return redirect(url_for('login'))
    events = events_table.scan().get('Items', [])
    logging.debug(f"Loading attendee_dashboard with events: {events}")
    return render_template('attendee_dashboard.html', events=events)

@app.route('/rsvp/<event_id>', methods=['POST'])
def rsvp(event_id):
    if 'email' not in session or session['role'] != 'attendee':
        return redirect(url_for('login'))
    rsvps_table.put_item(
        Item={
            'event_id': event_id,
            'email': session['email'],
            'status': 'confirmed',
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=f"RSVP confirmed for event {event_id} by {session['email']}"
    )
    # Updated: Log communication for admin oversight
    communication_log_table.put_item(
        Item={
            'log_id': str(uuid.uuid4()),
            'type': 'RSVP',
            'event_id': event_id,
            'email': session['email'],
            'timestamp': datetime.utcnow().isoformat(),
            'message': f"RSVP confirmed for event {event_id}"
        }
    )
    return redirect(url_for('attendee_dashboard'))

@app.route('/mark_attendance/<event_id>', methods=['POST'])
def mark_attendance(event_id):
    # Updated: Added functionality for marking attendance
    if 'email' not in session or session['role'] != 'attendee':
        return redirect(url_for('login'))
    attendance_table.put_item(
        Item={
            'event_id': event_id,
            'email': session['email'],
            'status': 'attended',
            'timestamp': datetime.utcnow().isoformat()
        }
    )
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=f"Attendance marked for event {event_id} by {session['email']}"
    )
    # Updated: Log communication for admin oversight
    communication_log_table.put_item(
        Item={
            'log_id': str(uuid.uuid4()),
            'type': 'Attendance',
            'event_id': event_id,
            'email': session['email'],
            'timestamp': datetime.utcnow().isoformat(),
            'message': f"Attendance marked for event {event_id}"
        }
    )
    return redirect(url_for('attendee_dashboard'))

@app.route('/organizer_dashboard', methods=['GET', 'POST'])
def organizer_dashboard():
    if 'email' not in session or session['role'] != 'organizer':
        return redirect(url_for('login'))
    if request.method == 'POST':
        event_id = str(uuid.uuid4())
        events_table.put_item(
            Item={
                'event_id': event_id,
                'title': request.form['title'],
                'description': request.form['description'],
                'date': request.form['date'],
                'organizer': session['email']
            }
        )
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"New event created: {request.form['title']} by {session['email']}"
        )
        # Updated: Log communication for admin oversight
        communication_log_table.put_item(
            Item={
                'log_id': str(uuid.uuid4()),
                'type': 'EventCreation',
                'event_id': event_id,
                'email': session['email'],
                'timestamp': datetime.utcnow().isoformat(),
                'message': f"New event created: {request.form['title']}"
            }
        )
        return redirect(url_for('organizer_dashboard'))
    events = events_table.scan(FilterExpression='organizer = :org', ExpressionAttributeValues={':org': session['email']}).get('Items', [])
    # Updated: Fixed RSVP scan with proper IN clause syntax
    event_ids = [e['event_id'] for e in events] if events else []
    if event_ids:
        rsvps = rsvps_table.scan(
            FilterExpression='event_id IN (' + ', '.join([':id' + str(i) for i in range(len(event_ids))]) + ')',
            ExpressionAttributeValues={f':id{i}': id for i, id in enumerate(event_ids)}
        ).get('Items', [])
    else:
        rsvps = []
    logging.debug(f"RSVP scan result for event_ids {event_ids}: {rsvps}")
    # Updated: Fixed attendance scan with proper IN clause syntax
    if event_ids:
        attendance = attendance_table.scan(
            FilterExpression='event_id IN (' + ', '.join([':id' + str(i) for i in range(len(event_ids))]) + ')',
            ExpressionAttributeValues={f':id{i}': id for i, id in enumerate(event_ids)}
        ).get('Items', [])
    else:
        attendance = []
    logging.debug(f"Attendance scan result for event_ids {event_ids}: {attendance}")
    # Updated: Fixed feedback scan with proper IN clause syntax
    if event_ids:
        feedback = feedback_table.scan(
            FilterExpression='event_id IN (' + ', '.join([':id' + str(i) for i in range(len(event_ids))]) + ')',
            ExpressionAttributeValues={f':id{i}': id for i, id in enumerate(event_ids)}
        ).get('Items', [])
    else:
        feedback = []
    logging.debug(f"Feedback scan result for event_ids {event_ids}: {feedback}")
    return render_template('organizer_dashboard.html', events=events, rsvps=rsvps, attendance=attendance, feedback=feedback)

@app.route('/send_update/<event_id>', methods=['POST'])
def send_update(event_id):
    # Updated: Added functionality to send updates/reminders
    if 'email' not in session or session['role'] != 'organizer':
        return redirect(url_for('login'))
    update_message = request.form['update_message']
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=f"Event {event_id} Update: {update_message} from {session['email']}"
    )
    # Updated: Log communication for admin oversight
    communication_log_table.put_item(
        Item={
            'log_id': str(uuid.uuid4()),
            'type': 'Update',
            'event_id': event_id,
            'email': session['email'],
            'timestamp': datetime.utcnow().isoformat(),
            'message': f"Event {event_id} Update: {update_message}"
        }
    )
    return redirect(url_for('organizer_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'email' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    users = users_table.scan().get('Items', [])
    events = events_table.scan().get('Items', [])
    # Added communication oversight
    communications = communication_log_table.scan().get('Items', [])
    
    # [UPDATE] Enhanced trend analysis
    event_ids = [e['event_id'] for e in events] if events else []
    trends = defaultdict(lambda: {'rsvps': 0, 'attendance': 0, 'feedback': 0})
    
    if event_ids:
        # [UPDATE] RSVP trends by event
        rsvps = rsvps_table.scan(
            FilterExpression='event_id IN (' + ', '.join([':id' + str(i) for i in range(len(event_ids))]) + ')',
            ExpressionAttributeValues={f':id{i}': id for i, id in enumerate(event_ids)}
        ).get('Items', [])
        for rsvp in rsvps:
            trends[rsvp['event_id']]['rsvps'] += 1
        
        # [UPDATE] Attendance trends by event
        attendance = attendance_table.scan(
            FilterExpression='event_id IN (' + ', '.join([':id' + str(i) for i in range(len(event_ids))]) + ')',
            ExpressionAttributeValues={f':id{i}': id for i, id in enumerate(event_ids)}
        ).get('Items', [])
        for att in attendance:
            trends[att['event_id']]['attendance'] += 1
        
        # [UPDATE] Feedback trends by event
        feedback = feedback_table.scan(
            FilterExpression='event_id IN (' + ', '.join([':id' + str(i) for i in range(len(event_ids))]) + ')',
            ExpressionAttributeValues={f':id{i}': id for i, id in enumerate(event_ids)}
        ).get('Items', [])
        for fb in feedback:
            trends[fb['event_id']]['feedback'] += 1
    
    # [UPDATE] Convert defaultdict to regular dict for template
    trends = dict(trends)
    
    # [UPDATE] Total counts for overview
    total_rsvp_count = sum(t['rsvps'] for t in trends.values())
    total_attendance_count = sum(t['attendance'] for t in trends.values())
    total_feedback_count = sum(t['feedback'] for t in trends.values())
    
    return render_template('admin_dashboard.html', users=users, events=events, communications=communications, 
                          trends=trends, total_rsvp_count=total_rsvp_count, 
                          total_attendance_count=total_attendance_count, 
                          total_feedback_count=total_feedback_count)

@app.route('/update_role/<email>', methods=['POST'])
def update_role(email):
    # Updated: Added functionality for managing user roles and permissions
    if 'email' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    new_role = request.form['role']
    users_table.update_item(
        Key={'email': email},
        UpdateExpression='SET #role = :r',  # Correct placeholder for reserved keyword
        ExpressionAttributeNames={'#role': 'role'},  # Maps #role to the actual 'role' attribute
        ExpressionAttributeValues={':r': new_role}
    )
    logging.info(f"Role updated for {email} to {new_role} by {session['email']}")
    return redirect(url_for('admin_dashboard'))

@app.route('/feedback/<event_id>', methods=['GET', 'POST'])
def feedback(event_id):
    # Updated: Changed session check to use 'email' instead of 'user'
    logging.debug(f"Accessing feedback for event {event_id}, session: {session.get('email')}")
    if 'email' not in session:
        logging.warning(f"No email in session for feedback/{event_id}, redirecting to login")
        return redirect(url_for('login'))
    response = events_table.get_item(Key={'event_id': event_id})
    if 'Item' not in response:
        logging.error(f"Event {event_id} not found")
        return render_template('error.html', message='Event not found'), 404
    if request.method == 'POST':
        email = session['email']
        feedback_text = request.form['feedback']
        feedback_table.put_item(Item={
            'event_id': event_id,
            'email': email,
            'feedback': feedback_text,
            'timestamp': datetime.utcnow().isoformat()
        })
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f'New feedback from {email} for event {event_id}: {feedback_text}',
            Subject='New EventMingle Feedback'
        )
        # Updated: Log communication for admin oversight
        communication_log_table.put_item(
            Item={
                'log_id': str(uuid.uuid4()),
                'type': 'Feedback',
                'event_id': event_id,
                'email': email,
                'timestamp': datetime.utcnow().isoformat(),
                'message': f'New feedback from {email} for event {event_id}'
            }
        )
        logging.info(f"Feedback submitted by {email} for event {event_id}")
        return redirect(url_for('attendee_dashboard'))
    return render_template('feedback.html', event_id=event_id)

@app.route('/logout')
def logout():
    logging.info(f"User {session.get('email')} logged out")
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
