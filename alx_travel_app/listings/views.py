#Create API ViewSets

from rest_framework import viewsets, status
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer, PaymentSerializer
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
import requests
import uuid
import os
from .tasks import send_booking_confirmation_email

class ListingViewSet(viewsets.ModelViewSet):
    #ViewSet for managing Listings
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        email = booking.user.email
        booking_details = f"{booking.destination} on {booking.date}"

        # Trigger Celery task asynchronously
        send_booking_confirmation_email.delay(email, booking_details)

class BookingViewSet(viewsets.ModelViewSet):
    #ViewSet for managing Bookings
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

"""
    Uses ModelViewSet → gives you full CRUD functionality automatically.

    Connects your models to serializers.

     DRF handles routes, validation, and responses for you.
"""

#  Payment ViewSet
class PaymentViewSet(viewsets.ViewSet):
    """
    Handles payment initiation and verification using Chapa API.
    """

    @action(detail=False, methods=["post"])
    def initiate(self, request):
        """
        Initiate a Chapa payment for a given booking.
        """
        booking_id = request.data.get("booking_id")

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        amount = booking.listing.price
        email = request.user.email if request.user.is_authenticated else "test@example.com"
        tx_ref = str(uuid.uuid4())  # unique reference

        payment = Payment.objects.create(
            booking=booking,
            amount=amount,
            chapa_tx_ref=tx_ref,
            status="pending",
        )

        headers = {
            "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}",
            "Content-Type": "application/json",
        }

        data = {
            "amount": str(amount),
            "currency": "ETB",
            "email": email,
            "tx_ref": tx_ref,
            "callback_url": "http://127.0.0.1:8000/api/payments/verify/",
            "first_name": request.user.username if request.user.is_authenticated else "Guest",
            "last_name": "User",
            "customization[title]": "Travel Booking Payment",
            "customization[description]": "Payment for travel booking",
        }

        response = requests.post(
            f"{os.getenv('CHAPA_BASE_URL')}/transaction/initialize",
            json=data,
            headers=headers
        )

        chapa_response = response.json()

        if response.status_code == 200 and chapa_response.get("status") == "success":
            return Response({
                "message": "Payment initialized successfully.",
                "checkout_url": chapa_response["data"]["checkout_url"],
                "tx_ref": tx_ref,
            })
        else:
            payment.status = "failed"
            payment.save()
            return Response({
                "error": "Payment initiation failed.",
                "details": chapa_response,
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def verify(self, request):
        """
        Verify payment status with Chapa after user completes payment.
        """
        tx_ref = request.query_params.get("tx_ref")

        if not tx_ref:
            return Response({"error": "Transaction reference is required."}, status=status.HTTP_400_BAD_REQUEST)

        headers = {
            "Authorization": f"Bearer {os.getenv('CHAPA_SECRET_KEY')}",
        }

        response = requests.get(
            f"{os.getenv('CHAPA_BASE_URL')}/transaction/verify/{tx_ref}",
            headers=headers
        )

        chapa_response = response.json()

        try:
            payment = Payment.objects.get(chapa_tx_ref=tx_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

        if response.status_code == 200 and chapa_response.get("status") == "success":
            payment.status = "completed"
            payment.chapa_transaction_id = chapa_response["data"]["id"]
            payment.save()
            return Response({
                "message": "Payment verified successfully.",
                "status": payment.status,
                "transaction_id": payment.chapa_transaction_id,
            })
        else:
            payment.status = "failed"
            payment.save()
            return Response({
                "error": "Payment verification failed.",
                "details": chapa_response,
            }, status=status.HTTP_400_BAD_REQUEST)


# --- home view ---
def home(request):
    return render(request, 'listings/home.html')