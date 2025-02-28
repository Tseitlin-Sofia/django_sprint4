from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse


QUANTITY_POST = 10


def send_email_to_admin(post, user):
    subject = f'Новый пост: {post.title}'
    message = f'''Пользователь {user.username}
        создал пост '{post.title}'.'''
    send_mail(
        subject=subject,
        message=message,
        from_email='user_email@blogicum.not',
        recipient_list=['admin_email@blogicum.not'],
        fail_silently=True
    )
    return HttpResponse('Email sent successfully!')


def paginated_pages(post_list, request):
    paginator = Paginator(post_list, QUANTITY_POST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
