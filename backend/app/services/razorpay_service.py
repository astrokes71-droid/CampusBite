import os
import razorpay
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

def get_razorpay_client():
    key = os.getenv("RAZORPAY_KEY_ID")
    secret = os.getenv("RAZORPAY_KEY_SECRET")

    if not key or not secret:
        raise RuntimeError("Razorpay credentials missing")

    if not key.startswith("rzp_test_"):
        raise RuntimeError("Only Razorpay Test Mode is allowed")

    return razorpay.Client(auth=(key, secret))

def create_razorpay_order(amount_paise, receipt):
    if type(amount_paise) is not int or amount_paise < 100:
        raise ValueError("Invalid payment amount")

    client = get_razorpay_client()
    return client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "receipt": receipt
    })

def verify_razorpay_payment(order_id, payment_id, signature):
    client = get_razorpay_client()
    client.utility.verify_payment_signature({
        "razorpay_order_id": order_id,
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature
    })
    return True
