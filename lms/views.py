from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    CourseForm,
    EnrollmentForm,
    InstructorForm,
    LessonForm,
    LessonResourceForm,
    LessonTrackerForm,
    PaymentReviewForm,
    PaymentSubmissionForm,
    SignupForm,
    PaymentForm,
    StudentForm,
)
from .decorators import login_required_message
from .models import Course, Enrollment, Instructor, Lesson, LessonResource, LessonTracker, Payment, Student


def _latest_five(queryset):
    return list(queryset.order_by("pk"))


def _course_cover(course_record):
    category = f"{course_record.course_name} {course_record.Category}".casefold()
    if "cyber" in category or "security" in category:
        return "cybersecurity.jpg"
    if "network" in category or "ccna" in category:
        return "networking-course.jpg"
    if "web" in category or "develop" in category or "program" in category:
        return "web-development.jpg"
    return "digital-learning.jpg"


def home(request):
    return render(request, "lms/landing.html")


@login_required_message
def dashboard(request):
    student_record = _student_for_user(request.user)
    display_name = request.user.get_full_name() or request.user.username
    if student_record and not request.user.is_staff:
        student_enrollments = list(
            Enrollment.objects.filter(Student_id=student_record)
            .exclude(status="Cancelled")
            .select_related("Course_id")
            .order_by("-pk")
        )
        for enrollment_record in student_enrollments:
            enrollment_record.course_cover = _course_cover(enrollment_record.Course_id)
            enrollment_record.lesson_count = Lesson.objects.filter(Course_id=enrollment_record.Course_id).count()
        student_cards = [
            {
                "label": "Courses Enrolled",
                "count": Enrollment.objects.filter(
                    Student_id=student_record,
                    status__in=("Pending", "Active", "Completed"),
                ).values("Course_id").distinct().count(),
                "description": "Your course enrollments",
                "icon": "book-half",
                "tone": "navy",
                "url": "enrollment",
            },
            {
                "label": "Payments Made",
                "count": Payment.objects.filter(Enrollment_id__Student_id=student_record).count(),
                "description": "Your submitted payments",
                "icon": "credit-card-2-front-fill",
                "tone": "terracotta",
                "url": "payment",
            },
            {
                "label": "Lessons Completed",
                "count": LessonTracker.objects.filter(
                    Enrollment_id__Student_id=student_record,
                    status="Completed",
                ).count(),
                "description": "Lessons you have completed",
                "icon": "clipboard2-check-fill",
                "tone": "green",
                "url": "lesson_tracker",
            },
        ]
        recent_payments = Payment.objects.filter(Enrollment_id__Student_id=student_record).select_related(
            "Enrollment_id__Course_id"
        ).order_by("-pk")[:3]
        return render(request, "lms/home.html", {
            "summary_cards": student_cards,
            "dashboard_role": "student",
            "display_name": display_name,
            "student_enrollments": student_enrollments,
            "recent_payments": recent_payments,
        })

    summary_cards = [
        {
            "label": "Students",
            "count": Student.objects.count(),
            "description": "Registered learners",
            "icon": "people-fill",
            "tone": "orange",
            "url": "student",
        },
        {
            "label": "Instructors",
            "count": Instructor.objects.count(),
            "description": "Registered instructors",
            "icon": "person-vcard-fill",
            "tone": "navy",
            "url": "instructor",
        },
        {
            "label": "Courses",
            "count": Course.objects.count(),
            "description": "Courses in the catalogue",
            "icon": "book-half",
            "tone": "terracotta",
            "url": "course",
        },
        {
            "label": "Enrollments",
            "count": Enrollment.objects.count(),
            "description": "Student course enrollments",
            "icon": "person-check-fill",
            "tone": "green",
            "url": "enrollment",
        },
        {
            "label": "Payments",
            "count": Payment.objects.count(),
            "description": "Recorded payment entries",
            "icon": "credit-card-2-front-fill",
            "tone": "gold",
            "url": "payment",
        },
        {
            "label": "Lessons",
            "count": Lesson.objects.count(),
            "description": "Lessons across all courses",
            "icon": "journal-bookmark-fill",
            "tone": "navy",
            "url": "lesson",
        },
        {
            "label": "Lesson Tracker",
            "count": LessonTracker.objects.count(),
            "description": "Recorded lesson progress",
            "icon": "clipboard2-check-fill",
            "tone": "green",
            "url": "lesson_tracker",
        },
    ]
    if not request.user.is_staff:
        instructor_record = Instructor.objects.filter(email__iexact=request.user.email).first()
        if instructor_record:
            taught_courses = Course.objects.filter(Instructor_id=instructor_record)
            instructor_courses = list(taught_courses.order_by("course_name"))
            for course_record in instructor_courses:
                course_record.course_cover = _course_cover(course_record)
                course_record.student_count = Enrollment.objects.filter(
                    Course_id=course_record, status__in=("Pending", "Active", "Completed")
                ).values("Student_id").distinct().count()
                course_record.lesson_count = Lesson.objects.filter(Course_id=course_record).count()
            summary_cards = [
                {
                    "label": "Courses Taught",
                    "count": taught_courses.count(),
                    "description": "Your assigned courses",
                    "icon": "book-half",
                    "tone": "navy",
                    "url": "course",
                },
                {
                    "label": "Lessons",
                    "count": Lesson.objects.filter(Course_id__in=taught_courses).count(),
                    "description": "Lessons in your courses",
                    "icon": "journal-bookmark-fill",
                    "tone": "green",
                    "url": "lesson",
                },
            ]
        else:
            summary_cards = []
        return render(request, "lms/home.html", {
            "summary_cards": summary_cards,
            "dashboard_role": "instructor" if instructor_record else "account",
            "display_name": display_name,
            "instructor_courses": instructor_courses if instructor_record else [],
        })
    return render(request, "lms/home.html", {
        "summary_cards": summary_cards,
        "dashboard_role": "admin" if request.user.is_staff else "account",
        "display_name": display_name,
    })


def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        role = form.cleaned_data["role"]
        user.is_active = role == "student"
        user.save()
        if role == "student":
            Student.objects.update_or_create(
                email=user.email,
                defaults={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "birth_year": form.cleaned_data["birth_year"],
                    "gender": form.cleaned_data["gender"],
                    "contact": form.cleaned_data["contact"],
                },
            )
            auth_login(request, user)
            messages.success(request, "Your student account was created successfully.")
            return redirect("dashboard")
        messages.success(request, "Instructor account created. An administrator must approve it before you can log in.")
        return redirect("login")
    return render(request, "registrations/signup.html", {"form": form})


@login_required_message
def student(request):
    username_by_email = {
        email.casefold(): username
        for email, username in get_user_model().objects.exclude(email="").values_list("email", "username")
    }
    if not request.user.is_staff:
        own_student = _student_for_user(request.user)
        if own_student:
            own_student.account_username = username_by_email.get(own_student.email.casefold(), "No linked login")
            return render(request, "lms/student.html", {"students": [own_student]})
        own_instructor = _instructor_for_user(request.user)
        if own_instructor:
            own_instructor.account_username = username_by_email.get(own_instructor.email.casefold(), "No linked login")
            return render(request, "lms/student.html", {"is_instructor": True, "instructors": [own_instructor]})
        return render(request, "lms/student.html", {"students": []})

    students = Student.objects.all().order_by("last_name", "first_name")
    student_rows = list(students)
    for record in student_rows:
        record.account_username = username_by_email.get(record.email.casefold(), "No linked login")
    return render(request, "lms/student.html", {"students": student_rows})


@login_required_message
def instructor(request):
    if not request.user.is_staff:
        messages.error(request, "Lecturer records are only available to administrators.")
        return redirect("dashboard")
    instructors = _latest_five(Instructor.objects.all())
    user_by_email = {
        email.casefold(): (user_id, is_active)
        for user_id, email, is_active in get_user_model().objects.exclude(email="").values_list("id", "email", "is_active")
    }
    for instructor_record in instructors:
        account = user_by_email.get(instructor_record.email.casefold())
        instructor_record.account_status = "No account"
        instructor_record.account_user_id = None
        if account:
            instructor_record.account_user_id = account[0]
            instructor_record.account_status = "Active" if account[1] else "Awaiting approval"
    return render(request, "lms/instructor.html", {"instructors": instructors})


@require_POST
@login_required_message
def approve_instructor_account(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Only an administrator can approve instructor accounts.")
        return redirect("dashboard")
    instructor_record = get_object_or_404(Instructor, pk=pk)
    user = get_user_model().objects.filter(email__iexact=instructor_record.email).first()
    if user is None:
        messages.error(request, "No instructor account has been registered for this email yet.")
    elif user.is_active:
        messages.info(request, "This instructor account is already active.")
    else:
        user.is_active = True
        user.save(update_fields=["is_active"])
        messages.success(request, f"Instructor account for {instructor_record.email} approved.")
    return redirect("instructor")


@login_required_message
def course(request):
    student_record = _student_for_user(request.user)
    return render(request, "lms/course.html", {
        "courses": _latest_five(Course.objects.select_related("Instructor_id")),
        "current_student": student_record,
    })


def _student_for_user(user):
    if not user.is_authenticated or not user.email:
        return None
    return Student.objects.filter(email__iexact=user.email).first()


def _instructor_for_user(user):
    if not user.is_authenticated or not user.email:
        return None
    return Instructor.objects.filter(email__iexact=user.email).first()


def _refresh_enrollment_progress(enrollment_record):
    total = Lesson.objects.filter(Course_id=enrollment_record.Course_id).count()
    completed = LessonTracker.objects.filter(
        Enrollment_id=enrollment_record,
        Lesson_id__Course_id=enrollment_record.Course_id,
        status="Completed",
    ).count()
    progress = min(100, int(round((completed / total) * 100))) if total else 0
    has_verified_payment = enrollment_record.payment_set.filter(status="completed").exists()
    if has_verified_payment:
        status = "Completed" if total and completed == total else "Active"
    elif enrollment_record.status == "Completed":
        status = "Pending"
    else:
        status = enrollment_record.status
    if enrollment_record.progress != progress or enrollment_record.status != status:
        enrollment_record.progress = progress
        enrollment_record.status = status
        enrollment_record.save(update_fields=["progress", "status"])


@require_POST
@login_required_message
def enroll_in_course(request, pk):
    student_record = _student_for_user(request.user)
    if student_record is None:
        messages.error(request, "Your account needs a student profile before you can enroll.")
        return redirect("course")
    course_record = get_object_or_404(Course, pk=pk)
    enrollment_record, created = Enrollment.objects.get_or_create(
        Student_id=student_record,
        Course_id=course_record,
        defaults={"status": "Pending", "progress": 0},
    )
    if enrollment_record.status == "Active" or enrollment_record.status == "Completed":
        messages.info(request, "You are already enrolled in this course.")
        return redirect("lesson")
    messages.success(request, "Enrollment created with Pending status. Complete payment to unlock lessons.")
    return redirect("pay_enrollment", pk=enrollment_record.pk)


@login_required_message
def pay_enrollment(request, pk):
    student_record = _student_for_user(request.user)
    enrollment_record = get_object_or_404(Enrollment.objects.select_related("Course_id"), pk=pk)
    if student_record is None or enrollment_record.Student_id_id != student_record.pk:
        messages.error(request, "You can only pay for your own enrollment.")
        return redirect("course")
    form = PaymentSubmissionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        Payment.objects.create(
            Enrollment_id=enrollment_record,
            Payment_date=timezone.localdate(),
            Amount=enrollment_record.Course_id.Amount,
            payment_method=form.cleaned_data["payment_method"],
            status="pending",
        )
        messages.success(request, "Payment submitted. Lessons unlock after an administrator verifies it.")
        return redirect("payment")
    return render(request, "lms/payment_checkout.html", {"form": form, "enrollment": enrollment_record})


@login_required_message
def enrollment(request):
    enrollments = Enrollment.objects.select_related("Student_id", "Course_id")
    student_record = _student_for_user(request.user)
    instructor_record = _instructor_for_user(request.user)
    is_instructor = bool(instructor_record and not request.user.is_staff)
    if not request.user.is_staff and student_record:
        enrollments = enrollments.filter(Student_id=student_record)
    elif is_instructor:
        enrollments = enrollments.filter(Course_id__Instructor_id=instructor_record)
    elif not request.user.is_staff:
        enrollments = enrollments.none()
    return render(
        request,
        "lms/enrollment.html",
        {"enrollments": _latest_five(enrollments), "is_instructor": is_instructor},
    )


@login_required_message
def payment(request):
    if not request.user.is_staff and _instructor_for_user(request.user):
        messages.error(request, "Payment records are available to students and administrators.")
        return redirect("dashboard")
    payments = Payment.objects.select_related("Enrollment_id__Student_id", "Enrollment_id__Course_id")
    student_record = _student_for_user(request.user)
    if not request.user.is_staff and student_record:
        payments = payments.filter(Enrollment_id__Student_id=student_record)
    elif not request.user.is_staff:
        payments = payments.none()
    return render(
        request,
        "lms/payment.html",
        {
            "payments": _latest_five(
                payments
            )
        },
    )


@login_required_message
def lesson(request):
    student_record = _student_for_user(request.user)
    instructor_record = _instructor_for_user(request.user)
    lesson_rows = []
    if student_record and not request.user.is_staff:
        student_enrollments = Enrollment.objects.filter(
            Student_id=student_record,
            status__in=("Active", "Completed"),
        ).select_related("Course_id")
        for enrollment_record in student_enrollments:
            _refresh_enrollment_progress(enrollment_record)
            if enrollment_record.status != "Active":
                continue
            for lesson_record in Lesson.objects.filter(Course_id=enrollment_record.Course_id).prefetch_related("resources"):
                tracker = LessonTracker.objects.filter(Enrollment_id=enrollment_record, Lesson_id=lesson_record).first()
                lesson_rows.append((lesson_record, enrollment_record, tracker, lesson_record.resources.all()))
        lessons = []
    elif instructor_record and not request.user.is_staff:
        lessons = _latest_five(Lesson.objects.filter(Course_id__Instructor_id=instructor_record).select_related("Course_id").prefetch_related("resources"))
    else:
        lessons = _latest_five(Lesson.objects.select_related("Course_id").prefetch_related("resources")) if request.user.is_staff else []
    return render(request, "lms/lesson.html", {
        "lessons": lessons, "lesson_rows": lesson_rows,
        "is_student": student_record is not None and not request.user.is_staff,
        "is_instructor": instructor_record is not None and not request.user.is_staff,
    })


@login_required_message
def open_lesson_resource(request, pk):
    student_record = _student_for_user(request.user)
    instructor_record = _instructor_for_user(request.user)
    resource = get_object_or_404(LessonResource.objects.select_related("Lesson_id__Course_id"), pk=pk)
    if request.user.is_staff or (instructor_record and resource.Lesson_id.Course_id.Instructor_id_id == instructor_record.pk):
        return redirect(resource.url)
    if student_record is None:
        messages.error(request, "This resource is only available to enrolled students and the course instructor.")
        return redirect("lesson")
    enrollment_record = get_object_or_404(
        Enrollment,
        Student_id=student_record,
        Course_id=resource.Lesson_id.Course_id,
        status__in=("Active", "Completed"),
    )
    _refresh_enrollment_progress(enrollment_record)
    if enrollment_record.status != "Active":
        messages.info(request, "You have completed this course and no new lessons are available.")
        return redirect("lesson")
    LessonTracker.objects.update_or_create(
        Enrollment_id=enrollment_record,
        Lesson_id=resource.Lesson_id,
        defaults={"status": "Completed"},
    )
    _refresh_enrollment_progress(enrollment_record)
    messages.success(request, "Lesson opened and your progress was recorded.")
    return redirect(resource.url)


@login_required_message
def lesson_resources(request):
    instructor_record = _instructor_for_user(request.user)
    if not request.user.is_staff and instructor_record is None:
        messages.error(request, "Only instructors and administrators can manage lesson resources.")
        return redirect("lesson")
    eligible_lessons = Lesson.objects.select_related("Course_id")
    if not request.user.is_staff:
        eligible_lessons = eligible_lessons.filter(Course_id__Instructor_id=instructor_record)
    form = LessonResourceForm(request.POST or None)
    form.fields["Lesson_id"].queryset = eligible_lessons
    resources = LessonResource.objects.select_related("Lesson_id__Course_id")
    if not request.user.is_staff:
        resources = resources.filter(Lesson_id__Course_id__Instructor_id=instructor_record)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Lesson resource added.")
        return redirect("lesson_resources")
    return render(request, "lms/lesson_resources.html", {"form": form, "resources": resources})


@login_required_message
def lesson_tracker(request):
    trackers = LessonTracker.objects.select_related(
        "Enrollment_id", "Lesson_id", "Enrollment_id__Student_id", "Enrollment_id__Course_id"
    )
    student_record = _student_for_user(request.user)
    instructor_record = _instructor_for_user(request.user)
    if not request.user.is_staff:
        if student_record:
            trackers = trackers.filter(Enrollment_id__Student_id=student_record)
        elif instructor_record:
            trackers = trackers.filter(Enrollment_id__Course_id__Instructor_id=instructor_record)
        else:
            trackers = trackers.none()
    return render(
        request,
        "lms/lesson_tracker.html",
        {
            "trackers": _latest_five(trackers),
            "can_manage_trackers": request.user.is_staff,
            "is_instructor": bool(instructor_record and not request.user.is_staff),
        },
    )


def _add_model(request, form_class, template_name, page_title, return_url, success_message):
    if not request.user.is_staff:
        messages.error(request, "Only staff can manage records directly.")
        return redirect("dashboard")
    form = form_class(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect(return_url)

    return render(
        request,
        template_name,
        {"form": form, "page_title": page_title, "return_url": return_url, "submit_label": "Save"},
    )


def _edit_model(request, model, form_class, template_name, page_title, return_url, success_message, pk):
    if not request.user.is_staff:
        messages.error(request, "Only staff can manage records directly.")
        return redirect("dashboard")
    instance = get_object_or_404(model, pk=pk)
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect(return_url)

    return render(
        request,
        template_name,
        {"form": form, "page_title": page_title, "return_url": return_url, "submit_label": "Save changes"},
    )


def _delete_model(request, model, return_url, success_message, pk):
    if not request.user.is_staff:
        messages.error(request, "Only staff can manage records directly.")
        return redirect("dashboard")
    instance = get_object_or_404(model, pk=pk)
    instance.delete()
    messages.success(request, success_message)
    return redirect(return_url)


@login_required_message
def add_student(request):
    return _add_model(request, StudentForm, "lms/add_student.html", "Add student", "student", "Student added.")


@login_required_message
def add_instructor(request):
    return _add_model(
        request, InstructorForm, "lms/add_instructor.html", "Add instructor", "instructor", "Instructor added."
    )


@login_required_message
def add_course(request):
    return _add_model(request, CourseForm, "lms/add_course.html", "Add course", "course", "Course added.")


@login_required_message
def add_enrollment(request):
    return _add_model(
        request, EnrollmentForm, "lms/add_enrollment.html", "Add enrollment", "enrollment", "Enrollment added."
    )


@login_required_message
def add_payment(request):
    return _add_model(request, PaymentForm, "lms/add_payment.html", "Add payment", "payment", "Payment added.")


@login_required_message
def add_lesson(request):
    return _add_model(request, LessonForm, "lms/add_lesson.html", "Add lesson", "lesson", "Lesson added.")


@login_required_message
def add_lesson_tracker(request):
    return _add_model(
        request,
        LessonTrackerForm,
        "lms/add_lesson_tracker.html",
        "Add lesson tracker",
        "lesson_tracker",
        "Lesson tracker added.",
    )


@login_required_message
def edit_student(request, pk):
    return _edit_model(request, Student, StudentForm, "lms/add_student.html", "Edit student", "student", "Student updated.", pk)


@require_POST
@login_required_message
def delete_student(request, pk):
    return _delete_model(request, Student, "student", "Student deleted.", pk)


@login_required_message
def edit_instructor(request, pk):
    return _edit_model(request, Instructor, InstructorForm, "lms/add_instructor.html", "Edit instructor", "instructor", "Instructor updated.", pk)


@require_POST
@login_required_message
def delete_instructor(request, pk):
    return _delete_model(request, Instructor, "instructor", "Instructor deleted.", pk)


@login_required_message
def edit_course(request, pk):
    return _edit_model(request, Course, CourseForm, "lms/add_course.html", "Edit course", "course", "Course updated.", pk)


@require_POST
@login_required_message
def delete_course(request, pk):
    return _delete_model(request, Course, "course", "Course deleted.", pk)


@login_required_message
def edit_enrollment(request, pk):
    return _edit_model(request, Enrollment, EnrollmentForm, "lms/add_enrollment.html", "Edit enrollment", "enrollment", "Enrollment updated.", pk)


@require_POST
@login_required_message
def delete_enrollment(request, pk):
    return _delete_model(request, Enrollment, "enrollment", "Enrollment deleted.", pk)


@login_required_message
def edit_payment(request, pk):
    if not request.user.is_staff:
        messages.error(request, "Only an administrator can verify payments.")
        return redirect("payment")
    return _edit_model(request, Payment, PaymentReviewForm, "lms/add_payment.html", "Verify payment", "payment", "Payment updated.", pk)


@require_POST
@login_required_message
def delete_payment(request, pk):
    return _delete_model(request, Payment, "payment", "Payment deleted.", pk)


@login_required_message
def edit_lesson(request, pk):
    return _edit_model(request, Lesson, LessonForm, "lms/add_lesson.html", "Edit lesson", "lesson", "Lesson updated.", pk)


@require_POST
@login_required_message
def delete_lesson(request, pk):
    return _delete_model(request, Lesson, "lesson", "Lesson deleted.", pk)


@login_required_message
def edit_lesson_tracker(request, pk):
    return _edit_model(
        request,
        LessonTracker,
        LessonTrackerForm,
        "lms/add_lesson_tracker.html",
        "Edit lesson tracker",
        "lesson_tracker",
        "Lesson tracker updated.",
        pk,
    )


@require_POST
@login_required_message
def delete_lesson_tracker(request, pk):
    return _delete_model(request, LessonTracker, "lesson_tracker", "Lesson tracker deleted.", pk)

