import os
from cvzone.HandTrackingModule import HandDetector
import cv2
from flask import Flask, render_template, Response, jsonify, request
import json
import stripe

app = Flask(__name__)
stripe.api_key = 'YOUR KEY'

cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)

modeType = 0
selections = ["blackcoffee", "latte", "espresso", "coffee", "cappuccino"]

@app.route('/get_coffee_details', methods=['GET'])
def get_coffee_details():
    coffee_type = request.args.get('coffeeType')
    print(coffee_type)
    coffee_details = {
        "blackcoffee": {
            "name": "Black Coffee",
            "price": 1000,
            "description": "A strong and bold coffee without any additives.",
        },
        "latte": {
            "name": "Latte",
            "price": 1200,
            "description": "Espresso with steamed milk and a small amount of milk foam.",
        },
        "espresso": {
            "name": "Espresso",
            "price": 800,
            "description": "Espresso with steamed milk and a small amount of milk foam.",
        },
        "coffee": {
            "name": "Coffee",
            "price": 500,
            "description": "Espresso with steamed milk and a small amount of milk foam.",
        },
        "cappuccino": {
            "name": "Cappuccino",
            "price": 900,
            "description": "Espresso with steamed milk and a small amount of milk foam.",
        },
    }

    if coffee_type in coffee_details:
        return jsonify(coffee_details[coffee_type])
    else:
        return jsonify({"error": "Coffee details not found for this type."})

@app.route('/payment', methods=['POST', 'GET'])
def payment():
    global modeType
    coffeeType = request.args.get('coffeeType')

    modeType = request.args.get('modeType')
    # print(coffeeType, modeType)
    price_mapping = {
        "blackcoffee": 1000,  
        "latte": 1200,
        "espresso": 800,
        "coffee": 500,
        "cappuccino": 1100,
    }

    if coffeeType in price_mapping:
        amount = price_mapping[coffeeType]
        print(coffeeType, amount)

    else:
        return jsonify({'error': 'Invalid coffeeType'})

    try:
        # Create a Stripe Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
        )
        print('HERE')
        return render_template('payment.html', coffeeType=coffeeType, clientSecret=intent.client_secret, modeType=modeType)
    except stripe.error.StripeError as e:
        return jsonify({'error': e.user_message})

    

@app.route('/get_mode_type')
def get_mode_type():
    global modeType
    if modeType == -1:
        modeType = None
    mode_type = selections[modeType]
    image_url = f"/static/images/{mode_type.lower().replace(' ', '-')}.jpeg" 
    return jsonify(modeType=mode_type, imageURL=image_url)

@app.route('/')
def index():
    image_dir = 'static/images'  # Change this to your image directory
    image_list = os.listdir(image_dir)
    # selections_json = json.dumps(selections)
    return render_template('test.html', image_list=image_list, selections=selections, modeType=modeType)

def get_image_selection(fingers):
    global modeType
    if fingers == [0, 1, 0, 0, 0]:
        modeType = 0  # One fingers, select the first image
    elif fingers == [0, 1, 1, 0, 0]:
        modeType = 1  # Two fingers, select the second image
    elif fingers == [0, 1, 1, 1, 0]:
        modeType = 2  # Three fingers, select the third image
    elif fingers == [0, 1, 1, 1, 1]:
        modeType = 3  # Four fingers, select the fourth image
    elif fingers == [1, 1, 1, 1, 1]:
        modeType = 4  # Five fingers, select the fifth image
    else:
        modeType = -1  # Default value if no mapping is found

    return modeType

def gen_frames():
    detector = HandDetector(detectionCon=0.8, maxHands=1)
    while True:
        success, img = cap.read()
        hands, img = detector.findHands(img)

        if hands:
            hand1 = hands[0]
            fingers1 = detector.fingersUp(hand1)
            print(fingers1)

            selected_image = get_image_selection(fingers1)

            if selected_image != -1:
                print('_________________________')
                # Handle selected image logic here, e.g., change modeType
                modeType = selected_image
                print(modeType)
        else:
     
            modeType = -1   
            print(modeType)

        _, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
