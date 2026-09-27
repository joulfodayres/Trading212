#!/usr/bin/env python3
"""
T212 Limit Order API Test GUI
Local testing tool for limit order API calls - NO automatic rounding
User controls decimal places for testing API behavior
Not integrated with project - standalone testing only
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import requests
import base64
from datetime import datetime

class T212LimitOrderTester:
    def __init__(self, root):
        self.root = root
        self.root.title("T212 Limit Order API Tester - Decimal Places Test")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e1e")

        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background="#1e1e1e", foreground="#e0e0e0")
        style.configure('TFrame', background="#1e1e1e")
        style.configure('TLabelframe', background="#1e1e1e", foreground="#e0e0e0")
        style.configure('TButton', background="#2d2d2d", foreground="#e0e0e0")
        style.configure('Header.TLabel', font=("Arial", 14, "bold"), foreground="#00d4ff")
        style.configure('Info.TLabel', font=("Arial", 10), foreground="#b0b0b0")
        style.configure('Success.TLabel', foreground="#00ff00")
        style.configure('Error.TLabel', foreground="#ff4444")

        # API Configuration
        self.api_key = "40512867ZyijwBGwduNcUlkHinVZrCXhzxAqU"
        self.api_secret = "iEQfVWUq3un1rGbM3ruzUWZweTRZYVLah-c8EFnCXW0"
        self.base_url = "https://demo.trading212.com/api/v0"
        self.environment = "demo"

        self.create_widgets()

    def create_widgets(self):
        """Create GUI widgets"""

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title = ttk.Label(main_frame, text="T212 Limit Order API Tester - Test Different Decimal Places", style="Header.TLabel")
        title.pack(pady=10)

        # Input Frame
        input_frame = ttk.LabelFrame(main_frame, text="Order Parameters (NO Automatic Rounding)", padding=10)
        input_frame.pack(fill="x", pady=10)

        # Ticker
        ttk.Label(input_frame, text="Ticker:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ticker_var = tk.StringVar(value="NQSEd_EQ")
        ticker_entry = ttk.Entry(input_frame, textvariable=self.ticker_var, width=25)
        ticker_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Quantity
        ttk.Label(input_frame, text="Quantity:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.quantity_var = tk.StringVar(value="0.5777225565048442")
        quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity_var, width=25)
        quantity_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(input_frame, text="Enter exact number - NO rounding applied", style="Info.TLabel").grid(row=1, column=2, sticky="w", padx=5)

        # Quantity Decimal Places
        ttk.Label(input_frame, text="Qty Decimals to Send:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.qty_decimals_var = tk.StringVar(value="3")
        qty_decimals_spinbox = ttk.Spinbox(input_frame, from_=0, to=16, textvariable=self.qty_decimals_var, width=5)
        qty_decimals_spinbox.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(input_frame, text="(Will round quantity to this many decimals)", style="Info.TLabel").grid(row=2, column=2, sticky="w", padx=5)

        # Limit Price
        ttk.Label(input_frame, text="Limit Price:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.price_var = tk.StringVar(value="17.326656")
        price_entry = ttk.Entry(input_frame, textvariable=self.price_var, width=25)
        price_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(input_frame, text="Enter exact number - NO rounding applied", style="Info.TLabel").grid(row=3, column=2, sticky="w", padx=5)

        # Price Decimal Places
        ttk.Label(input_frame, text="Price Decimals to Send:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.price_decimals_var = tk.StringVar(value="3")
        price_decimals_spinbox = ttk.Spinbox(input_frame, from_=0, to=16, textvariable=self.price_decimals_var, width=5)
        price_decimals_spinbox.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(input_frame, text="(Will round price to this many decimals)", style="Info.TLabel").grid(row=4, column=2, sticky="w", padx=5)

        # Time Validity
        ttk.Label(input_frame, text="Time Validity:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.validity_var = tk.StringVar(value="GOOD_TILL_CANCEL")
        validity_combo = ttk.Combobox(input_frame, textvariable=self.validity_var,
                                      values=["DAY", "GOOD_TILL_CANCEL"], state="readonly", width=23)
        validity_combo.grid(row=5, column=1, sticky="w", padx=5, pady=5)

        # Order Type
        ttk.Label(input_frame, text="Order Type:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.order_type_var = tk.StringVar(value="BUY")
        type_combo = ttk.Combobox(input_frame, textvariable=self.order_type_var,
                                  values=["BUY", "SELL"], state="readonly", width=23)
        type_combo.grid(row=6, column=1, sticky="w", padx=5, pady=5)

        # Environment info
        env_frame = ttk.Frame(input_frame)
        env_frame.grid(row=7, column=0, columnspan=3, sticky="w", padx=5, pady=10)
        ttk.Label(env_frame, text="Environment:", style="Info.TLabel").pack(side="left", padx=5)
        ttk.Label(env_frame, text="DEMO", style="Success.TLabel").pack(side="left", padx=5)
        ttk.Label(env_frame, text=f"URL: {self.base_url}", style="Info.TLabel").pack(side="left", padx=5)

        # Button Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        test_button = ttk.Button(button_frame, text="Send to T212 API", command=self.test_order)
        test_button.pack(side="left", padx=5)

        clear_button = ttk.Button(button_frame, text="Clear Output", command=self.clear_output)
        clear_button.pack(side="left", padx=5)

        # Test presets frame
        presets_frame = ttk.LabelFrame(main_frame, text="Quick Test Presets", padding=5)
        presets_frame.pack(fill="x", pady=5)

        ttk.Button(presets_frame, text="3 decimals (current fix)", command=lambda: self.set_decimals(3, 3)).pack(side="left", padx=2)
        ttk.Button(presets_frame, text="2 decimals", command=lambda: self.set_decimals(2, 2)).pack(side="left", padx=2)
        ttk.Button(presets_frame, text="1 decimal", command=lambda: self.set_decimals(1, 1)).pack(side="left", padx=2)
        ttk.Button(presets_frame, text="4 decimals", command=lambda: self.set_decimals(4, 4)).pack(side="left", padx=2)
        ttk.Button(presets_frame, text="8 decimals", command=lambda: self.set_decimals(8, 8)).pack(side="left", padx=2)
        ttk.Button(presets_frame, text="Original (16)", command=lambda: self.set_decimals(16, 16)).pack(side="left", padx=2)

        # Output Frame - Notebook with tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=10)

        # Tab 1: Request
        self.request_frame = ttk.Frame(notebook)
        notebook.add(self.request_frame, text="Request Payload")
        self.request_text = tk.Text(self.request_frame, height=15, width=120,
                                     bg="#2d2d2d", fg="#00ff00", font=("Courier", 9))
        self.request_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 2: Response
        self.response_frame = ttk.Frame(notebook)
        notebook.add(self.response_frame, text="Response Payload")
        self.response_text = tk.Text(self.response_frame, height=15, width=120,
                                      bg="#2d2d2d", fg="#00ff00", font=("Courier", 9))
        self.response_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab 3: Status
        self.status_frame = ttk.Frame(notebook)
        notebook.add(self.status_frame, text="Request/Response Info")
        self.status_text = tk.Text(self.status_frame, height=15, width=120,
                                    bg="#2d2d2d", fg="#00ff00", font=("Courier", 9))
        self.status_text.pack(fill="both", expand=True, padx=5, pady=5)

    def set_decimals(self, qty_decimals, price_decimals):
        """Set decimal places and test"""
        self.qty_decimals_var.set(str(qty_decimals))
        self.price_decimals_var.set(str(price_decimals))
        self.test_order()

    def test_order(self):
        """Test the limit order API call"""
        try:
            # Get input values
            ticker = self.ticker_var.get().strip()
            quantity_str = self.quantity_var.get().strip()
            price_str = self.price_var.get().strip()
            validity = self.validity_var.get()
            order_type = self.order_type_var.get()

            # Get decimal places to use
            try:
                qty_decimals = int(self.qty_decimals_var.get())
                price_decimals = int(self.price_decimals_var.get())
            except ValueError:
                messagebox.showerror("Error", "Decimal places must be integers")
                return

            # Validate inputs
            if not ticker:
                messagebox.showerror("Error", "Please enter a ticker")
                return

            try:
                quantity = float(quantity_str)
                price = float(price_str)
            except ValueError:
                messagebox.showerror("Error", "Quantity and Price must be valid numbers")
                return

            # Round values based on user-selected decimal places
            quantity_rounded = round(quantity, qty_decimals)
            price_rounded = round(price, price_decimals)

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

            # Display request
            self.display_request(payload, quantity, price, quantity_rounded, price_rounded,
                               qty_decimals, price_decimals, order_type)

            # Make API call
            self.make_api_call(payload)

        except Exception as e:
            messagebox.showerror("Error", f"Error: {str(e)}")

    def display_request(self, payload, original_qty, original_price, rounded_qty, rounded_price,
                       qty_decimals, price_decimals, order_type):
        """Display the request payload"""
        self.request_text.config(state="normal")
        self.request_text.delete(1.0, "end")

        # Title
        self.request_text.insert("end", "=" * 140 + "\n")
        self.request_text.insert("end", "REQUEST PAYLOAD - LIMIT ORDER\n")
        self.request_text.insert("end", "=" * 140 + "\n\n")

        # Order info
        self.request_text.insert("end", "ORDER DETAILS:\n")
        self.request_text.insert("end", f"  Order Type:      {order_type}\n")
        self.request_text.insert("end", f"  Ticker:          {payload['ticker']}\n")
        self.request_text.insert("end", f"  Time Validity:   {payload['timeValidity']}\n\n")

        # Quantity rounding
        self.request_text.insert("end", "QUANTITY ROUNDING:\n")
        self.request_text.insert("end", f"  Original Value:  {original_qty}\n")
        self.request_text.insert("end", f"  Original Decimals: {len(str(original_qty).split('.')[1]) if '.' in str(original_qty) else 0}\n")
        self.request_text.insert("end", f"  Decimals to Send: {qty_decimals}\n")
        self.request_text.insert("end", f"  Rounded Value:   {rounded_qty}\n")
        self.request_text.insert("end", f"  Final (in payload): {payload['quantity']}\n\n")

        # Price rounding
        self.request_text.insert("end", "PRICE ROUNDING:\n")
        self.request_text.insert("end", f"  Original Value:  {original_price}\n")
        self.request_text.insert("end", f"  Original Decimals: {len(str(original_price).split('.')[1]) if '.' in str(original_price) else 0}\n")
        self.request_text.insert("end", f"  Decimals to Send: {price_decimals}\n")
        self.request_text.insert("end", f"  Rounded Value:   {rounded_price}\n\n")

        # JSON Payload
        self.request_text.insert("end", "JSON PAYLOAD BEING SENT:\n")
        self.request_text.insert("end", json.dumps(payload, indent=2) + "\n\n")

        # URL
        self.request_text.insert("end", "ENDPOINT:\n")
        self.request_text.insert("end", f"  POST {self.base_url}/equity/orders/limit\n\n")

        # Auth
        self.request_text.insert("end", "AUTHENTICATION:\n")
        self.request_text.insert("end", f"  Type:            HTTP Basic Auth\n")
        credentials = f"{self.api_key}:{self.api_secret}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()
        self.request_text.insert("end", f"  Authorization:   Basic {credentials_b64[:50]}...\n")

        self.request_text.config(state="disabled")

    def make_api_call(self, payload):
        """Make the actual API call"""
        self.status_text.config(state="normal")
        self.status_text.delete(1.0, "end")

        start_time = datetime.now()

        self.status_text.insert("end", "=" * 140 + "\n")
        self.status_text.insert("end", "API CALL STATUS\n")
        self.status_text.insert("end", "=" * 140 + "\n\n")

        self.status_text.insert("end", f"Start Time:      {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        self.status_text.insert("end", f"Environment:     {self.environment.upper()}\n")
        self.status_text.insert("end", f"URL:             {self.base_url}/equity/orders/limit\n")
        self.status_text.insert("end", f"Payload Size:    {len(json.dumps(payload))} bytes\n\n")

        self.status_text.insert("end", "Sending request...\n\n")
        self.status_text.config(state="disabled")
        self.root.update()

        try:
            # Make request
            auth = (self.api_key, self.api_secret)
            headers = {"Content-Type": "application/json"}

            response = requests.post(
                f"{self.base_url}/equity/orders/limit",
                json=payload,
                auth=auth,
                headers=headers,
                timeout=10
            )

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Display response
            self.display_response(response, duration)

            # Display status
            self.display_status(response, duration, end_time)

        except requests.exceptions.RequestException as e:
            self.status_text.config(state="normal")
            self.status_text.insert("end", f"\nREQUEST FAILED:\n\n")
            self.status_text.insert("end", f"Error Type:  {type(e).__name__}\n")
            self.status_text.insert("end", f"Error:       {str(e)}\n")
            self.status_text.config(state="disabled")

            self.response_text.config(state="normal")
            self.response_text.delete(1.0, "end")
            self.response_text.insert("end", f"No response - request failed\n\n{str(e)}")
            self.response_text.config(state="disabled")

    def display_response(self, response, duration):
        """Display the response payload"""
        self.response_text.config(state="normal")
        self.response_text.delete(1.0, "end")

        self.response_text.insert("end", "=" * 140 + "\n")
        self.response_text.insert("end", "RESPONSE PAYLOAD\n")
        self.response_text.insert("end", "=" * 140 + "\n\n")

        # Status
        status_indicator = "[SUCCESS]" if 200 <= response.status_code < 300 else "[FAILED]"
        self.response_text.insert("end", f"Status Code:     {status_indicator} {response.status_code}\n")
        self.response_text.insert("end", f"Content-Type:    {response.headers.get('Content-Type', 'N/A')}\n")
        self.response_text.insert("end", f"Response Size:   {len(response.text)} bytes\n")
        self.response_text.insert("end", f"Duration:        {duration:.3f} seconds\n\n")

        # Response body
        self.response_text.insert("end", "RESPONSE BODY:\n\n")

        if response.text:
            try:
                response_json = response.json()
                self.response_text.insert("end", json.dumps(response_json, indent=2))
            except:
                self.response_text.insert("end", response.text)
        else:
            self.response_text.insert("end", "(No body)")

        self.response_text.config(state="disabled")

    def display_status(self, response, duration, end_time):
        """Display request/response status"""
        self.status_text.config(state="normal")
        self.status_text.insert("end", f"\nREQUEST SENT SUCCESSFULLY\n\n")
        self.status_text.insert("end", f"End Time:        {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n")
        self.status_text.insert("end", f"Duration:        {duration:.3f} seconds\n\n")

        # Status indicator
        if 200 <= response.status_code < 300:
            self.status_text.insert("end", f"[SUCCESS] 2xx Response\n\n")
            self.status_text.insert("end", f"Status Code:     {response.status_code}\n")
            self.status_text.insert("end", f"Reason:          {response.reason}\n")
            try:
                order_id = response.json().get('id')
                self.status_text.insert("end", f"Order ID:        {order_id}\n")
            except:
                pass
        elif 400 <= response.status_code < 500:
            self.status_text.insert("end", f"[ERROR] 4xx Client Error\n\n")
            self.status_text.insert("end", f"Status Code:     {response.status_code}\n")
            self.status_text.insert("end", f"Reason:          {response.reason}\n")
            try:
                error_detail = response.json().get("detail", "No detail provided")
                self.status_text.insert("end", f"Detail:          {error_detail}\n")
            except:
                pass
        elif 500 <= response.status_code < 600:
            self.status_text.insert("end", f"[WARNING] 5xx Server Error\n\n")
            self.status_text.insert("end", f"Status Code:     {response.status_code}\n")
            self.status_text.insert("end", f"Reason:          {response.reason}\n")
        else:
            self.status_text.insert("end", f"[UNKNOWN] Unexpected Status\n\n")
            self.status_text.insert("end", f"Status Code:     {response.status_code}\n")

        # Headers
        self.status_text.insert("end", f"\n\nRESPONSE HEADERS:\n")
        for header, value in response.headers.items():
            self.status_text.insert("end", f"  {header}: {value}\n")

        self.status_text.config(state="disabled")

    def clear_output(self):
        """Clear all output"""
        self.request_text.config(state="normal")
        self.request_text.delete(1.0, "end")
        self.request_text.config(state="disabled")

        self.response_text.config(state="normal")
        self.response_text.delete(1.0, "end")
        self.response_text.config(state="disabled")

        self.status_text.config(state="normal")
        self.status_text.delete(1.0, "end")
        self.status_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = T212LimitOrderTester(root)
    root.mainloop()
