from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import logging
from typing import Optional

app = FastAPI();
logging.basicConfig(level=logging.INFO)

# -------------------------
# Request / Response Models
# -------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    
class ChatResponse(BaseModel):
    response: str   
    status: str
    
# -------------------------
# Mock Backend Service
# -------------------------
def get_order_status(order_id: str) -> str:
    # Simulate fetching order status from a database. Mock data for demonstration.
    order_statuses = {
        "12345": "Shipped",
        "67890": "Processing",
        "54321": "Delivered"
    }
    if order_id in order_statuses:
        return order_statuses[order_id]
    else:        
        raise ValueError("Order ID not found")
    
    # -------------------------
# Deterministic Intent Logic
# -------------------------
def extract_order_id(message: str) -> Optional[str]:
    # Simple regex to extract order ID (assuming it's a 5-digit number)
    match = re.search(r'\b\d{5}\b', message)
    if match:
        return match.group();
    return None;

def is_order_status_intent(message: str) -> bool:
    """
    Simple deterministic intent check.
    """
    keywords = ["order", "status", "where"]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in keywords)

# -------------------------
# Chat Endpoint
# -------------------------

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        #Step 1 define request message; handle error if intent not order status
        message = request.message.strip()
        
        logging.info(f"Incoming message: {message}");
        
        if not is_order_status_intent(message):
            return ChatResponse(
                response= "I'm sorry, I can help with Order Status Inquiries",   
                status= "unsupported_intent"
            )
            
        #Step 2 define order id; handle error if order id not found
        order_id = extract_order_id(message)
        
        if not order_id:
            return ChatResponse(
                response= "Please provide your Order ID",   
                status= "missing_order_id"
            )
        
        #Step 3 define order status; give a success response
        order_status = get_order_status(order_id);
        
        if order_status:
            return ChatResponse(
                response= f"Your order {order_id} is currently {order_status}.",
                status= "Success"
            )
    # except: ValueError; handle error if order is in correct or value is not correct        
    except ValueError as ve:
        logging.error(f"Business error: {str(ve)}")
        
        return ChatResponse(
            response="I couldn't find that order. Please verify the ID.",
            status="order_not_found"
        )
    # except: Exception; handle all other errors and raise a HTTPException 500
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal Sever Error"
        )
    








        
# #EXPRESS JS EQUIVALENT (for reference, not part of the FastAPI code)
# const express = require("express");
# const router = express.Router();

# #Example: your helper functions
# const { isOrderStatusIntent, extractOrderId, getOrderStatus } = require("./utils");

# router.post("/chat", async (req, res) => {
#   try {
#     const message = req.body.message.trim();

#     console.info(`Incoming message: ${message}`);

#     // Step 1: Intent check
#     if (!isOrderStatusIntent(message)) {
#       return res.json({
#         response: "I'm sorry, I can currently only help with order status inquiries.",
#         status: "unsupported_intent"
#       });
#     }

#     // Step 2: Extract order ID
#     const orderId = extractOrderId(message);

#     if (!orderId) {
#       return res.json({
#         response: "Please provide your order ID.",
#         status: "missing_order_id"
#       });
#     }

#     // Step 3: Call backend service
#     const orderStatus = await getOrderStatus(orderId);

#     return res.json({
#       response: `Your order ${orderId} is currently ${orderStatus}.`,
#       status: "success"
#     });

#   } catch (err) {
#     # // Business logic error (similar to catching ValueError)
#     if (err instanceof ValueError) {
#       console.error(`Business error: ${err.message}`);
#       return res.json({
#         response: "I couldn't find that order. Please verify the ID.",
#         status: "order_not_found"
#       });
#     }

#     # // Unexpected error
#     console.error(`Unexpected error: ${err.message}`);
#     return res.status(500).json({
#       detail: "Internal server error"
#     });
#   }
# });

# module.exports = router;
