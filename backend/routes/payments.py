"""
Micro-transaction payment routes
Handles $1.99 single re-scans and $6.99 weekly passes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import stripe
import os
import logging
import secrets
import bcrypt

from models import db, User, Purchase, Analysis
from services.subscription_service import SubscriptionService

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')
logger = logging.getLogger(__name__)

# Get Stripe API key from environment
STRIPE_API_KEY = os.getenv('STRIPE_SECRET_KEY')
if STRIPE_API_KEY:
    stripe.api_key = STRIPE_API_KEY

# Pricing configuration
PRICING = {
    'single_rescan': {
        'amount': 199,  # $1.99 in cents
        'description': 'Single Resume Re-Scan',
        'credits': 1
    },
    'weekly_pass': {
        'amount': 699,  # $6.99 in cents
        'description': '7-Day Unlimited Pass',
        'duration_days': 7,
        'credits': 0  # Unlimited during the period
    }
}


@payments_bp.route('/create-micro-purchase', methods=['POST'])
@jwt_required()
def create_micro_purchase():
    """
    Create a Stripe payment intent for micro-transactions ($1.99 re-scan or $6.99 weekly pass)

    Request body:
        - purchase_type: 'single_rescan' or 'weekly_pass'

    Returns:
        - client_secret: Stripe PaymentIntent client secret
        - amount: Amount in cents
        - purchase_info: Details about the purchase
    """
    try:
        if not STRIPE_API_KEY:
            logger.error("Stripe API key not configured")
            return jsonify({
                'error': 'Payment service is not configured. Please contact support.'
            }), 500

        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get purchase type from request
        data = request.get_json()
        purchase_type = data.get('purchase_type', 'single_rescan')

        if purchase_type not in PRICING:
            return jsonify({'error': 'Invalid purchase type'}), 400

        pricing_info = PRICING[purchase_type]

        # Create or get Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name or user.email.split('@')[0]
            )
            user.stripe_customer_id = customer.id
            db.session.commit()

        # Create PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            amount=pricing_info['amount'],
            currency='usd',
            customer=user.stripe_customer_id,
            description=pricing_info['description'],
            metadata={
                'user_id': user.id,
                'purchase_type': purchase_type,
                'user_email': user.email
            },
            automatic_payment_methods={'enabled': True}
        )

        logger.info(f"Created payment intent {payment_intent.id} for user {user.id} - {purchase_type}")

        return jsonify({
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
            'amount': pricing_info['amount'],
            'amount_display': f"${pricing_info['amount'] / 100:.2f}",
            'purchase_type': purchase_type,
            'description': pricing_info['description']
        }), 200

    except Exception as e:
        logger.error(f"Error creating micro-purchase payment intent: {str(e)}")
        return jsonify({
            'error': 'Failed to create payment intent',
            'details': str(e)
        }), 500


@payments_bp.route('/confirm-micro-purchase', methods=['POST'])
@jwt_required()
def confirm_micro_purchase():
    """
    Confirm a micro-purchase after successful payment

    Request body:
        - payment_intent_id: Stripe PaymentIntent ID
        - purchase_type: 'single_rescan' or 'weekly_pass'

    Returns:
        - success: boolean
        - purchase: Purchase details
        - user_info: Updated user information
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        purchase_type = data.get('purchase_type')

        if not payment_intent_id or purchase_type not in PRICING:
            return jsonify({'error': 'Invalid request'}), 400

        # Verify payment intent with Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if payment_intent.status != 'succeeded':
            return jsonify({
                'error': 'Payment not completed',
                'payment_status': payment_intent.status
            }), 400

        # Check if purchase already exists (prevent double-processing)
        existing_purchase = Purchase.query.filter_by(
            stripe_payment_intent_id=payment_intent_id
        ).first()

        if existing_purchase:
            logger.warning(f"Purchase already processed: {payment_intent_id}")
            return jsonify({
                'success': True,
                'purchase': existing_purchase.to_dict(),
                'message': 'Purchase already processed'
            }), 200

        pricing_info = PRICING[purchase_type]

        # Create purchase record
        purchase = Purchase(
            user_id=user.id,
            purchase_type=purchase_type,
            amount_usd=pricing_info['amount'] / 100,  # Convert cents to dollars
            credits_granted=pricing_info.get('credits', 0),
            stripe_payment_intent_id=payment_intent_id,
            stripe_charge_id=payment_intent.latest_charge if hasattr(payment_intent, 'latest_charge') else None,
            payment_status='succeeded',
            payment_method=payment_intent.payment_method_types[0] if payment_intent.payment_method_types else None
        )

        # Grant benefits based on purchase type
        if purchase_type == 'single_rescan':
            # Add 1 credit for re-scan
            user.credits += 1
            purchase.credits_granted = 1
            message = 'Credit added! You can now re-scan your resume.'

        elif purchase_type == 'weekly_pass':
            # Grant 7-day unlimited access
            purchase.access_expires_at = datetime.utcnow() + timedelta(days=7)
            user.subscription_tier = 'weekly_pass'
            user.subscription_status = 'active'
            user.subscription_start_date = datetime.utcnow()
            message = '7-day pass activated! Enjoy unlimited scans for the next week.'

        db.session.add(purchase)
        db.session.commit()

        logger.info(f"Confirmed {purchase_type} purchase for user {user.id}")

        return jsonify({
            'success': True,
            'purchase': purchase.to_dict(),
            'user_info': {
                'credits': user.credits,
                'subscription_tier': user.subscription_tier,
                'subscription_status': user.subscription_status
            },
            'message': message
        }), 200

    except Exception as e:
        logger.error(f"Error confirming micro-purchase: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to confirm purchase',
            'details': str(e)
        }), 500


@payments_bp.route('/check-weekly-pass', methods=['GET'])
@jwt_required()
def check_weekly_pass():
    """
    Check if user has an active weekly pass

    Returns:
        - has_active_pass: boolean
        - expires_at: expiration datetime if active
    """
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Find active weekly pass
        active_pass = Purchase.query.filter(
            Purchase.user_id == user.id,
            Purchase.purchase_type == 'weekly_pass',
            Purchase.is_active == True,
            Purchase.payment_status == 'succeeded',
            Purchase.access_expires_at > datetime.utcnow()
        ).order_by(Purchase.access_expires_at.desc()).first()

        if active_pass:
            time_remaining = active_pass.access_expires_at - datetime.utcnow()
            hours_remaining = int(time_remaining.total_seconds() / 3600)

            return jsonify({
                'has_active_pass': True,
                'expires_at': active_pass.access_expires_at.isoformat(),
                'hours_remaining': hours_remaining,
                'purchase_id': active_pass.id
            }), 200
        else:
            return jsonify({
                'has_active_pass': False,
                'expires_at': None
            }), 200

    except Exception as e:
        logger.error(f"Error checking weekly pass: {str(e)}")
        return jsonify({
            'error': 'Failed to check weekly pass status',
            'details': str(e)
        }), 500


@payments_bp.route('/guest-checkout', methods=['POST'])
def guest_checkout():
    """
    Create a payment intent for guest checkout (no account required)
    Only available for $1.99 single_rescan purchases
    
    Request body:
        - email: Customer email (required)
        - purchase_type: 'single_rescan' (only allowed type)
    
    Returns:
        - client_secret: Stripe PaymentIntent client secret
        - guest_token: Temporary token for guest session
        - amount: Amount in cents
    """
    try:
        if not STRIPE_API_KEY:
            logger.error("Stripe API key not configured")
            return jsonify({
                'error': 'Payment service is not configured. Please contact support.'
            }), 500

        data = request.get_json()
        email = data.get('email', '').strip().lower()
        purchase_type = data.get('purchase_type', 'single_rescan')

        # Validate email
        if not email or '@' not in email:
            return jsonify({'error': 'Valid email is required'}), 400

        # Only allow single_rescan for guest checkout
        if purchase_type != 'single_rescan':
            return jsonify({
                'error': 'Guest checkout is only available for single re-scan purchases'
            }), 400

        if purchase_type not in PRICING:
            return jsonify({'error': 'Invalid purchase type'}), 400

        pricing_info = PRICING[purchase_type]

        # Find or create guest user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create guest account (no password, email not verified)
            # User can verify and set password later if they want
            user = User(
                email=email,
                password_hash=None,  # No password for guest accounts
                auth_provider='guest',
                email_verified=False,
                subscription_tier='free',
                subscription_status='inactive',
                credits=0,  # Will be granted after payment
                is_trial_active=False
            )
            db.session.add(user)
            db.session.flush()  # Get user.id without committing
            logger.info(f"Created guest account for {email}")
        else:
            # Existing user - they can pay as guest and we'll link it
            logger.info(f"Guest checkout for existing user {email}")

        # Create or get Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name or user.email.split('@')[0]
            )
            user.stripe_customer_id = customer.id
            db.session.commit()
        else:
            db.session.commit()

        # Create PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            amount=pricing_info['amount'],
            currency='usd',
            customer=user.stripe_customer_id,
            description=pricing_info['description'],
            metadata={
                'user_id': user.id,
                'purchase_type': purchase_type,
                'user_email': user.email,
                'is_guest_checkout': 'true'
            },
            automatic_payment_methods={'enabled': True}
        )

        # Generate temporary guest token for this checkout session
        guest_token = 'guest_checkout_' + secrets.token_urlsafe(32)

        logger.info(f"Created guest checkout payment intent {payment_intent.id} for {email}")

        return jsonify({
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
            'guest_token': guest_token,
            'amount': pricing_info['amount'],
            'amount_display': f"${pricing_info['amount'] / 100:.2f}",
            'purchase_type': purchase_type,
            'description': pricing_info['description']
        }), 200

    except Exception as e:
        logger.error(f"Error creating guest checkout: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create checkout',
            'details': str(e)
        }), 500


@payments_bp.route('/confirm-guest-purchase', methods=['POST'])
def confirm_guest_purchase():
    """
    Confirm a guest purchase after successful payment
    No authentication required - uses payment_intent_id to verify
    
    Request body:
        - payment_intent_id: Stripe PaymentIntent ID
        - email: Customer email
        - guest_token: Temporary guest token (optional)
    
    Returns:
        - success: boolean
        - purchase: Purchase details
        - user_info: User information
        - access_token: JWT token if user wants to create account
    """
    try:
        data = request.get_json()
        payment_intent_id = data.get('payment_intent_id')
        email = data.get('email', '').strip().lower()
        purchase_type = 'single_rescan'  # Only type for guest checkout

        if not payment_intent_id or not email:
            return jsonify({'error': 'Invalid request'}), 400

        # Verify payment intent with Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if payment_intent.status != 'succeeded':
            return jsonify({
                'error': 'Payment not completed',
                'payment_status': payment_intent.status
            }), 400

        # Get user from payment intent metadata
        user_id = payment_intent.metadata.get('user_id')
        if not user_id:
            return jsonify({'error': 'Invalid payment'}), 400

        user = User.query.get(int(user_id))
        if not user or user.email != email:
            return jsonify({'error': 'User not found'}), 404

        # Check if purchase already exists
        existing_purchase = Purchase.query.filter_by(
            stripe_payment_intent_id=payment_intent_id
        ).first()

        if existing_purchase:
            logger.warning(f"Guest purchase already processed: {payment_intent_id}")
            return jsonify({
                'success': True,
                'purchase': existing_purchase.to_dict(),
                'message': 'Purchase already processed'
            }), 200

        pricing_info = PRICING[purchase_type]

        # Create purchase record
        purchase = Purchase(
            user_id=user.id,
            purchase_type=purchase_type,
            amount_usd=pricing_info['amount'] / 100,
            credits_granted=1,
            stripe_payment_intent_id=payment_intent_id,
            stripe_charge_id=payment_intent.latest_charge if hasattr(payment_intent, 'latest_charge') else None,
            payment_status='succeeded',
            payment_method=payment_intent.payment_method_types[0] if payment_intent.payment_method_types else None
        )

        # Grant 1 credit for re-scan
        user.credits += 1
        purchase.credits_granted = 1

        db.session.add(purchase)
        db.session.commit()

        logger.info(f"Confirmed guest {purchase_type} purchase for user {user.id}")

        # Generate access token if user wants to create account
        from flask_jwt_extended import create_access_token
        access_token = None
        if user.auth_provider == 'guest':
            # Create temporary token for guest to access their account
            access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=30))

        return jsonify({
            'success': True,
            'purchase': purchase.to_dict(),
            'user_info': {
                'email': user.email,
                'credits': user.credits,
                'is_guest': user.auth_provider == 'guest'
            },
            'access_token': access_token,  # Token for guest to access account
            'message': 'Payment successful! You can now re-scan your resume.',
            'create_account_prompt': user.auth_provider == 'guest'  # Prompt to create account
        }), 200

    except Exception as e:
        logger.error(f"Error confirming guest purchase: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'Failed to confirm purchase',
            'details': str(e)
        }), 500


@payments_bp.route('/pricing', methods=['GET'])
def get_pricing():
    """
    Get current pricing information (public endpoint)

    Returns:
        - pricing: All pricing tiers and options
    """
    return jsonify({
        'micro_transactions': {
            'single_rescan': {
                'price': 1.99,
                'currency': 'USD',
                'description': 'Single Resume Re-Scan',
                'best_for': 'Quick check after making changes'
            },
            'weekly_pass': {
                'price': 6.99,
                'currency': 'USD',
                'description': '7-Day Unlimited Pass',
                'best_for': 'Active job seekers',
                'popular': True
            }
        },
        'subscription': {
            'monthly_pro': {
                'price': 19.99,
                'currency': 'USD',
                'description': 'Monthly Pro Subscription',
                'best_for': 'Serious career advancement'
            }
        }
    }), 200


@payments_bp.route('/purchase-history', methods=['GET'])
@jwt_required()
def get_purchase_history():
    """
    Get user's purchase history

    Returns:
        - purchases: List of all purchases
    """
    try:
        user_id = int(get_jwt_identity())

        purchases = Purchase.query.filter_by(user_id=user_id).order_by(
            Purchase.created_at.desc()
        ).limit(50).all()

        return jsonify({
            'purchases': [p.to_dict() for p in purchases],
            'total_purchases': len(purchases)
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving purchase history: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve purchase history',
            'details': str(e)
        }), 500
