from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProjectForm, BuildingDetailsForm, TaskForm, ProgressForm, MaterialForm, CostEstimationLogForm, MaterialRateForm, BudgetEstimationForm, ProductForm, DesignForm, HouseDesignForm
from .models import User, Project, BuildingDetails, Task, CostEstimation, ProjectProgress, Material, CostEstimationLog, MaterialRate, ContractorProfile, Product, ProductRequest, Design, HouseDesign, Attendance
from .decorators import role_required
import random

# ... [Previous Views] ...

@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.user != task.assigned_to:
        return redirect('dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['IN_PROGRESS', 'COMPLETED']:
            task.status = new_status
            if new_status == 'COMPLETED':
                from django.utils import timezone
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, f'Task status updated to {task.get_status_display()}')
            
    return redirect('dashboard')

@login_required
@role_required(['ADMIN'])
def update_material_rates(request):
        
    rates = MaterialRate.objects.all()
    if request.method == 'POST':
        form = MaterialRateForm(request.POST)
        if form.is_valid():
            rate, created = MaterialRate.objects.get_or_create(
                name=form.cleaned_data['name'],
                defaults={'unit': form.cleaned_data['unit'], 'current_price': form.cleaned_data['current_price']}
            )
            if not created:
                rate.current_price = form.cleaned_data['current_price']
                rate.save()
            messages.success(request, 'Material Rate Updated')
            return redirect('update_material_rates')
    else:
        form = MaterialRateForm()
    
    return render(request, 'core/update_material_rates.html', {'rates': rates, 'form': form})

@login_required
@role_required(['ADMIN'])
def user_list(request):
    users = User.objects.exclude(role='ADMIN').order_by('-date_joined')
    return render(request, 'core/user_list.html', {'users': users})

@login_required
@role_required(['ADMIN'])
def delete_user(request, pk):
    
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user.role == 'ADMIN':
            messages.error(request, "Cannot delete an Admin account.")
        else:
            username = user.username
            user.delete()
            messages.success(request, f"User {username} deleted successfully.")
    
    return redirect('user_list')

@login_required
def budget_estimation(request):
    estimation_result = None
    if request.method == 'POST':
        form = BudgetEstimationForm(request.POST)
        if form.is_valid():
            budget = form.cleaned_data['max_budget']
            area = form.cleaned_data['plot_area']
            quality = form.cleaned_data['preferred_material']
            
            # Simple AI Logic (Mock Rules)
            base_rates = {'Standard': 1200, 'Premium': 1800, 'Luxury': 2500}
            rate_per_sqft = base_rates.get(quality, 1500)
            
            estimated_cost = area * rate_per_sqft
            suggestion = ""
            
            if estimated_cost > budget:
                diff = estimated_cost - budget
                suggestion = f"Warning: Over Budget by ₹{diff}. Consider reducing area by {int(diff/rate_per_sqft)} sqft or choosing a lower quality material."
                status = "Over Budget"
            else:
                saving = budget - estimated_cost
                suggestion = f"Great! You are within budget. You save ₹{saving}. You could upgrade to better flooring."
                status = "Within Budget"
                
            estimation_result = {
                'total_cost': estimated_cost,
                'status': status,
                'suggestion': suggestion,
                'breakdown': {
                    'Cement': estimated_cost * 0.15,
                    'Steel': estimated_cost * 0.12,
                    'Labor': estimated_cost * 0.25,
                    'Finishing': estimated_cost * 0.20
                }
            }
    else:
        form = BudgetEstimationForm()
        
    return render(request, 'core/budget_estimation.html', {'form': form, 'result': estimation_result})

def index(request):
    return render(request, 'core/index.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    if user.role == 'ADMIN':
        return admin_dashboard(request)
    elif user.role == 'USER':
        return user_dashboard(request)
    elif user.role == 'CONTRACTOR':
        return contractor_dashboard(request)
    elif user.role == 'WORKER':
        return worker_dashboard(request)
    return render(request, 'core/dashboard.html')

def admin_dashboard(request):
    projects = Project.objects.all().order_by('-created_at')
    users = User.objects.all()
    
    # Statistics
    total_projects = projects.count()
    completed_projects = projects.filter(status='APPROVED').count() # Using APPROVED as 'Done' for now
    pending_projects = projects.filter(status='PENDING').count()
    in_progress_projects = projects.filter(status='IN_PROGRESS').count()
    
    context = {
        'projects': projects,
        'users': users,
        'stats': {
            'total': total_projects,
            'completed': completed_projects,
            'pending': pending_projects,
            'in_progress': in_progress_projects
        }
    }
    return render(request, 'core/dashboard_admin.html', context)

def user_dashboard(request):
    projects = Project.objects.filter(client=request.user)
    return render(request, 'core/dashboard_user.html', {'projects': projects})

def contractor_dashboard(request):
    # Show projects assigned to this contractor
    projects = Project.objects.filter(contractor=request.user)
    return render(request, 'core/dashboard_contractor.html', {'projects': projects})

def worker_dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'core/dashboard_worker.html', {'tasks': tasks})

@login_required
@role_required(['USER'])
def create_project(request):
        
    if request.method == 'POST':
        p_form = ProjectForm(request.POST) # Now includes 'contractor'
        b_form = BuildingDetailsForm(request.POST, request.FILES)
        if p_form.is_valid() and b_form.is_valid():
            project = p_form.save(commit=False)
            project.client = request.user
            # Contractor is already set from form clean_data
            project.status = 'PENDING' # Request sent to contractor
            project.save()
            
            details = b_form.save(commit=False)
            details.project = project
            
            # Link selected design if present
            design_id = request.POST.get('dt_design_id')
            if design_id:
                from .models import HouseDesign
                try:
                    design_obj = HouseDesign.objects.get(pk=design_id)
                    details.selected_design = design_obj
                except HouseDesign.DoesNotExist:
                    pass
            
            details.save()
            
            # Mock AI Cost Estimation for Project Total
            estimated_cost = details.total_area_sqft * 1500 * details.floors
            
            CostEstimation.objects.create(
                project=project,
                estimated_total_cost=estimated_cost,
                breakdown_json={"material": estimated_cost*0.6, "labor": estimated_cost*0.3, "overhead": estimated_cost*0.1}
            )
            
            messages.success(request, 'Project Request Sent to Contractor Successfully')
            return redirect('dashboard')
    else:
        p_form = ProjectForm()
        initial_requirements = ""
        selected_design_id = request.GET.get('design_id')
        selected_design_title = request.GET.get('design') # Fallback
        
        # Prepare context for the template to include a hidden field
        context_design_id = ""

        if selected_design_id:
            from .models import HouseDesign
            try:
                design_obj = HouseDesign.objects.get(pk=selected_design_id)
                initial_requirements = f"Selected Design: {design_obj.title}. I would like to build this house."
                context_design_id = selected_design_id
            except HouseDesign.DoesNotExist:
                pass
        elif selected_design_title:
             # Fallback for old links
             initial_requirements = f"Selected Design: {selected_design_title}. I would like to build this house."

        b_form = BuildingDetailsForm(initial={'requirements': initial_requirements})
        
    return render(request, 'core/create_project.html', {'p_form': p_form, 'b_form': b_form, 'selected_design_id': context_design_id})

@login_required
def ai_estimation(request):
    estimated_cost = None
    uploaded_image_url = None
    
    if request.method == 'POST':
        form = CostEstimationLogForm(request.POST, request.FILES)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save() # Save first to get the file path

            # Call AI Service
            from .ai_service import analyze_construction_image
            
            try:
                # Get absolute path for the image
                image_path = log.image.path
                result = analyze_construction_image(
                    image_path, 
                    log.material_type, 
                    log.square_footage, 
                    log.floors
                )
                
                if 'error' in result and result['estimated_cost'] == 'N/A':
                     messages.warning(request, f"AI Analysis Skipped: {result['error']}")
                     log.estimated_cost_display = "N/A (API Key Missing)"
                elif 'error' in result:
                     messages.error(request, f"AI Analysis Failed: {result['error']}")
                     log.estimated_cost_display = "Error"
                else:
                    log.estimated_cost_display = result.get('estimated_cost', 'N/A')
                    # We could also save reasoning if we added a field for it
            except Exception as e:
                messages.error(request, f"Processing Error: {str(e)}")
                log.estimated_cost_display = "Error"

            log.save()
            
            uploaded_image_url = log.image.url
            estimated_cost = log.estimated_cost_display
            messages.success(request, "Image processed successfully!")
    else:
        form = CostEstimationLogForm()
    
    recent_logs = CostEstimationLog.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    return render(request, 'core/ai_estimation.html', {
        'form': form,
        'estimated_cost': estimated_cost,
        'uploaded_image_url': uploaded_image_url,
        'recent_logs': recent_logs
    })

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Strict Security Check
    is_admin = request.user.role == 'ADMIN'
    is_client = request.user == project.client
    is_contractor = request.user == project.contractor
    is_assigned_worker = Task.objects.filter(project=project, assigned_to=request.user).exists()
    
    if not (is_admin or is_client or is_contractor or is_assigned_worker):
        messages.error(request, "You do not have permission to view this project.")
        return redirect('dashboard')

    progress_updates = project.progress_updates.all().order_by('-updated_at')
    materials = project.materials.all()
    tasks = project.tasks.all()
    
    if request.method == 'POST':
        if 'add_progress' in request.POST and (request.user == project.contractor or request.user.role == 'ADMIN'):
            prog_form = ProgressForm(request.POST, request.FILES)
            if prog_form.is_valid():
                prog = prog_form.save(commit=False)
                prog.project = project
                prog.updated_by = request.user
                prog.save()
                messages.success(request, 'Progress Updated')
                return redirect('project_detail', pk=pk)
        elif 'add_material' in request.POST and request.user == project.contractor:
            mat_form = MaterialForm(request.POST)
            if mat_form.is_valid():
                mat = mat_form.save(commit=False)
                mat.project = project
                mat.save()
                messages.success(request, 'Material Added')
                return redirect('project_detail', pk=pk)
        elif 'add_task' in request.POST and request.user == project.contractor:
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.project = project
                task.save()
                messages.success(request, 'Task Assigned')
                return redirect('project_detail', pk=pk)

    prog_form = ProgressForm()
    mat_form = MaterialForm()
    task_form = TaskForm()
    # Limit task assignment to workers
    task_form.fields['assigned_to'].queryset = User.objects.filter(role='WORKER')
    
    return render(request, 'core/project_detail.html', {
        'project': project,
        'progress_updates': progress_updates,
        'materials': materials,
        'tasks': tasks,
        'prog_form': prog_form,
        'mat_form': mat_form,
        'task_form': task_form
    })

@login_required
@role_required(['ADMIN', 'CONTRACTOR'])
def approve_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Allow ADMIN to approve immediately
    if request.user.role == 'ADMIN':
        project.status = 'APPROVED'
        project.save()
        messages.success(request, f'Project {project.title} approved by Admin.')
        return redirect('dashboard')
    
    # Allow CONTRACTOR to review and approve
    elif request.user == project.contractor:
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'reject':
                project.status = 'REJECTED'
                project.save()
                messages.warning(request, 'Project Request Rejected')
            else:
                project.status = 'APPROVED'
                project.save()
                messages.success(request, 'Project Request Accepted')
            return redirect('dashboard')
        return render(request, 'core/project_confirm_approval.html', {'project': project})
        
    else:
        # Unauthorized access
        return redirect('dashboard')

@login_required
@role_required(['ADMIN'])
def assign_contractor(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        contractor_id = request.POST.get('contractor')
        contractor = User.objects.get(pk=contractor_id)
        project.contractor = contractor
        project.status = 'IN_PROGRESS'
        project.save()
        messages.success(request, f'Assigned to {contractor.username}')
        return redirect('dashboard')
    
    contractors = User.objects.filter(role='CONTRACTOR')
    return render(request, 'core/assign_contractor.html', {'project': project, 'contractors': contractors})

@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    # Ensure only the assigned worker can update the task
    if request.user != task.assigned_to:
        return redirect('dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['IN_PROGRESS', 'COMPLETED']:
            task.status = new_status
            if new_status == 'COMPLETED':
                from django.utils import timezone
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, f'Task status updated to {task.get_status_display()}')
            
    return redirect('dashboard')

@login_required
def shop(request):
    category = request.GET.get('category')
    if category:
        products = Product.objects.filter(category=category).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')
        
    categories = Product.CATEGORY_CHOICES
    
    return render(request, 'core/shop.html', {
        'products': products,
        'categories': categories,
        'selected_category': category
    })

@login_required
@role_required(['ADMIN'])
def manage_products(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'core/manage_products.html', {'products': products})

@login_required
@role_required(['ADMIN'])
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('manage_products')
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
@role_required(['ADMIN'])
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form, 'title': 'Edit Product'})

@login_required
@role_required(['ADMIN'])
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
    return redirect('manage_products')

@login_required
@role_required(['USER'])
def request_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    # Find all projects for the user that have an assigned contractor
    projects_with_contractors = Project.objects.filter(
        client=request.user, 
        contractor__isnull=False,
        status__in=['APPROVED', 'IN_PROGRESS', 'PENDING']
    )
    
    if not projects_with_contractors.exists():
        # Check if they have ANY projects at all for a custom error message
        has_any_project = Project.objects.filter(client=request.user).exists()
        if has_any_project:
            messages.error(request, "Your project doesn't have an assigned contractor yet. We will notify you once one is assigned.")
        else:
            messages.error(request, "You need an active project to request products.")
        return redirect('shop')

    # If the user has a specific project selected via GET
    selected_project_id = request.GET.get('project_id')
    
    if selected_project_id:
        project = get_object_or_404(projects_with_contractors, pk=selected_project_id)
    elif projects_with_contractors.count() == 1:
        # Auto-select if there's only one
        project = projects_with_contractors.first()
    else:
        # Show selection page if there are multiple projects/contractors
        return render(request, 'core/select_project_request.html', {
            'product': product,
            'projects': projects_with_contractors
        })

    # Create the request
    exists = ProductRequest.objects.filter(product=product, client=request.user, project=project, status='PENDING').exists()
    if exists:
        messages.warning(request, f"A request for {product.name} is already pending for project '{project.title}'.")
    else:
        ProductRequest.objects.create(
            product=product,
            client=request.user,
            contractor=project.contractor,
            project=project
        )
        messages.success(request, f"Request for {product.name} sent to {project.contractor.username} (Project: {project.title}).")
    
    return redirect('shop')

@login_required
@role_required(['CONTRACTOR'])
def contractor_requests(request):
    prod_requests = ProductRequest.objects.filter(contractor=request.user).order_by('-created_at')
    return render(request, 'core/contractor_requests.html', {'prod_requests': prod_requests})

@login_required
@role_required(['CONTRACTOR'])
def update_request_status(request, pk, status):
    prod_request = get_object_or_404(ProductRequest, pk=pk, contractor=request.user)
    if status.upper() in ['ORDERED', 'REJECTED']:
        prod_request.status = status.upper()
        prod_request.save()
        messages.success(request, f"Request status updated to {prod_request.get_status_display()}")
    return redirect('contractor_requests')


@login_required
@role_required(['CONTRACTOR'])
def add_design(request):
    """Allow contractors to upload a design file with optional price and link to project/product."""
    if request.method == 'POST':
        form = DesignForm(request.POST, request.FILES)
        if form.is_valid():
            design = form.save(commit=False)
            design.contractor = request.user
            design.save()
            messages.success(request, 'Design uploaded successfully.')
            return redirect('dashboard')
    else:
        form = DesignForm()
    return render(request, 'core/add_design.html', {'form': form})

@login_required
@role_required(['ADMIN'])
def admin_manage_designs(request):
    designs = HouseDesign.objects.all().order_by('-created_at')
    if request.method == 'POST':
        # Handle Add Design
        form = HouseDesignForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'House Design Added Successfully')
            return redirect('admin_manage_designs')
    else:
        form = HouseDesignForm()
    
    return render(request, 'core/admin_manage_designs.html', {'designs': designs, 'form': form})

@login_required
@role_required(['ADMIN'])
def admin_delete_design(request, pk):
    design = get_object_or_404(HouseDesign, pk=pk)
    if request.method == 'POST':
        design.delete()
        messages.success(request, 'Design Deleted')
    return redirect('admin_manage_designs')

@login_required
def house_design_gallery(request):
    designs = HouseDesign.objects.all().order_by('-created_at')
    return render(request, 'core/house_design_gallery.html', {'designs': designs})


@login_required
@role_required(['CONTRACTOR'])
@login_required
@role_required(['CONTRACTOR'])
def manage_attendance(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Ensure this contractor owns the project
    if project.contractor != request.user:
        messages.error(request, "Access Denied")
        return redirect('dashboard')

    # Get all workers associated with this contractor
    workers = User.objects.filter(role='WORKER', worker_profile__contractor=request.user)
    
    from .models import Attendance
    import datetime

    today = datetime.date.today()
    date_str = request.GET.get('date') or request.POST.get('attendance_date')
    selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else today
    
    if request.method == 'POST':
        count = 0
        for worker in workers:
            wage_key = f"wage_{worker.id}"
            wage = request.POST.get(wage_key)
            
            if wage:
                # Get existing record or create if not exists
                status_key = f"status_{worker.id}"
                is_present = request.POST.get(status_key) == 'on'

                attendance, created = Attendance.objects.get_or_create(
                    worker=worker,
                    project=project,
                    date=selected_date,
                    defaults={
                        'is_present': is_present,
                        'wage_paid': wage
                    }
                )
                
                attendance.wage_paid = wage
                attendance.is_present = is_present
                attendance.save()
                count += 1
            
        messages.success(request, f"Wages updated for {count} workers on {selected_date}")
        return redirect(f"{request.path}?date={selected_date}")

    # Prepare list with attendance status
    workers_data = []
    for worker in workers:
        attendance = Attendance.objects.filter(worker=worker, project=project, date=selected_date).first()
        workers_data.append({
            'worker': worker,
            'attendance': attendance
        })

    return render(request, 'core/manage_attendance.html', {
        'project': project,
        'workers_data': workers_data,
        'today': today.strftime('%Y-%m-%d'),
        'selected_date': selected_date.strftime('%Y-%m-%d')
    })


@login_required
@role_required(['WORKER'])
def worker_attendance(request):
    from .forms import WorkerAttendanceForm
    from .models import Attendance
    import datetime
    
    today = datetime.date.today()
    
    # Check if already marked for today
    existing_records = Attendance.objects.filter(worker=request.user, date=today)
    
    if request.method == 'POST':
        form = WorkerAttendanceForm(request.user, request.POST)
        if form.is_valid():
            project = form.cleaned_data['project']
            
            # Prevent duplicate
            if Attendance.objects.filter(worker=request.user, project=project, date=today).exists():
                messages.warning(request, "You have already marked attendance for this project today.")
            else:
                Attendance.objects.create(
                    worker=request.user,
                    project=project,
                    date=today,
                    is_present=True,
                    wage_paid=0 # To be updated by contractor
                )
                messages.success(request, f"Attendance marked for {project.title}")
            return redirect('worker_attendance')
    else:
        form = WorkerAttendanceForm(request.user)
        
    history = Attendance.objects.filter(worker=request.user).order_by('-date')[:10]
    
    return render(request, 'core/worker_attendance.html', {
        'form': form,
        'today': today,
        'history': history,
        'existing_records': existing_records
    })

@login_required
@role_required('CONTRACTOR')
def attendance_analysis(request, pk):
    project = get_object_or_404(Project, pk=pk)
    # Ensure the contractor owns the project
    if project.contractor != request.user:
        return redirect('dashboard')
    
    workers_stats = Attendance.objects.filter(project=project, is_present=True).values(
        'worker__username', 'worker__worker_profile__skill'
    ).annotate(
        total_days=Count('id'),
        total_wage=Sum('wage_paid')
    ).order_by('-total_days')

    total_project_wage = workers_stats.aggregate(Sum('total_wage'))['total_wage__sum'] or 0

    return render(request, 'core/attendance_analysis.html', {
        'project': project,
        'workers_stats': workers_stats,
        'total_project_wage': total_project_wage
    })

@login_required
def chatbot_api(request):
    """API endpoint for chatbot interactions."""
    if request.method == 'POST':
        import json
        from .ai_service import get_chatbot_response
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'reply': "I didn't catch that. Could you please specify your doubt?"})
                
            reply = get_chatbot_response(user_message)
            return JsonResponse({'reply': reply})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request'}, status=400)

