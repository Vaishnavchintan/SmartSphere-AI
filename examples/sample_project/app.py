"""
Online Order Processing Service
Intentionally flawed sample file for testing multi-agent review crew.
Demonstrates security vulnerabilities, high cyclomatic complexity,
and missing test/doc coverage.
"""

import os
import sqlite3
import requests

# Security Flaw #1: Hardcoded sensitive API secret
STRIPE_API_KEY = "sk_live_51M0abcdef1234567890qwertyuiopASDFGHJKLzxcvbnm"
DATABASE_PATH = "production_orders.db"


def get_user_profile(username, password):
    """Fetch user profile with raw SQL string formatting."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Security Flaw #2: Direct SQL Injection vulnerability
    query = f"SELECT id, username, email, is_admin FROM users WHERE username = '{username}' AND password = '{password}'"
    print(f"[DEBUG] Executing: {query}")
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    return user


def process_orders(orders, user_tier, discount_code, apply_tax, country_code, is_holiday, max_retry=3):
    # Quality Flaw: Radon Cyclomatic Complexity > 16 (Grade C/D), deeply nested conditionals
    processed_count = 0
    total_revenue = 0.0
    failed_orders = []

    if orders is not None:
        if len(orders) > 0:
            for order in orders:
                if order.get("status") == "pending":
                    if order.get("amount") is not None and order.get("amount") > 0:
                        base_price = order.get("amount")
                        
                        # Nested tier discount logic
                        if user_tier == "vip":
                            if discount_code == "SUMMER2026":
                                final_price = base_price * 0.70
                            elif discount_code == "LOYALTY":
                                final_price = base_price * 0.80
                            else:
                                final_price = base_price * 0.85
                        elif user_tier == "gold":
                            if discount_code == "SUMMER2026":
                                final_price = base_price * 0.80
                            else:
                                final_price = base_price * 0.90
                        elif user_tier == "silver":
                            if discount_code == "FIRST_ORDER":
                                final_price = base_price * 0.95
                            else:
                                final_price = base_price
                        else:
                            final_price = base_price

                        # Holiday surcharge or discount
                        if is_holiday:
                            if country_code == "US" or country_code == "CA":
                                final_price = final_price * 1.05
                            elif country_code == "UK" or country_code == "DE":
                                final_price = final_price * 1.02
                            else:
                                final_price = final_price * 1.01

                        # Tax calculations
                        if apply_tax:
                            if country_code == "US":
                                final_price += final_price * 0.08
                            elif country_code == "UK":
                                final_price += final_price * 0.20
                            elif country_code == "DE":
                                final_price += final_price * 0.19
                            else:
                                final_price += final_price * 0.05

                        if final_price > 10000:
                            print("High value order detected! Manual review required.")
                            order["requires_manual_approval"] = True
                        else:
                            order["requires_manual_approval"] = False

                        order["final_price"] = round(final_price, 2)
                        order["status"] = "processed"
                        total_revenue += order["final_price"]
                        processed_count += 1
                    else:
                        failed_orders.append({"id": order.get("id"), "reason": "invalid_amount"})
                else:
                    if order.get("status") == "cancelled":
                        failed_orders.append({"id": order.get("id"), "reason": "cancelled_by_user"})
                    elif order.get("status") == "refunded":
                        failed_orders.append({"id": order.get("id"), "reason": "already_refunded"})
                    else:
                        failed_orders.append({"id": order.get("id"), "reason": "unknown_status"})
        else:
            return {"error": "Empty orders list"}
    else:
        return {"error": "Orders cannot be None"}

    return {
        "processed_count": processed_count,
        "total_revenue": round(total_revenue, 2),
        "failed_orders": failed_orders
    }


def execute_admin_diagnostic(command_arg):
    # Security Flaw #3: Insecure Command Execution
    import os
    # Potential OS command injection
    result = os.system("echo 'Diagnostics for: " + command_arg + "' >> system_audit.log")
    return result
