from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Project, BuildingDetails, Task, ProjectProgress, Material, CostEstimationLog, ContractorProfile, MaterialRate, Product, Design, HouseDesign, Attendance

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Product Description'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Interior, Electrical, Plumbing'}),
        }

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'phone', 'address', 'profile_image')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valid username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full address'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ContractorProfileForm(forms.ModelForm):
    class Meta:
        model = ContractorProfile
        fields = ['company_name', 'license_number', 'experience_years']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'License Number'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class MaterialRateForm(forms.ModelForm):
    class Meta:
        model = MaterialRate
        fields = ['name', 'unit', 'current_price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Cement'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bag'}),
            'current_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class BudgetEstimationForm(forms.Form):
    max_budget = forms.DecimalField(
        label="Maximum Budget (INR)",
        max_digits=12, 
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 50000'})
    )
    plot_area = forms.IntegerField(
        label="Plot Area (sqft)",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1200'})
    )
    preferred_material = forms.ChoiceField(
        choices=[('Standard', 'Standard'), ('Premium', 'Premium'), ('Luxury', 'Luxury')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ProjectForm(forms.ModelForm):
    contractor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='CONTRACTOR'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        empty_label="Select a Contractor"
    )

    class Meta:
        model = Project
        fields = ['title', 'description', 'location', 'deadline', 'contractor']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your project...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Site Location'}),
            'deadline': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class BuildingDetailsForm(forms.ModelForm):
    class Meta:
        model = BuildingDetails
        fields = ['bedroom_count', 'hall_size_sqft', 'kitchen_size_sqft', 'total_area_sqft', 'floors', 'plot_image', 'requirements']
        widgets = {
            'bedroom_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'hall_size_sqft': forms.NumberInput(attrs={'class': 'form-control'}),
            'kitchen_size_sqft': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_area_sqft': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total square feet'}),
            'floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'plot_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any specific requirements?'}),
        }

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'status']
    
    def __init__(self, *args, **kwargs):
        contractor = kwargs.pop('contractor', None)
        super().__init__(*args, **kwargs)
        if contractor:
            pass # Filtering logic if needed

class ProgressForm(forms.ModelForm):
    class Meta:
        model = ProjectProgress
        fields = ['percentage', 'description', 'image']

class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'quantity', 'unit', 'cost_per_unit']

class CostEstimationLogForm(forms.ModelForm):
    class Meta:
        model = CostEstimationLog
        fields = ['image', 'material_type', 'square_footage', 'floors']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'material_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Cement, Interior Design, Full House'}),
            'square_footage': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 1200'}),
            'floors': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2', 'min': 1}),
        }


class DesignForm(forms.ModelForm):
    class Meta:
        model = Design
        fields = ['title', 'description', 'design_file', 'price', 'project', 'product']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Design Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional description...'}),
            'design_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'product': forms.Select(attrs={'class': 'form-control'}),
        }

class HouseDesignForm(forms.ModelForm):
    class Meta:
        model = HouseDesign
        fields = ['title', 'description', 'price', 'square_feet', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Design Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'square_feet': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'is_present', 'wage_paid']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'wage_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class WorkerAttendanceForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select the Project you worked on today"
    )

    def __init__(self, user=None, *args, **kwargs):
        super(WorkerAttendanceForm, self).__init__(*args, **kwargs)
        if user and hasattr(user, 'worker_profile') and user.worker_profile.contractor:
            contractor = user.worker_profile.contractor
            self.fields['project'].queryset = Project.objects.filter(
                contractor=contractor,
                status='IN_PROGRESS'
            )
        else:
            self.fields['project'].queryset = Project.objects.none()
