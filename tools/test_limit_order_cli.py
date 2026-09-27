#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
T212 Limit Order API Test - CLI Version
Simulates what the GUI would do
"""

import json
import requests
import base64
from datetime import datetime
import sys
import os

# Fix encoding on Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

def test_limit_order():
    """Test limit order API call"""

    # Configuration
    api_key = "40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU"
    api_secret = "iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0"
    base_url = "https://demo.trading212.com/api/v0"

    # Input values
    ticker = "NQSEd_EQ"
    quantity = 0.5777225565048442
    price = 17.326656
    validity = "GOOD_TILL_CANCEL"
    order_type = "BUY"

    print("=" * 100)
    print("T212 LIMIT ORDER API TEST - CLI VERSION")
    print("=" * 100)
    print()

    # Round values
    quantity_rounded = round(quantity, 3)
    price_rounded = round(price, 3)

    # Apply SELL logic if needed
    if order_type == "SELL":
        quantity_final = -abs(quantity_rounded)
    else:
        quantity_final = quantity_rounded

    # Build payload
    payload = {
        "ticker": ticker,
        "quantity": quantity_final,
        "limitPrice": price_rounded,
        "timeValidity": validity
    }

    # Display REQUEST
    print("[REQUEST PAYLOAD]")
    print("-" * 100)
    print()
    print("ORDER DETAILS:")
    print(f"  Order Type:      {order_type}")
    print(f"  Ticker:          {ticker}")
    print(f"  Time Validity:   {validity}")
    print()

    print("QUANTITY ROUNDING:")
    print(f"  Original:        {quantity} ({len(str(quantity).split('.')[1]) if '.' in str(quantity) else 0} decimals)")
    print(f"  Rounded:         {quantity_rounded} (3 decimals)")
    print(f"  Final:           {quantity_final}")
    print()

    print("PRICE ROUNDING:")
    print(f"  Original:        {price} ({len(str(price).split('.')[1]) if '.' in str(price) else 0} decimals)")
    print(f"  Rounded:         {price_rounded} (3 decimals)")
    print()

    print("JSON PAYLOAD:")
    print(json.dumps(payload, indent=2))
    print()

    print("ENDPOINT:")
    print(f"  POST {base_url}/equity/orders/limit")
    print()

    print("AUTHENTICATION:")
    print(f"  Type:            HTTP Basic Auth")
    credentials = f"{api_key}:{api_secret}"
    credentials_b64 = base64.b64encode(credentials.encode()).decode()
    print(f"  Authorization:   Basic {credentials_b64[:50]}...")
    print()

    # Make API call
    print("=" * 100)
    print("MAKING API CALL...")
    print("=" * 100)
    print()

    start_time = datetime.now()

    try:
        auth = (api_key, api_secret)
        headers = {"Content-Type": "application/json"}

        response = requests.post(
            f"{base_url}/equity/orders/limit",
            json=payload,
            auth=auth,
            headers=headers,
            timeout=10
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Display RESPONSE
        print("[RESPONSE] RESPONSE PAYLOAD")
        print("-" * 100)
        print()

        status_icon = "[SUCCESS]" if 200 <= response.status_code < 300 else "[FAILED]"
        print(f"Status Code:     {status_icon} {response.status_code}")
        print(f"Reason:          {response.reason}")
        print(f"Content-Type:    {response.headers.get('Content-Type', 'N/A')}")
        print(f"Response Size:   {len(response.text)} bytes")
        print(f"Duration:        {duration:.3f} seconds")
        print()

        print("RESPONSE BODY:")
        print()

        if response.text:
            try:
                response_json = response.json()
                print(json.dumps(response_json, indent=2))
            except:
                print(response.text)
        else:
            print("(No body)")
        print()

        # Display STATUS
        print("=" * 100)
        print("[STATUS] REQUEST/RESPONSE STATUS")
        print("=" * 100)
        print()

        print(f"[TIME]  Start Time:     {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print(f"[TIME]  End Time:       {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print(f"[DURATION] Duration:       {duration:.3f} seconds")
        print()

        if 200 <= response.status_code < 300:
            print("[OK] SUCCESS (2xx)")
            print()
            print(f"Status Code:     {response.status_code}")
            print(f"Reason:          {response.reason}")
            try:
                order_id = response.json().get('id')
                print(f"Order ID:        {order_id}")
            except:
                pass
        elif 400 <= response.status_code < 500:
            print("[ERROR] CLIENT ERROR (4xx)")
            print()
            print(f"Status Code:     {response.status_code}")
            print(f"Reason:          {response.reason}")
            try:
                error_detail = response.json().get("detail", "No detail")
                error_type = response.json().get("type", "No type")
                print(f"Error Type:      {error_type}")
                print(f"Detail:          {error_detail}")
            except:
                print(f"Response:        {response.text}")
        elif 500 <= response.status_code < 600:
            print("[WARNING]  SERVER ERROR (5xx)")
            print()
            print(f"Status Code:     {response.status_code}")
            print(f"Reason:          {response.reason}")

        print()
        print("RESPONSE HEADERS:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")

        print()
        print("=" * 100)

        if 200 <= response.status_code < 300:
            print("[OK] TEST PASSED - Order created successfully!")
            print("The quantity and price rounding fix is working!")
        elif response.status_code == 400:
            print("[ERROR] TEST FAILED - API returned 400 Bad Request")
            print("Check the error detail above for what needs to be fixed")
        else:
            print(f"[WARNING]  TEST INCONCLUSIVE - Got status {response.status_code}")

        print("=" * 100)

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] REQUEST FAILED")
        print()
        print(f"Error Type:  {type(e).__name__}")
        print(f"Error:       {str(e)}")
        print()
        print("=" * 100)

if __name__ == "__main__":
    test_limit_order()
