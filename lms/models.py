from django.db import models

# Create your models here.
class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_year = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Instructor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    contact = models.CharField(max_length=15)
    qualification = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Course(models.Model):
    Instructor_id = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name='courses',
    )
    course_name = models.CharField(max_length=100)
    Category = models.TextField()
    Status = models.CharField(max_length=20)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.course_name

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    Student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    Course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    Enrollment_date = models.DateField(auto_now_add=True)
    progress = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    def __str__(self):
        return f"{self.Student_id} enrolled in {self.Course_id}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('incomplete', 'Incomplete'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('Card', 'Card'),
        ('Mobile Money', 'Mobile Money'),
        ('Bank Transfer', 'Bank Transfer'),
    ]
    Enrollment_id = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    Payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    Amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        enrollment = self.Enrollment_id
        if enrollment.status == 'Completed':
            return
        if self.status == 'completed':
            target_status = 'Active'
        elif not enrollment.payment_set.filter(status='completed').exists():
            target_status = 'Pending'
        else:
            return
        if enrollment.status != target_status:
            enrollment.status = target_status
            enrollment.save(update_fields=['status'])

    def __str__(self):
        return f"Payment of {self.Amount} for {self.Enrollment_id}"

class Lesson(models.Model):
    Course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    Lesson_title = models.CharField(max_length=100)
    content = models.TextField(blank=True)

    def __str__(self):
        return self.Lesson_title


class LessonResource(models.Model):
    Lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=150)
    url = models.URLField(max_length=500)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} — {self.Lesson_id}"
    
class LessonTracker(models.Model):
    STATUS_CHOICES = [
        ('Incomplete', 'Incomplete'),
        ('Completed', 'Completed'),
    ]
    Enrollment_id = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    Lesson_id = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Incomplete')

    class Meta:
        constraints = [models.UniqueConstraint(fields=('Enrollment_id', 'Lesson_id'), name='unique_enrollment_lesson_tracker')]

    def __str__(self):
        return f"{self.Enrollment_id} - {self.Lesson_id} - {self.status}"



    

