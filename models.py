from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('USER', 'User'),
        ('CONTRACTOR', 'Contractor'),
        ('WORKER', 'Worker'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='worker_profile')
    skill = models.CharField(max_length=100)
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2)
    contractor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='workers', limit_choices_to={'role': 'CONTRACTOR'})
    availability_status = models.BooleanField(default=True)

    def __str__(self):
        return f"Worker: {self.user.username}"

class ContractorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='contractor_profile')
    company_name = models.CharField(max_length=200, blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    is_approved = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    experience_years = models.IntegerField(default=0)

    def __str__(self):
        return f"Contractor: {self.user.username}"

class MaterialRate(models.Model):
    """Admin managed global rates for materials"""
    name = models.CharField(max_length=100, unique=True) # e.g. Cement, Steel
    unit = models.CharField(max_length=20) # e.g. Bag, Kg
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name}: {self.current_price}/{self.unit}"

class Project(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DELAYED', 'Delayed'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_projects', limit_choices_to={'role': 'USER'})
    contractor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='contractor_projects', limit_choices_to={'role': 'CONTRACTOR'})
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.title

class BuildingDetails(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='building_details')
    bedroom_count = models.IntegerField(default=1)
    hall_size_sqft = models.IntegerField(default=100)
    kitchen_size_sqft = models.IntegerField(default=80)
    total_area_sqft = models.IntegerField(default=1000, help_text="Total build-up area in square feet")
    floors = models.IntegerField(default=1)
    plot_image = models.ImageField(upload_to='plots/', blank=True, null=True)
    selected_design = models.ForeignKey('HouseDesign', on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
    requirements = models.TextField(blank=True, help_text="Specific requirements for materials, design, etc.")

    def __str__(self):
        return f"Details for {self.project.title}"

class CostEstimation(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='cost_estimation')
    estimated_total_cost = models.DecimalField(max_digits=15, decimal_places=2)
    breakdown_json = models.JSONField(default=dict, help_text="JSON structure of cost breakdown")
    ai_model_used = models.CharField(max_length=50, default="Standard Regression")
    confidence_score = models.IntegerField(default=85)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cost Est: {self.estimated_total_cost} for {self.project.title}"

class ProjectProgress(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='progress_updates')
    percentage = models.IntegerField(default=0)
    description = models.TextField()
    image = models.ImageField(upload_to='progress/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Material(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='materials')
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=20, default='units') # kg, bags, etc.
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.cost_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

class Task(models.Model):
    STATUS_CHOICES = (
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', limit_choices_to={'role': 'WORKER'})
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ASSIGNED')
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

class Attendance(models.Model):
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='attendance_records') # Which project were they working on?
    date = models.DateField()
    is_present = models.BooleanField(default=True)
    wage_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('worker', 'date', 'project')

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} -> {self.recipient.username}"

class CostEstimationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='estimation_logs')
    image = models.ImageField(upload_to='ai_estimates/')
    material_type = models.CharField(max_length=100, default="General Construction")
    square_footage = models.IntegerField(default=1000)
    floors = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    # Mock result storage
    estimated_cost_display = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Est Request by {self.user.username} at {self.created_at}"

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    CATEGORY_CHOICES = (
        ('Bedroom', 'Bedroom'),
        ('Kitchen', 'Kitchen'),
        ('Bathroom', 'Bathroom'),
        ('Toilet', 'Toilet'),
        ('Visiting Room', 'Visiting Room'),
        ('Living Room', 'Living Room'),
        ('Interior Paint', 'Interior Paint'),
        ('Exterior Paint', 'Exterior Paint'),
    )
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ProductRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ORDERED', 'Ordered'),
        ('REJECTED', 'Rejected'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='requests')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_requests')
    contractor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_requests')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='product_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} requested by {self.client.username}"


class Design(models.Model):
    """Designs uploaded by contractors with an optional price and link to a project or product."""
    contractor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='designs', limit_choices_to={'role': 'CONTRACTOR'})
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='designs')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='design_proposals')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    design_file = models.FileField(upload_to='designs/', blank=True, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.contractor.username}"

class HouseDesign(models.Model):
    """Admin Curated Designs for Users to Select"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    square_feet = models.IntegerField()
    image = models.ImageField(upload_to='house_designs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.square_feet} sqft)"
