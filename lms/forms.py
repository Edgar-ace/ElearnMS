from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Course, Enrollment, Instructor, Lesson, LessonResource, LessonTracker, Payment, Student


class BootstrapModelForm(forms.ModelForm):
    """Apply the shared Bootstrap field classes to model forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = css_class


class StudentForm(BootstrapModelForm):
    class Meta:
        model = Student
        fields = ("first_name", "last_name", "email", "birth_year", "gender", "contact")
        widgets = {"birth_year": forms.DateInput(attrs={"type": "date"})}


class InstructorForm(BootstrapModelForm):
    class Meta:
        model = Instructor
        fields = (
            "first_name",
            "last_name",
            "email",
            "gender",
            "contact",
            "qualification",
            "salary",
        )
        labels = {"salary": "Salary (UGX)"}


class CourseForm(BootstrapModelForm):
    class Meta:
        model = Course
        fields = ("Instructor_id", "course_name", "Category", "Status", "Amount")
        labels = {"Instructor_id": "Instructor", "Amount": "Amount (UGX)"}


class EnrollmentForm(BootstrapModelForm):
    class Meta:
        model = Enrollment
        fields = ("Student_id", "Course_id", "progress", "status")


class PaymentForm(BootstrapModelForm):
    class Meta:
        model = Payment
        fields = ("Enrollment_id", "Amount", "payment_method")
        labels = {"Amount": "Amount (UGX)"}


class PaymentReviewForm(PaymentForm):
    class Meta(PaymentForm.Meta):
        fields = ("Enrollment_id", "Amount", "payment_method", "status")


class PaymentSubmissionForm(forms.Form):
    payment_method = forms.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["payment_method"].widget.attrs["class"] = "form-select"


class LessonForm(BootstrapModelForm):
    class Meta:
        model = Lesson
        fields = ("Course_id", "Lesson_title")
        labels = {"Course_id": "Course"}


class LessonResourceForm(BootstrapModelForm):
    class Meta:
        model = LessonResource
        fields = ("Lesson_id", "title", "url")
        labels = {"Lesson_id": "Lesson"}


class LessonTrackerForm(BootstrapModelForm):
    class Meta:
        model = LessonTracker
        fields = ("Enrollment_id", "Lesson_id", "status")


class LoginForm(AuthenticationForm):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("instructor", "Instructor"),
        ("admin", "Administrator"),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Sign in as")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].widget.attrs.update({"class": "form-control"})
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your username", "autocomplete": "username"}
        )
        self.fields["password"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your password", "autocomplete": "current-password"}
        )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        user = getattr(self, "user_cache", None)
        if not user or not role:
            return cleaned_data

        if role == "admin" and user.is_staff:
            return cleaned_data
        if role == "student" and not user.is_staff and user.email and Student.objects.filter(email__iexact=user.email).exists():
            return cleaned_data
        if role == "instructor" and not user.is_staff and user.email and Instructor.objects.filter(email__iexact=user.email).exists():
            return cleaned_data

        raise forms.ValidationError("These credentials are not registered for the selected account type.")

    def confirm_login_allowed(self, user):
        if not user.is_active and user.email and Instructor.objects.filter(email__iexact=user.email).exists():
            raise forms.ValidationError("Your instructor account is awaiting administrator approval.")
        super().confirm_login_allowed(user)


class SignupForm(UserCreationForm):
    role = forms.ChoiceField(choices=(("student", "Student"), ("instructor", "Instructor")), label="Account type")
    email = forms.EmailField(widget=forms.EmailInput(attrs={"autocomplete": "email"}))
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "given-name"}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"autocomplete": "family-name"}))
    birth_year = forms.DateField(label="Date of birth", widget=forms.DateInput(attrs={"type": "date"}), required=False)
    gender = forms.ChoiceField(choices=Student.GENDER_CHOICES, required=False)
    contact = forms.CharField(max_length=15, required=False)

    class Meta:
        model = get_user_model()
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        email = cleaned_data.get("email")
        if email and get_user_model().objects.filter(email__iexact=email).exists():
            self.add_error("email", "An account already uses this email address.")
        if role == "student":
            for field_name in ("birth_year", "gender", "contact"):
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, "This field is required for student accounts.")
        elif role == "instructor":
            if email and not Instructor.objects.filter(email__iexact=email).exists():
                self.add_error("email", "Use the email on your instructor record. Ask an administrator to add your instructor details first.")
        return cleaned_data
