from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import LoginForm

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(
        template_name='registrations/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('student/', views.student, name='student'),
    path('instructor/', views.instructor, name='instructor'),
    path('instructor/<int:pk>/approve-account/', views.approve_instructor_account, name='approve_instructor_account'),
    path('course/', views.course, name='course'),
    path('course/<int:pk>/enroll/', views.enroll_in_course, name='enroll_in_course'),
    path('enrollment/<int:pk>/pay/', views.pay_enrollment, name='pay_enrollment'),
    path('enrollment/', views.enrollment, name='enrollment'),
    path('payment/', views.payment, name='payment'),
    path('lesson/', views.lesson, name='lesson'),
    path('lesson-resources/', views.lesson_resources, name='lesson_resources'),
    path('lesson-resource/<int:pk>/open/', views.open_lesson_resource, name='open_lesson_resource'),
    path('lesson-tracker/', views.lesson_tracker, name='lesson_tracker'),

    path('add-course/', views.add_course, name='add_course'),
    path('add-enrollment/', views.add_enrollment, name='add_enrollment'),
    path('add-payment/', views.add_payment, name='add_payment'),
    path('add-lesson/', views.add_lesson, name='add_lesson'),
    path('add-lesson-tracker/', views.add_lesson_tracker, name='add_lesson_tracker'),
    path('add-student/', views.add_student, name='add_student'),
    path('add-instructor/', views.add_instructor, name='add_instructor'),

    path('student/<int:pk>/edit/', views.edit_student, name='edit_student'),
    path('student/<int:pk>/delete/', views.delete_student, name='delete_student'),
    path('instructor/<int:pk>/edit/', views.edit_instructor, name='edit_instructor'),
    path('instructor/<int:pk>/delete/', views.delete_instructor, name='delete_instructor'),
    path('course/<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('course/<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('enrollment/<int:pk>/edit/', views.edit_enrollment, name='edit_enrollment'),
    path('enrollment/<int:pk>/delete/', views.delete_enrollment, name='delete_enrollment'),
    path('payment/<int:pk>/edit/', views.edit_payment, name='edit_payment'),
    path('payment/<int:pk>/delete/', views.delete_payment, name='delete_payment'),
    path('lesson/<int:pk>/edit/', views.edit_lesson, name='edit_lesson'),
    path('lesson/<int:pk>/delete/', views.delete_lesson, name='delete_lesson'),
    path('lesson-tracker/<int:pk>/edit/', views.edit_lesson_tracker, name='edit_lesson_tracker'),
    path('lesson-tracker/<int:pk>/delete/', views.delete_lesson_tracker, name='delete_lesson_tracker'),

]



