# app/service.py
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Delivery


class DeliveryService:
    def create_delivery(
        self,
        db: Session,
        reservation_id: str,
        item_id: str,
        buyer_email: str,
        seller_email: str,
    ) -> Delivery:
        delivery = Delivery(
            reservation_id=reservation_id,
            item_id=item_id,
            buyer_email=buyer_email.lower(),
            seller_email=seller_email.lower(),
            status="PENDING",
        )
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
        return delivery

    def confirm_delivery(self, db: Session, delivery_id: str, actor_email: str) -> Delivery:
        delivery = db.get(Delivery, delivery_id)
        if not delivery:
            raise ValueError("delivery_not_found")

        email = actor_email.lower()

        if email == delivery.buyer_email:
            delivery.buyer_confirmed = True
        elif email == delivery.seller_email:
            delivery.seller_confirmed = True
        else:
            raise PermissionError("not_participant")

        if delivery.buyer_confirmed and delivery.seller_confirmed:
            delivery.status = "DELIVERED"
            delivery.delivered_at = datetime.utcnow()

        db.commit()
        db.refresh(delivery)
        return delivery
