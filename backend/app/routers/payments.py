import os
import time
import razorpay
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/payments", tags=["Payments"])

razorpay_client = razorpay.Client(
    auth=(os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET"))
)

class OrderRequest(BaseModel):
    amount: float

@router.post("/create-order")
async def create_order(data: OrderRequest):
    try:
        if not data.amount or data.amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")

        amount_in_paise = int(data.amount * 100)
        
        options = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": f"rcpt_{int(time.time())}"
        }

        order = razorpay_client.order.create(data=options)
        return {"success": True, "order": order}
        
    except Exception as e:
        print("Razorpay Order Error:", str(e))
        raise HTTPException(
            status_code=500, 
            detail=f"Unable to create payment order: {str(e)}"
        )