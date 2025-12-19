from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
import logging


from .models import Loan


@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass


@shared_task
def check_overdue_loans():
    logging.info("Task check_overdue_loans has started")
    overdue_loans = Loan.objects.filter(is_returned=False, due_date__gt=timezone.now()).select_related("member__user", "book")

    logging.info(f"{len(overdue_loans)} overdue loans found.")
    for loan in overdue_loans:
        book_title = loan.book.title
        member_email = loan.member.user.email
 
        send_mail(
            subject='Overdue Loan Reminder',
            message=f'Hello {loan.member.user.username},\n\nThe book with title: "{book_title}" is past overdue.\nPlease return it.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
        logging.info("Email for loan with id: f{loan.id}, sent.")
