from django.contrib import admin

from .forms import CourseForm, InstructorForm, PaymentReviewForm
from .models import Course, Enrollment, Instructor, Lesson, LessonResource, LessonTracker, Payment, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "birth_year", "gender", "contact")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("gender",)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    form = InstructorForm
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "gender",
        "contact",
        "qualification",
        "salary_ugx",
    )
    search_fields = ("first_name", "last_name", "email", "qualification")
    list_filter = ("gender",)

    @admin.display(description="Salary (UGX)", ordering="salary")
    def salary_ugx(self, obj):
        return f"UGX {obj.salary:,.2f}"


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseForm
    list_display = ("id", "course_name", "Instructor_id", "Category", "Status", "amount_ugx")
    search_fields = ("course_name", "Category")
    list_filter = ("Status",)

    @admin.display(description="Amount (UGX)", ordering="Amount")
    def amount_ugx(self, obj):
        return f"UGX {obj.Amount:,.2f}"


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id", "Student_id", "Course_id", "progress", "status")
    search_fields = ("Student_id__first_name", "Student_id__last_name", "Course_id__course_name")
    list_filter = ("status",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    form = PaymentReviewForm
    list_display = ("id", "Enrollment_id", "amount_ugx", "payment_method", "Payment_date", "status")
    search_fields = (
        "Enrollment_id__Student_id__first_name",
        "Enrollment_id__Student_id__last_name",
        "Enrollment_id__Course_id__course_name",
    )
    list_filter = ("payment_method", "status", "Payment_date")

    @admin.display(description="Amount (UGX)", ordering="Amount")
    def amount_ugx(self, obj):
        return f"UGX {obj.Amount:,.2f}"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id", "Course_id", "Lesson_title")
    search_fields = ("Lesson_title", "Course_id__course_name")


@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ("id", "Lesson_id", "title", "url", "added_at")
    search_fields = ("title", "Lesson_id__Lesson_title", "Lesson_id__Course_id__course_name")


@admin.register(LessonTracker)
class LessonTrackerAdmin(admin.ModelAdmin):
    list_display = ("id", "Enrollment_id", "Lesson_id", "status")
    list_filter = ("status",)
